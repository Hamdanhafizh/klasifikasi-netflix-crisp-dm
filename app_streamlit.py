from pathlib import Path
import joblib
import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).parent
DATASET_PATH = BASE_DIR / "netflix_titles.csv"
MODEL_PATH = BASE_DIR / "best_netflix_model.joblib"

st.set_page_config(
    page_title="Netflix ML Classifier • CRISP-DM",
    page_icon=":material/movie_filter:",
    layout="wide",
)


def count_comma_items(val):
    if not isinstance(val, str) or not val.strip():
        return 0
    return len([x.strip() for x in val.split(",") if x.strip()])


@st.cache_resource
def load_artifacts():
    artifact = joblib.load(MODEL_PATH)
    df = pd.read_csv(DATASET_PATH)
    return artifact, df


def apply_preset(preset_type, default_rating):
    if preset_type == "movie":
        st.session_state["inp_judul"] = "Echoes of the Horizon"
        st.session_state["inp_genre"] = "Dramas, Thrillers, International Movies"
        st.session_state["inp_negara"] = "United States, United Kingdom"
        st.session_state["inp_tahun"] = 2022
        st.session_state["inp_durasi"] = 118
        st.session_state["inp_sinopsis"] = (
            "A former pilot uncovers a hidden signal over the Pacific while racing against time."
        )
    elif preset_type == "tv":
        st.session_state["inp_judul"] = "Chronicles of Northwood"
        st.session_state["inp_genre"] = "TV Dramas, Mystery TV Shows"
        st.session_state["inp_negara"] = "United States"
        st.session_state["inp_tahun"] = 2021
        st.session_state["inp_durasi"] = 3
        st.session_state["inp_sinopsis"] = (
            "Across multiple seasons, a small-town investigation reveals interconnected family secrets."
        )
    if default_rating in st.session_state.get("ratings_list", []):
        st.session_state["inp_rating"] = default_rating


artifact, df = load_artifacts()
model = artifact["model"]
model_name = artifact["model_name"]
best_roc_auc = artifact.get("best_roc_auc", artifact.get("best_f1", 0.0))
label_map = artifact.get("label_map", {0: "Movie", 1: "TV Show"})
ratings = artifact["ratings"]
st.session_state["ratings_list"] = ratings

# Inisialisasi nilai awal input di session_state
st.session_state.setdefault("inp_judul", "Midnight Chronicles")
st.session_state.setdefault("inp_genre", "Dramas, International Movies, Thrillers")
st.session_state.setdefault("inp_negara", "United States, United Kingdom")
st.session_state.setdefault("inp_tahun", 2021)
st.session_state.setdefault("inp_durasi", 105)
st.session_state.setdefault("inp_rating", "TV-MA" if "TV-MA" in ratings else ratings[0])
st.session_state.setdefault(
    "inp_sinopsis",
    "A detective investigates a series of mysterious disappearances in a quiet coastal town.",
)

st.title(":material/smart_display: Klasifikasi Tayangan Netflix (Movie vs TV Show)")
st.caption("Mini Project Machine Learning End-to-End (CRISP-DM) • Deployment Streamlit")

# Kartu Metrik Ringkasan
m1, m2, m3, m4 = st.columns(4)
m1.metric(":material/database: Total Dataset", f"{len(df):,}", border=True)
m2.metric(":material/model_training: Model Terbaik", model_name, border=True)
m3.metric(":material/monitoring: Skor Evaluasi", f"{best_roc_auc:.4f}", border=True)
m4.metric(":material/tune: Fitur Pipeline", "6 Fitur", border=True)

st.divider()

tab_pred, tab_eda = st.tabs([
    ":material/psychology: Prediksi Interaktif (ML)",
    ":material/analytics: Eksplorasi Dataset (EDA)",
])

with tab_pred:
    st.subheader(":material/auto_awesome: Uji Prediksi Model Machine Learning")
    st.write("Pilih contoh cepat atau isi data tayangan secara manual lalu klik **Prediksi Kategori Tayangan**.")

    p_col1, p_col2, _ = st.columns([1.2, 1.2, 3.6])
    with p_col1:
        st.button(
            ":material/movie: Contoh Movie",
            on_click=apply_preset,
            args=("movie", "PG-13" if "PG-13" in ratings else ratings[0]),
            width="stretch",
        )
    with p_col2:
        st.button(
            ":material/tv: Contoh TV Show",
            on_click=apply_preset,
            args=("tv", "TV-14" if "TV-14" in ratings else ratings[0]),
            width="stretch",
        )

    with st.form("form_prediksi"):
        c1, c2 = st.columns(2)
        with c1:
            judul = st.text_input(":material/title: Judul Tayangan", key="inp_judul")
            genre = st.text_input(":material/category: Genre (pisahkan dengan koma)", key="inp_genre")
            negara = st.text_input(":material/public: Negara Produksi (pisahkan dengan koma)", key="inp_negara")
        with c2:
            tahun = st.number_input(":material/calendar_today: Tahun Rilis", min_value=1920, max_value=2030, key="inp_tahun")
            durasi_angka = st.number_input(
                ":material/schedule: Angka Durasi (menit untuk Movie / season untuk TV Show)",
                min_value=1,
                max_value=500,
                key="inp_durasi",
            )
            rating = st.selectbox(":material/verified_user: Rating Usia", options=ratings, key="inp_rating")

        sinopsis = st.text_area(":material/description: Sinopsis / Deskripsi", key="inp_sinopsis", height=95)
        submit = st.form_submit_button(":material/bolt: Prediksi Kategori Tayangan", type="primary")

    if submit:
        num_countries = count_comma_items(negara)
        num_genres = count_comma_items(genre)
        text_corpus = f"{judul} {genre} {sinopsis}".strip()

        input_df = pd.DataFrame(
            [
                {
                    "release_year_num": float(tahun),
                    "duration_num": float(durasi_angka),
                    "num_countries": num_countries,
                    "num_genres": num_genres,
                    "rating": rating,
                    "text_corpus": text_corpus,
                }
            ]
        )

        raw_pred = model.predict(input_df)[0]
        pred_label = (
            label_map.get(int(raw_pred), str(raw_pred))
            if str(raw_pred).isdigit()
            else str(raw_pred)
        )
        proba = model.predict_proba(input_df)[0]
        prob_movie = float(proba[0]) * 100.0
        prob_tv = float(proba[1]) * 100.0

        st.success(f"Hasil Prediksi: **{pred_label}**")

        r1, r2 = st.columns(2)
        with r1:
            st.metric(":material/movie: Probabilitas Movie", f"{prob_movie:.2f}%", border=True)
            st.progress(min(max(prob_movie / 100.0, 0.0), 1.0))
        with r2:
            st.metric(":material/tv: Probabilitas TV Show", f"{prob_tv:.2f}%", border=True)
            st.progress(min(max(prob_tv / 100.0, 0.0), 1.0))

        with st.expander(":material/engineering: Lihat Fitur Hasil Feature Engineering"):
            st.dataframe(
                pd.DataFrame(
                    [
                        {
                            "release_year_num": int(tahun),
                            "duration_num": float(durasi_angka),
                            "num_countries": num_countries,
                            "num_genres": num_genres,
                            "rating": rating,
                            "panjang_teks_korpus": len(text_corpus),
                        }
                    ]
                ),
                width="stretch",
                hide_index=True,
            )

with tab_eda:
    st.subheader(":material/query_stats: Eksplorasi Dataset Netflix (EDA)")

    df_eda = df.copy()
    df_eda["release_year_num"] = pd.to_numeric(df_eda["release_year"], errors="coerce")
    valid_years = df_eda["release_year_num"].dropna()
    min_yr = int(valid_years.min()) if not valid_years.empty else 1925
    max_yr = int(valid_years.max()) if not valid_years.empty else 2025

    f1, f2 = st.columns([1, 2])
    with f1:
        tipe_pilihan = st.selectbox(":material/filter_alt: Filter Tipe Tayangan", ["Semua", "Movie", "TV Show"])
    with f2:
        rentang_tahun = st.slider(
            ":material/date_range: Rentang Tahun Rilis",
            min_value=min_yr,
            max_value=max_yr,
            value=(max(min_yr, 2015), max_yr),
        )

    df_filtered = df_eda[
        (df_eda["release_year_num"] >= rentang_tahun[0])
        & (df_eda["release_year_num"] <= rentang_tahun[1])
    ]
    if tipe_pilihan != "Semua":
        df_filtered = df_filtered[df_filtered["type"] == tipe_pilihan]

    st.caption(f"Menampilkan **{len(df_filtered):,}** data sesuai filter aktif.")

    c_left, c_right = st.columns(2)
    with c_left:
        st.markdown("#### :material/pie_chart: Distribusi Tipe Tayangan")
        st.bar_chart(df_filtered["type"].value_counts(), height=260)
    with c_right:
        st.markdown("#### :material/flag: Top 10 Negara Produksi")
        top_countries = (
            df_filtered["country"]
            .dropna()
            .apply(lambda x: x.split(",")[0].strip())
            .value_counts()
            .head(10)
        )
        st.bar_chart(top_countries, height=260)

    st.markdown("#### :material/table_view: Cuplikan Data (25 Baris)")
    st.dataframe(
        df_filtered[["title", "type", "release_year", "rating", "duration", "listed_in"]].head(25),
        width="stretch",
        hide_index=True,
    )