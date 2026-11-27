import csv
from collections import Counter
from pathlib import Path

file_dataset = Path(__file__).parent / "netflix_titles.csv"

total_tayangan = 0
jenis_tayangan = Counter()
negara_terbanyak = Counter()
rilis_terbaru = []

with open(file_dataset, mode="r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        total_tayangan += 1
        tipe = row["type"].strip()
        jenis_tayangan[tipe] += 1

        negara = row["country"].split(",")[0].strip()
        if negara:
            negara_terbanyak[negara] += 1

        if row["release_year"].isdigit() and int(row["release_year"]) >= 2019:
            rilis_terbaru.append((row["title"], tipe, row["release_year"], row["rating"]))

print("=== ANALISIS DATASET NETFLIX (SUMBER: KAGGLE / GITHUB) ===")
print(f"Total Judul dalam Dataset : {total_tayangan:,} judul")
print(f"Jumlah Movie              : {jenis_tayangan['Movie']:,}")
print(f"Jumlah TV Show            : {jenis_tayangan['TV Show']:,}")

print("\n=== 5 NEGARA PRODUKSI TERBANYAK ===")
for negara, jumlah in negara_terbanyak.most_common(5):
    print(f"- {negara}: {jumlah:,} judul")

print("\n=== CONTOH 5 TAYANGAN RILIS >= 2019 ===")
for judul, tipe, tahun, rating in rilis_terbaru[:5]:
    print(f"- {judul} ({tipe}, {tahun}) | Rating: {rating}")
    

    # --- TAMBAHAN FITUR PENCARIAN JUDUL ---
cari = input("\nMasukkan kata kunci judul film/serial (atau Enter untuk lewati): ").strip().lower()

if cari:
    hasil = []
    with open(file_dataset, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if cari in row["title"].lower():
                hasil.append(row)

    print(f"\nDitemukan {len(hasil)} hasil untuk '{cari}':")
    for item in hasil[:10]:
        print(f"- {item['title']} | {item['type']} | {item['release_year']} | {item['listed_in']}")