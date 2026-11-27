# Implementasi CRISP-DM untuk Klasifikasi Katalog Netflix (Movie vs TV Show) Berbasis Web Streamlit

Proyek akhir *Machine Learning* end-to-end berbasis metodologi **CRISP-DM** menggunakan dataset `netflix_titles.csv` untuk mengklasifikasikan konten katalog Netflix menjadi **Movie** atau **TV Show**, dilengkapi aplikasi web interaktif berbasis **Streamlit**.

## Identitas Penyusun
- **Nama:** Hamdan Hafizh
- **NPM:** 202343501215
- **Kelas:** X7I
- **Program Studi:** Teknik Informatika

## Ringkasan Model & Evaluasi
Evaluasi model dilakukan menggunakan `StratifiedKFold(n_splits=5)` dan `GridSearchCV` pada fitur numerik, *rating*, serta korpus teks TF-IDF:
- **Decision Tree**
- **K-Nearest Neighbors (KNN)**
- **Naive Bayes Classifier** (model terbaik, disimpan sebagai `best_netflix_model.joblib`, dengan ROC-AUC `0.9999` dan Precision `1.0000`)

## Struktur File di Repository
- `train_ml.py` — Skrip *preprocessing*, pelatihan, *tuning* hiperparameter, evaluasi, dan penyimpanan model terbaik (`best_netflix_model.joblib`).
- `app_streamlit.py` — Aplikasi web interaktif Streamlit untuk prediksi katalog, inspeksi fitur, dan eksplorasi data (EDA).
- `best_netflix_model.joblib` — Model klasifikasi terbaik hasil pelatihan.
- `netflix_titles.csv` — Dataset katalog Netflix.
- `app_netflix.py` & `web_netflix.py` — File pendukung/alternatif aplikasi web.

## Cara Menjalankan Lokal
1. Instal dependensi utama:
   ```bash
   pip install streamlit scikit-learn pandas numpy joblib# Implementasi CRISP-DM untuk Klasifikasi Katalog Netflix (Movie vs TV Show) Berbasis Web Streamlit

Proyek akhir *Machine Learning* end-to-end berbasis metodologi **CRISP-DM** menggunakan dataset `netflix_titles.csv` untuk mengklasifikasikan konten katalog Netflix menjadi **Movie** atau **TV Show**, dilengkapi aplikasi web interaktif berbasis **Streamlit**.

## Identitas Penyusun
- **Nama:** Hamdan Hafizh
- **NPM:** 202343501215
- **Kelas:** X7I
- **Program Studi:** Teknik Informatika

## Ringkasan Model & Evaluasi
Evaluasi model dilakukan menggunakan `StratifiedKFold(n_splits=5)` dan `GridSearchCV` pada fitur numerik, *rating*, serta korpus teks TF-IDF:
- **Decision Tree**
- **K-Nearest Neighbors (KNN)**
- **Naive Bayes Classifier** (model terbaik, disimpan sebagai `best_netflix_model.joblib`, dengan ROC-AUC `0.9999` dan Precision `1.0000`)

## Struktur File di Repository
- `train_ml.py` — Skrip *preprocessing*, pelatihan, *tuning* hiperparameter, evaluasi, dan penyimpanan model terbaik (`best_netflix_model.joblib`).
- `app_streamlit.py` — Aplikasi web interaktif Streamlit untuk prediksi katalog, inspeksi fitur, dan eksplorasi data (EDA).
- `best_netflix_model.joblib` — Model klasifikasi terbaik hasil pelatihan.
- `netflix_titles.csv` — Dataset katalog Netflix.
- `app_netflix.py` & `web_netflix.py` — File pendukung/alternatif aplikasi web.

## Cara Menjalankan Lokal
1. Instal dependensi utama:

       pip install streamlit scikit-learn pandas numpy joblib

2. Jalankan aplikasi Streamlit:

       streamlit run app_streamlit.py
   
