import csv
import html
import json
import random
from collections import Counter
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

FILE_DATASET = Path(__file__).parent / "netflix_titles.csv"


def baca_dataset():
    data = []
    with open(FILE_DATASET, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data


DATA_NETFLIX = baca_dataset()


def buat_payload_detail(r):
    return html.escape(
        json.dumps(
            {
                "title": r.get("title", "-"),
                "type": r.get("type", "-"),
                "year": r.get("release_year", "-"),
                "rating": r.get("rating", "-"),
                "duration": r.get("duration", "-"),
                "director": r.get("director") or "Tidak tercantum",
                "cast": r.get("cast") or "Tidak tercantum",
                "country": r.get("country") or "Tidak tercantum",
                "genre": r.get("listed_in", "-"),
                "desc": r.get("description", "-"),
            }
        )
    )


class NetflixWebHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        kata_kunci = params.get("q", [""])[0].strip()
        filter_tipe = params.get("type", ["ALL"])[0].strip()
        filter_tahun = params.get("year", [""])[0].strip()
        filter_rating = params.get("rating", ["ALL"])[0].strip()

        total = len(DATA_NETFLIX)
        jenis = Counter(r["type"].strip() for r in DATA_NETFLIX if r.get("type"))
        negara = Counter(
            r["country"].split(",")[0].strip()
            for r in DATA_NETFLIX
            if r.get("country") and r["country"].strip()
        )
        tahun_counter = Counter(
            r["release_year"].strip()
            for r in DATA_NETFLIX
            if r.get("release_year") and r["release_year"].strip().isdigit()
        )
        daftar_rating = sorted(
            {r["rating"].strip() for r in DATA_NETFLIX if r.get("rating") and r["rating"].strip()}
        )

        # Terapkan filter
        hasil = DATA_NETFLIX
        if filter_tipe in ("Movie", "TV Show"):
            hasil = [r for r in hasil if r.get("type", "").strip() == filter_tipe]
        if filter_tahun:
            hasil = [r for r in hasil if r.get("release_year", "").strip() == filter_tahun]
        if filter_rating != "ALL":
            hasil = [r for r in hasil if r.get("rating", "").strip() == filter_rating]
        if kata_kunci:
            hasil = [r for r in hasil if kata_kunci.lower() in r.get("title", "").lower()]

        ada_filter = bool(
            kata_kunci or filter_tipe != "ALL" or filter_tahun or filter_rating != "ALL"
        )
        total_ditemukan = len(hasil)
        hasil_tampil = hasil[:50] if ada_filter else hasil[:20]

        judul_tabel = (
            f"Menampilkan {len(hasil_tampil)} dari {total_ditemukan:,} hasil"
            if ada_filter
            else "20 Data Pertama dari Dataset Netflix"
        )

        # Rekomendasi acak dari hasil filter (fallback ke seluruh dataset jika kosong)
        sumber_acak = hasil if hasil else DATA_NETFLIX
        item_acak = random.choice(sumber_acak) if sumber_acak else None
        payload_acak = buat_payload_detail(item_acak) if item_acak else "{}"

        # Grafik 5 negara terbanyak
        top_negara = negara.most_common(5)
        max_negara = top_negara[0][1] if top_negara else 1
        grafik_negara = ""
        for n, jml in top_negara:
            persen = int((jml / max_negara) * 100)
            grafik_negara += f"""
            <div class="bar-row">
                <div class="bar-label">{html.escape(n)}</div>
                <div class="bar-track">
                    <div class="bar-fill" style="width: {persen}%;">{jml:,} judul</div>
                </div>
            </div>
            """

        # Grafik tren 5 tahun terakhir berdasarkan tahun rilis tertinggi di dataset
        top_tahun = sorted(tahun_counter.items(), key=lambda x: x[0], reverse=True)[:5]
        top_tahun.reverse()
        max_tahun = max((jml for _, jml in top_tahun), default=1)
        grafik_tahun = ""
        for thn, jml in top_tahun:
            persen = int((jml / max_tahun) * 100)
            grafik_tahun += f"""
            <div class="bar-row">
                <div class="bar-label">{html.escape(thn)}</div>
                <div class="bar-track">
                    <div class="bar-fill bar-fill-alt" style="width: {persen}%;">{jml:,} rilis</div>
                </div>
            </div>
            """

        # Baris tabel
        baris_tabel = ""
        for r in hasil_tampil:
            detail_payload = buat_payload_detail(r)
            tipe_val = r.get("type", "-")
            badge_cls = "badge-movie" if tipe_val == "Movie" else "badge-tv"
            baris_tabel += f"""
            <tr>
                <td><strong>{html.escape(r.get('title', '-'))}</strong></td>
                <td><span class="badge {badge_cls}">{html.escape(tipe_val)}</span></td>
                <td>{html.escape(r.get('release_year', '-'))}</td>
                <td>{html.escape(r.get('rating', '-'))}</td>
                <td>{html.escape(r.get('listed_in', '-'))}</td>
                <td><button type="button" class="btn-detail" data-info="{detail_payload}" onclick="bukaDetail(this)">Detail</button></td>
            </tr>
            """

        if not baris_tabel:
            baris_tabel = """
            <tr>
                <td colspan="6" style="text-align:center; color:#aaa; padding:20px;">
                    Tidak ada tayangan yang cocok dengan kombinasi filter tersebut.
                </td>
            </tr>
            """

        sel_all = "selected" if filter_tipe == "ALL" else ""
        sel_movie = "selected" if filter_tipe == "Movie" else ""
        sel_tv = "selected" if filter_tipe == "TV Show" else ""

        opsi_rating = ['<option value="ALL">Semua Rating</option>']
        for rt in daftar_rating:
            sel = "selected" if filter_rating == rt else ""
            opsi_rating.append(f'<option value="{html.escape(rt)}" {sel}>{html.escape(rt)}</option>')
        html_rating = "\n".join(opsi_rating)

        halaman_html = f"""<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <title>Analisis Dataset Netflix</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #141414; color: #fff; margin: 0; padding: 24px; }}
        .container {{ max-width: 1080px; margin: auto; }}
        .header-row {{ display: flex; justify-content: space-between; align-items: center; gap: 12px; flex-wrap: wrap; }}
        h1 {{ color: #e50914; margin-bottom: 4px; }}
        .sub {{ color: #999; margin-top: 0; }}
        .cards {{ display: flex; gap: 16px; margin: 20px 0; flex-wrap: wrap; }}
        .card {{ background: #1f1f1f; padding: 16px 20px; border-radius: 10px; flex: 1; min-width: 180px; border: 1px solid #2c2c2c; }}
        .card h3 {{ margin: 0 0 8px; color: #aaa; font-size: 13px; text-transform: uppercase; }}
        .card p {{ margin: 0; font-size: 26px; font-weight: bold; }}
        .grid-2 {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 16px; margin-bottom: 20px; }}
        .box {{ background: #1f1f1f; padding: 20px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #2c2c2c; }}
        .grid-2 .box {{ margin-bottom: 0; }}

        /* Grafik Batang */
        .bar-row {{ display: flex; align-items: center; margin-bottom: 10px; gap: 12px; }}
        .bar-label {{ width: 120px; font-size: 14px; font-weight: bold; }}
        .bar-track {{ flex: 1; background: #2c2c2c; border-radius: 6px; overflow: hidden; height: 26px; }}
        .bar-fill {{ background: #e50914; height: 100%; line-height: 26px; padding-left: 10px; font-size: 12px; font-weight: bold; white-space: nowrap; }}
        .bar-fill-alt {{ background: #2563eb; }}

        /* Form Filter */
        form {{ display: flex; gap: 10px; margin-bottom: 16px; flex-wrap: wrap; }}
        input[type="text"], input[type="number"], select {{ padding: 10px 12px; border-radius: 6px; border: 1px solid #444; background: #2a2a2a; color: #fff; font-size: 14px; }}
        input[type="text"] {{ flex: 1; min-width: 200px; }}
        input[type="number"] {{ width: 110px; }}
        button {{ padding: 10px 18px; background: #e50914; color: #fff; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; }}
        button:hover {{ background: #b80710; }}
        .btn-random {{ background: #7c3aed; }}
        .btn-random:hover {{ background: #6d28d9; }}
        a.reset {{ padding: 10px 16px; background: #3a3a3a; color: #fff; text-decoration: none; border-radius: 6px; font-size: 14px; display: inline-flex; align-items: center; }}

        /* Tabel & Badge */
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 14px; }}
        th, td {{ padding: 10px; border-bottom: 1px solid #2e2e2e; text-align: left; }}
        th {{ background: #292929; }}
        .badge {{ padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }}
        .badge-movie {{ background: #1d4ed8; }}
        .badge-tv {{ background: #047857; }}
        .btn-detail {{ padding: 6px 12px; font-size: 12px; background: #374151; }}
        .btn-detail:hover {{ background: #4b5563; }}

        /* Modal Pop-up */
        .modal {{ display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.75); justify-content: center; align-items: center; padding: 20px; z-index: 99; }}
        .modal-content {{ background: #222; padding: 24px; border-radius: 10px; max-width: 560px; width: 100%; border: 1px solid #444; }}
        .modal-content h2 {{ margin-top: 0; color: #e50914; }}
        .modal-meta {{ color: #bbb; font-size: 13px; margin-bottom: 12px; }}
        .modal-desc {{ line-height: 1.5; margin-bottom: 16px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header-row">
            <div>
                <h1>Analisis Dataset Netflix</h1>
                <p class="sub">Sumber Dataset: Kaggle / GitHub (<code>netflix_titles.csv</code>)</p>
            </div>
            <button type="button" class="btn-random" data-info="{payload_acak}" onclick="bukaDetail(this)">
                Acak Rekomendasi
            </button>
        </div>

        <div class="cards">
            <div class="card"><h3>Total Tayangan</h3><p>{total:,}</p></div>
            <div class="card"><h3>Movie</h3><p>{jenis.get('Movie', 0):,}</p></div>
            <div class="card"><h3>TV Show</h3><p>{jenis.get('TV Show', 0):,}</p></div>
        </div>

        <div class="grid-2">
            <div class="box">
                <h3>5 Negara Produksi Terbanyak</h3>
                {grafik_negara}
            </div>
            <div class="box">
                <h3>Tren 5 Tahun Rilis Terbaru di Dataset</h3>
                {grafik_tahun}
            </div>
        </div>

        <div class="box">
            <h3>Eksplorasi & Filter Tayangan</h3>
            <form method="GET" action="/">
                <input type="text" name="q" placeholder="Ketik kata kunci judul (misal: love, dark, spider)..." value="{html.escape(kata_kunci)}">
                <select name="type">
                    <option value="ALL" {sel_all}>Semua Tipe</option>
                    <option value="Movie" {sel_movie}>Movie Saja</option>
                    <option value="TV Show" {sel_tv}>TV Show Saja</option>
                </select>
                <input type="number" name="year" placeholder="Tahun" min="1900" max="2030" value="{html.escape(filter_tahun)}">
                <select name="rating">
                    {html_rating}
                </select>
                <button type="submit">Filter / Cari</button>
                <a class="reset" href="/">Reset</a>
            </form>

            <h4>{judul_tabel}</h4>
            <table>
                <thead>
                    <tr>
                        <th>Judul</th>
                        <th>Tipe</th>
                        <th>Tahun</th>
                        <th>Rating</th>
                        <th>Genre</th>
                        <th>Aksi</th>
                    </tr>
                </thead>
                <tbody>{baris_tabel}</tbody>
            </table>
        </div>
    </div>

    <div id="detailModal" class="modal" onclick="tutupModal(event)">
        <div class="modal-content" onclick="event.stopPropagation()">
            <h2 id="mTitle"></h2>
            <div id="mMeta" class="modal-meta"></div>
            <p id="mDesc" class="modal-desc"></p>
            <p><strong>Sutradara:</strong> <span id="mDirector"></span></p>
            <p><strong>Pemain:</strong> <span id="mCast"></span></p>
            <p><strong>Negara:</strong> <span id="mCountry"></span></p>
            <button type="button" onclick="document.getElementById('detailModal').style.display='none'">Tutup</button>
        </div>
    </div>

    <script>
        function bukaDetail(btn) {{
            const data = JSON.parse(btn.getAttribute('data-info'));
            document.getElementById('mTitle').textContent = data.title;
            document.getElementById('mMeta').textContent = `${{data.type}} • ${{data.year}} • Rating: ${{data.rating}} • ${{data.duration}}`;
            document.getElementById('mDesc').textContent = data.desc;
            document.getElementById('mDirector').textContent = data.director;
            document.getElementById('mCast').textContent = data.cast;
            document.getElementById('mCountry').textContent = data.country;
            document.getElementById('detailModal').style.display = 'flex';
        }}
        function tutupModal(e) {{
            if (e.target.id === 'detailModal') {{
                document.getElementById('detailModal').style.display = 'none';
            }}
        }}
    </script>
</body>
</html>"""

        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(halaman_html.encode("utf-8"))


if __name__ == "__main__":
    server = HTTPServer(("localhost", 8000), NetflixWebHandler)
    print("Server jalan! Refresh Chrome di: http://localhost:8000")
    server.serve_forever()