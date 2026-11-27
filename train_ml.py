import re
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MaxAbsScaler, OneHotEncoder
from sklearn.tree import DecisionTreeClassifier

BASE_DIR = Path(__file__).parent
DATASET_PATH = BASE_DIR / "netflix_titles.csv"
MODEL_OUT_PATH = BASE_DIR / "best_netflix_model.joblib"


def parse_duration_num(val):
    if not isinstance(val, str):
        return 0.0
    match = re.search(r"(\d+)", val)
    return float(match.group(1)) if match else 0.0


def count_comma_items(val):
    if not isinstance(val, str) or not val.strip():
        return 0
    return len([x.strip() for x in val.split(",") if x.strip()])


def run_crisp_dm_pipeline():
    print("=== 1. DATA UNDERSTANDING & EDA ===")
    df = pd.read_csv(DATASET_PATH)
    print(f"Jumlah baris awal: {len(df):,}, jumlah kolom: {df.shape[1]}")
    print("Distribusi target (type):")
    print(df["type"].value_counts(dropna=False))
    print("\nMissing value per kolom:")
    print(df.isnull().sum())

    print("\n=== 2. DATA PREPARATION & FEATURE ENGINEERING ===")
    df_clean = df.dropna(subset=["type", "release_year"]).copy()
    df_clean["type"] = df_clean["type"].astype(str).str.strip()
    df_clean = df_clean[df_clean["type"].isin(["Movie", "TV Show"])].copy()

    df_clean["rating"] = df_clean["rating"].fillna("Unknown").astype(str).str.strip()
    df_clean["country"] = df_clean["country"].fillna("Unknown").astype(str).str.strip()
    df_clean["listed_in"] = df_clean["listed_in"].fillna("").astype(str).str.strip()
    df_clean["title"] = df_clean["title"].fillna("").astype(str).str.strip()
    df_clean["description"] = df_clean["description"].fillna("").astype(str).str.strip()
    df_clean["duration"] = df_clean["duration"].fillna("0").astype(str).str.strip()

    df_clean["release_year_num"] = pd.to_numeric(df_clean["release_year"], errors="coerce").fillna(2015)
    df_clean["duration_num"] = df_clean["duration"].apply(parse_duration_num)
    df_clean["num_countries"] = df_clean["country"].apply(count_comma_items)
    df_clean["num_genres"] = df_clean["listed_in"].apply(count_comma_items)
    df_clean["text_corpus"] = (
        df_clean["title"] + " " + df_clean["listed_in"] + " " + df_clean["description"]
    )

    feature_cols = [
        "release_year_num",
        "duration_num",
        "num_countries",
        "num_genres",
        "rating",
        "text_corpus",
    ]
    X = df_clean[feature_cols]
    # Target biner: TV Show = 1 (kelas positif), Movie = 0
    y = (df_clean["type"] == "TV Show").astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # MaxAbsScaler menjaga nilai tetap non-negatif agar kompatibel dengan MultinomialNB
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", MaxAbsScaler(), ["release_year_num", "duration_num", "num_countries", "num_genres"]),
            ("cat", OneHotEncoder(handle_unknown="ignore"), ["rating"]),
            ("txt", TfidfVectorizer(max_features=300, stop_words="english"), "text_corpus"),
        ]
    )

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    # 3 algoritma dari daftar Bab 5-14 + GridSearchCV
    experiments = [
        (
            "Decision Tree",
            DecisionTreeClassifier(random_state=42),
            {
                "clf__max_depth": [5, 10, None],
                "clf__min_samples_split": [2, 5],
            },
        ),
        (
            "K-Nearest Neighbors (KNN)",
            KNeighborsClassifier(),
            {
                "clf__n_neighbors": [3, 5, 7],
                "clf__weights": ["uniform", "distance"],
            },
        ),
        (
            "Naive Bayes Classifier",
            MultinomialNB(),
            {
                "clf__alpha": [0.1, 0.5, 1.0, 2.0],
            },
        ),
    ]

    print("\n=== 3. MODELING, TUNING (GRIDSEARCHCV + STRATIFIED K-FOLD) & EVALUATION ===")
    best_score = -1.0
    best_name = None
    best_estimator = None
    summary_rows = []

    for name, estimator, param_grid in experiments:
        pipe = Pipeline(
            steps=[
                ("prep", preprocessor),
                ("clf", estimator),
            ]
        )
        grid = GridSearchCV(
            pipe,
            param_grid=param_grid,
            cv=cv,
            scoring="roc_auc",
            n_jobs=-1,
        )
        grid.fit(X_train, y_train)
        model_best = grid.best_estimator_

        y_pred = model_best.predict(X_test)
        y_prob = model_best.predict_proba(X_test)[:, 1]

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        roc_auc = roc_auc_score(y_test, y_prob)
        cm = confusion_matrix(y_test, y_pred)

        summary_rows.append(
            {
                "Model": name,
                "Best Params": grid.best_params_,
                "Accuracy": round(acc, 4),
                "Precision": round(prec, 4),
                "Recall": round(rec, 4),
                "F1-Score": round(f1, 4),
                "ROC-AUC": round(roc_auc, 4),
            }
        )

        print(f"\n[{name}] Best Params: {grid.best_params_} | CV ROC-AUC: {grid.best_score_:.4f}")
        print(f"Test Accuracy : {acc:.4f}")
        print(f"Test Precision: {prec:.4f} | Recall: {rec:.4f} | F1-Score: {f1:.4f} | ROC-AUC: {roc_auc:.4f}")
        print("Confusion Matrix [baris=aktual (0=Movie, 1=TV Show), kolom=prediksi]:")
        print(cm)
        print(classification_report(y_test, y_pred, target_names=["Movie", "TV Show"], zero_division=0))

        if roc_auc > best_score:
            best_score = roc_auc
            best_name = name
            best_estimator = model_best

    print("\n=== RINGKASAN PERBANDINGAN MODEL (TEST SET) ===")
    print(pd.DataFrame(summary_rows).to_string(index=False))

    joblib.dump(
        {
            "model": best_estimator,
            "model_name": best_name,
            "best_roc_auc": best_score,
            "label_map": {0: "Movie", 1: "TV Show"},
            "ratings": sorted(df_clean["rating"].unique().tolist()),
        },
        MODEL_OUT_PATH,
    )
    print(f"\nModel terbaik ({best_name}) disimpan ke: {MODEL_OUT_PATH}")


if __name__ == "__main__":
    run_crisp_dm_pipeline()