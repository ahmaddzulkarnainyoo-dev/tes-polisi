"""
engine.py — CAT Psikotes Polri v3.1
Sesi:
  1. Pass Hand   → Pernyataan YA/TIDAK (profiling polisi, skor 0)
  2. Kecerdasan  → Groq AI + template math dasar + soal spasial/mata angin
  3. Kecermatan  → Angka hilang dari kunci kolom (sesuai PDF 2025)
  4. Kepribadian → Groq AI, Likert 5 skala (pernyataan + arah positif/negatif)
"""

import json
import re
import random
import time
import math
from groq import Groq
import streamlit as st

# ──────────────────────────────────────────────
# CLIENT
# ──────────────────────────────────────────────
def get_client() -> Groq:
    return Groq(api_key=st.secrets["GROQ_API_KEY"])


# ══════════════════════════════════════════════
# 1. PASS HAND → YA/TIDAK Profiling
# ══════════════════════════════════════════════

_PERNYATAAN_POLISI = [
    ("Saya akan menegur rekan yang melanggar prosedur meski ia lebih senior.", True),
    ("Dalam situasi darurat, prosedur boleh diabaikan demi menyelamatkan nyawa.", True),
    ("Saya lebih memilih diam daripada melaporkan atasan yang korupsi.", False),
    ("Kepentingan kelompok harus selalu di atas kepentingan pribadi dalam tugas.", True),
    ("Saya bersedia bertugas malam tanpa kompensasi jika negara membutuhkan.", True),
    ("Saya akan mengikuti perintah atasan meskipun bertentangan dengan hati nurani.", False),
    ("Integritas adalah aset terpenting seorang aparat kepolisian.", True),
    ("Saya akan melaporkan teman dekat yang terbukti melakukan pelanggaran hukum.", True),
    ("Menerima hadiah kecil dari warga yang sudah dibantu adalah hal wajar.", False),
    ("Saya mampu bekerja di bawah tekanan tanpa mempengaruhi kualitas tugas.", True),
    ("Saya lebih suka bertugas di kota besar daripada daerah terpencil.", False),
    ("Kepatuhan pada hukum tidak boleh dikompromikan dengan alasan apapun.", True),
    ("Saya bersedia melatih anggota junior meski itu bukan tanggung jawab saya.", True),
    ("Kritik dari masyarakat terhadap polisi harus ditanggapi dengan profesional.", True),
    ("Menggunakan fasilitas dinas untuk keperluan pribadi sekali-kali adalah wajar.", False),
    ("Saya siap ditempatkan di mana saja sesuai kebutuhan institusi.", True),
    ("Kecepatan bertindak lebih penting dari akurasi dalam situasi darurat.", False),
    ("Saya akan selalu transparan dalam membuat laporan meski hasilnya buruk.", True),
    ("Persatuan sesama anggota lebih penting dari kebenaran dalam sebuah kasus.", False),
    ("Saya mampu mengendalikan emosi saat menghadapi warga yang kasar.", True),
    ("Pelatihan fisik rutin adalah kewajiban yang tidak bisa dihindari.", True),
    ("Saya percaya bahwa reputasi institusi harus dijaga di atas segalanya.", False),
    ("Mengakui kesalahan sendiri adalah tanda kekuatan, bukan kelemahan.", True),
    ("Warga sipil berhak mendapat perlakuan hormat dan adil dari aparat.", True),
    ("Loyalitas pada atasan lebih penting dari ketaatan pada prosedur resmi.", False),
    ("Saya akan tetap profesional meski bertugas saat hari libur keluarga.", True),
    ("Keberanian fisik adalah syarat utama menjadi polisi yang baik.", False),
    ("Saya akan menolak tawaran suap meski kondisi keuangan saya sedang sulit.", True),
    ("Kerja tim yang solid lebih berdampak besar daripada kerja individu berbakat.", True),
    ("Saya tidak masalah mendapat tugas administratif daripada tugas lapangan.", True),
]

def generate_pass_hand() -> dict:
    pernyataan, jawaban_ideal = random.choice(_PERNYATAAN_POLISI)
    return {
        "pernyataan": pernyataan,
        "jawaban_ideal": jawaban_ideal,
        "instruksi": "Jawab dengan jujur sesuai kondisi dan sikap Anda sebenarnya.",
        "skor": 0,
    }

def hitung_aps(jumlah_klik: int, durasi_detik: float) -> dict:
    aps = round(jumlah_klik / max(durasi_detik, 0.001), 2)
    if aps >= 3.0:
        kategori, deskripsi = "Sangat Baik", "Koordinasi mata-tangan sangat responsif."
    elif aps >= 2.0:
        kategori, deskripsi = "Baik", "Koordinasi mata-tangan di atas rata-rata."
    elif aps >= 1.0:
        kategori, deskripsi = "Cukup", "Koordinasi mata-tangan rata-rata."
    else:
        kategori, deskripsi = "Kurang", "Perlu latihan koordinasi lebih lanjut."
    return {
        "jumlah_klik": jumlah_klik,
        "durasi_detik": round(durasi_detik, 2),
        "aps": aps,
        "kategori": kategori,
        "deskripsi": deskripsi,
    }

def posisi_target_acak(area_width: int, area_height: int, target_size: int) -> dict:
    x = random.randint(0, max(0, area_width - target_size))
    y = random.randint(0, max(0, area_height - target_size))
    return {"x": x, "y": y}


# ══════════════════════════════════════════════
# 2. KECERDASAN
# ══════════════════════════════════════════════

def _soal_matematika() -> dict:
    tipe = random.choice(["campuran", "perkalian", "pembagian", "pecahan", "persentase"])

    if tipe == "campuran":
        a, b, c = random.randint(10, 99), random.randint(2, 9), random.randint(5, 50)
        ops = random.choice(["+", "-"])
        if ops == "+":
            jawaban = a * b + c
            soal = f"Berapakah hasil dari {a} × {b} + {c}?"
        else:
            jawaban = a * b - c
            soal = f"Berapakah hasil dari {a} × {b} - {c}?"

    elif tipe == "perkalian":
        a, b = random.randint(12, 99), random.randint(11, 25)
        jawaban = a * b
        soal = f"Berapakah hasil dari {a} × {b}?"

    elif tipe == "pembagian":
        b = random.randint(4, 12)
        jawaban = random.randint(10, 50)
        a = b * jawaban
        soal = f"Berapakah hasil dari {a} ÷ {b}?"

    elif tipe == "pecahan":
        b = random.choice([4, 6, 8, 12])
        d = random.choice([3, 4, 6])
        a = random.randint(1, b - 1)
        c = random.randint(1, d - 1)
        from math import gcd
        import fractions
        val = fractions.Fraction(a, b) + fractions.Fraction(c, d)
        jawaban = str(val.numerator) if val.denominator == 1 else f"{val.numerator}/{val.denominator}"
        soal = f"Berapakah hasil dari {a}/{b} + {c}/{d}?"

    else:  # persentase
        persen = random.choice([10, 15, 20, 25, 30, 40, 50])
        total = random.choice([200, 400, 500, 800, 1000, 1200, 1500, 2000])
        jawaban = total * persen // 100
        soal = f"Berapa {persen}% dari {total}?"

    if isinstance(jawaban, str):
        import fractions
        base = fractions.Fraction(jawaban)
        val_float = float(base)
        benar = jawaban
        distractors = set()
        for delta in [0.25, 0.5, -0.25, -0.5, 1, -1]:
            d = fractions.Fraction(val_float + delta).limit_denominator(12)
            if d != base:
                distractors.add(str(d.numerator) if d.denominator == 1 else f"{d.numerator}/{d.denominator}")
        distractors = list(distractors)[:3]
    else:
        benar = jawaban
        deltas = random.sample([-3, -2, -1, 1, 2, 3, 4, 5, -4, -5], 4)
        distractors = [benar + d for d in deltas[:3]]

    opsi_vals = [benar] + distractors
    random.shuffle(opsi_vals)
    huruf = ["A", "B", "C", "D", "E"]
    opsi = [f"{huruf[i]}. {opsi_vals[i]}" for i in range(len(opsi_vals))]
    jawaban_huruf = huruf[opsi_vals.index(benar)]

    return {
        "pertanyaan": soal,
        "opsi": opsi,
        "jawaban": jawaban_huruf,
        "kategori": "Matematika Dasar",
        "skor_benar": 5,
        "skor_salah": 0,
    }


_ARAH = ["Utara", "Selatan", "Timur", "Barat", "Timur Laut", "Barat Laut", "Tenggara", "Barat Daya"]
_ARAH_LAWAN = {
    "Utara": "Selatan", "Selatan": "Utara",
    "Timur": "Barat", "Barat": "Timur",
    "Timur Laut": "Barat Daya", "Barat Daya": "Timur Laut",
    "Tenggara": "Barat Laut", "Barat Laut": "Tenggara",
}
_PUTAR_90CW = {
    "Utara": "Timur", "Timur": "Selatan", "Selatan": "Barat", "Barat": "Utara",
    "Timur Laut": "Tenggara", "Tenggara": "Barat Daya",
    "Barat Daya": "Barat Laut", "Barat Laut": "Timur Laut",
}

def _soal_spasial() -> dict:
    tipe = random.choice(["lawan_arah", "putar_90", "denah_jarak"])

    if tipe == "lawan_arah":
        arah = random.choice(list(_ARAH_LAWAN.keys()))
        jawaban_str = _ARAH_LAWAN[arah]
        soal = f"Seseorang berjalan menghadap {arah}. Jika ia berbalik arah 180°, ia kini menghadap ke arah ....?"

    elif tipe == "putar_90":
        arah_awal = random.choice(list(_PUTAR_90CW.keys()))
        kali = random.choice([1, 2, 3])
        arah_sekarang = arah_awal
        for _ in range(kali):
            arah_sekarang = _PUTAR_90CW[arah_sekarang]
        jawaban_str = arah_sekarang
        derajat = kali * 90
        soal = f"Seorang polisi menghadap {arah_awal}, lalu berputar {derajat}° searah jarum jam. Ia kini menghadap ke arah ....?"

    else:
        jarak1 = random.randint(2, 8)
        jarak2 = random.randint(2, 8)
        arah1 = random.choice(["Utara", "Selatan"])
        arah2 = random.choice(["Timur", "Barat"])
        soal = (
            f"Dari Pos A, Rudi berjalan {jarak1} km ke {arah1}, "
            f"kemudian {jarak2} km ke {arah2}. "
            f"Berapa km jarak lurus Rudi dari Pos A?"
        )
        jawaban_val = round(math.sqrt(jarak1**2 + jarak2**2), 1)
        jawaban_str = str(jawaban_val)

    if tipe in ("lawan_arah", "putar_90"):
        pilihan = [jawaban_str]
        pool = [a for a in _ARAH if a != jawaban_str]
        random.shuffle(pool)
        pilihan += pool[:3]
    else:
        base = float(jawaban_str)
        deltas = [-1.0, -0.5, 0.5, 1.0, 1.5, -1.5]
        random.shuffle(deltas)
        pilihan = [jawaban_str]
        seen = {base}
        for d in deltas:
            v = round(base + d, 1)
            if v > 0 and v not in seen:
                pilihan.append(str(v))
                seen.add(v)
            if len(pilihan) == 4:
                break

    random.shuffle(pilihan)
    huruf = ["A", "B", "C", "D"]
    opsi = [f"{huruf[i]}. {pilihan[i]}" for i in range(len(pilihan))]
    jawaban_huruf = huruf[pilihan.index(jawaban_str)]

    return {
        "pertanyaan": soal,
        "opsi": opsi,
        "jawaban": jawaban_huruf,
        "kategori": "Spasial / Mata Angin",
        "skor_benar": 5,
        "skor_salah": 0,
    }


_FALLBACK_KECERDASAN = {
    "pertanyaan": "Jika 3x + 7 = 22, berapakah nilai x?",
    "opsi": ["A. 3", "B. 4", "C. 5", "D. 6", "E. 7"],
    "jawaban": "C",
    "kategori": "Matematika",
    "skor_benar": 5,
    "skor_salah": 0,
}

def generate_soal_kecerdasan(kategori: str = "acak") -> dict:
    if kategori == "acak":
        roll = random.random()
        if roll < 0.40:
            return _soal_matematika()
        elif roll < 0.60:
            return _soal_spasial()

    groq_kategori_pool = ["Verbal", "Logika", "Wawasan Kebangsaan"]
    if kategori in groq_kategori_pool:
        selected = kategori
    else:
        selected = random.choice(groq_kategori_pool)

    prompt = f"""Buat 1 soal psikotes Polri kategori {selected} tingkat menengah.
HANYA JSON, tanpa markdown:
{{"pertanyaan":"...","opsi":["A. ...","B. ...","C. ...","D. ...","E. ..."],"jawaban":"huruf","kategori":"{selected}"}}
Jawaban benar WAJIB ada di opsi."""

    try:
        client = get_client()
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=300,
        )
        raw = resp.choices[0].message.content
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        data = json.loads(match.group() if match else raw)
        data["skor_benar"] = 5
        data["skor_salah"] = 0
        data["jawaban"] = str(data.get("jawaban", "A")).strip().upper()[0]
        if "opsi" not in data or len(data["opsi"]) < 4:
            raise ValueError("opsi tidak lengkap")
        return data
    except Exception:
        return _FALLBACK_KECERDASAN.copy()


def nilai_jawaban_kecerdasan(jawaban_user: str, jawaban_benar: str) -> int:
    return 5 if str(jawaban_user).strip().upper()[0] == str(jawaban_benar).strip().upper()[0] else 0


# ══════════════════════════════════════════════
# 3. KECERMATAN — Karakter Hilang (sesuai PDF 2025)
# ══════════════════════════════════════════════

_KUNCI_KOLOM = [
    {"nama": "KOLOM 1", "kunci": list("ZPTXQ")},
    {"nama": "KOLOM 2", "kunci": list("YLKJC")},
    {"nama": "KOLOM 3", "kunci": list("OSRVU")},
    {"nama": "KOLOM 4", "kunci": list("BGFHI")},
    {"nama": "KOLOM 5", "kunci": list("SNAWM")},
]

def generate_kecermatan() -> dict:
    """
    Tampilkan 4 dari 5 karakter kunci, user pilih yang hilang.
    Tidak ada tanda tanya — user harus mandiri mengenali karakter yang absen.
    """
    kolom = random.choice(_KUNCI_KOLOM)
    kunci = kolom["kunci"].copy()

    hilang = random.choice(kunci)
    tampilan = [k for k in kunci if k != hilang]
    random.shuffle(tampilan)

    opsi = kunci.copy()
    random.shuffle(opsi)

    return {
        "nama_kolom": kolom["nama"],
        "kunci": kunci,
        "tampilan": " ".join(tampilan),
        "jawaban": hilang,
        "opsi": opsi,
        "timestamp_mulai": time.time(),
    }


def catat_waktu_jawab(soal: dict) -> float:
    return round(time.time() - soal["timestamp_mulai"], 3)


def hitung_ketahanan(waktu_per_soal: list) -> dict:
    n = len(waktu_per_soal)
    if n == 0:
        return {"jumlah_soal": 0, "rata_rata_detik": 0.0, "std_dev": 0.0,
                "cv_persen": 0.0, "skor_ketahanan": 0, "kategori": "Tidak ada data"}
    rata = sum(waktu_per_soal) / n
    variance = sum((t - rata) ** 2 for t in waktu_per_soal) / n
    std = math.sqrt(variance)
    cv = (std / rata * 100) if rata > 0 else 0.0
    if cv < 20:
        skor = int(90 + (20 - cv) / 20 * 10)
        kategori = "Sangat Stabil"
    elif cv < 40:
        skor = int(70 + (40 - cv) / 20 * 19)
        kategori = "Stabil"
    elif cv < 60:
        skor = int(50 + (60 - cv) / 20 * 19)
        kategori = "Cukup Stabil"
    else:
        skor = max(0, int(50 - (cv - 60) / 40 * 50))
        kategori = "Tidak Stabil"
    return {
        "jumlah_soal": n,
        "rata_rata_detik": round(rata, 3),
        "std_dev": round(std, 3),
        "cv_persen": round(cv, 2),
        "skor_ketahanan": min(skor, 100),
        "kategori": kategori,
    }


def nilai_jawaban_kecermatan(jawaban_user: str, jawaban_benar: str) -> int:
    return 1 if str(jawaban_user).strip().upper() == str(jawaban_benar).strip().upper() else 0


# ══════════════════════════════════════════════
# 4. KEPRIBADIAN — Likert 5 Skala
# ══════════════════════════════════════════════
# Format baru: AI hanya generate PERNYATAAN + arah (positif/negatif).
# Opsi A–E ditampilkan statis di app.py.
# Skor:
#   Pernyataan POSITIF → SS=5, S=4, RR=3, TS=2, STS=1
#   Pernyataan NEGATIF → SS=1, S=2, RR=3, TS=4, STS=5

LIKERT_OPSI = [
    "A. Sangat Setuju",
    "B. Setuju",
    "C. Ragu-ragu",
    "D. Tidak Setuju",
    "E. Sangat Tidak Setuju",
]

LIKERT_SKOR_POSITIF = {"A": 5, "B": 4, "C": 3, "D": 2, "E": 1}
LIKERT_SKOR_NEGATIF = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5}

_FALLBACK_KEPRIBADIAN = {
    "pernyataan": "Saya selalu melaporkan pelanggaran yang saya saksikan meskipun pelakunya adalah rekan dekat.",
    "arah": "positif",
    "kategori": "Kepribadian",
}

def generate_soal_kepribadian() -> dict:
    """
    Generate PERNYATAAN psikologis saja (Likert).
    Opsi dan skor dihitung di app.py secara statis.
    Arah 'positif' = setuju berarti baik; 'negatif' = setuju berarti buruk.
    """
    prompt = """Buat 1 pernyataan tes kepribadian Polri untuk Likert scale.
Tema: integritas, kedisiplinan, loyalitas, profesionalisme, atau etika.
Tentukan apakah pernyataan bersifat POSITIF (setuju = baik) atau NEGATIF (setuju = buruk).
HANYA JSON tanpa markdown:
{"pernyataan":"...","arah":"positif","kategori":"Kepribadian"}
Arah hanya boleh: "positif" atau "negatif"."""

    try:
        client = get_client()
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.85,
            max_tokens=200,
        )
        raw = resp.choices[0].message.content
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        data = json.loads(match.group() if match else raw)
        if "pernyataan" not in data:
            raise ValueError("pernyataan missing")
        arah = str(data.get("arah", "positif")).lower().strip()
        if arah not in ("positif", "negatif"):
            arah = "positif"
        data["arah"] = arah
        data["kategori"] = "Kepribadian"
        return data
    except Exception:
        return _FALLBACK_KEPRIBADIAN.copy()


def nilai_jawaban_kepribadian(jawaban_user: str, arah: str) -> int:
    """
    Hitung skor berdasarkan jawaban Likert dan arah pernyataan.
    jawaban_user: huruf A/B/C/D/E
    arah: 'positif' atau 'negatif'
    """
    key = str(jawaban_user).strip().upper()[0]
    if arah == "negatif":
        return LIKERT_SKOR_NEGATIF.get(key, 3)
    return LIKERT_SKOR_POSITIF.get(key, 3)


# ══════════════════════════════════════════════
# DISPATCHER
# ══════════════════════════════════════════════

def generate_soal_ai(sesi: str = "Kecerdasan") -> dict:
    sesi = sesi.strip().title()
    if sesi == "Kepribadian":
        return generate_soal_kepribadian()
    elif sesi == "Kecermatan":
        return generate_kecermatan()
    elif sesi in ("Pass Hand", "Pass_Hand"):
        return generate_pass_hand()
    else:
        return generate_soal_kecerdasan()


# ══════════════════════════════════════════════
# REKAP SKOR AKHIR
# ══════════════════════════════════════════════

def rekap_sesi(pass_hand=None, kecerdasan=None, kecermatan=None, kepribadian=None) -> dict:
    hasil = {}
    if pass_hand:
        hasil["pass_hand"] = pass_hand
    if kecerdasan:
        total = max(kecerdasan.get("total", 1), 1)
        benar = kecerdasan.get("benar", 0)
        hasil["kecerdasan"] = {
            "skor": benar * 5, "benar": benar,
            "salah": kecerdasan.get("salah", total - benar),
            "total_soal": total,
            "akurasi_persen": round(benar / total * 100, 1),
        }
    if kecermatan:
        total = max(kecermatan.get("total", 1), 1)
        benar = kecermatan.get("benar", 0)
        hasil["kecermatan"] = {
            "skor_akurasi": benar, "total_soal": total,
            "akurasi_persen": round(benar / total * 100, 1),
            "ketahanan": kecermatan.get("ketahanan", {}),
        }
    if kepribadian:
        jml = max(kepribadian.get("jumlah_soal", 1), 1)
        total_skor = kepribadian.get("total_skor", 0)
        hasil["kepribadian"] = {
            "skor_total": total_skor, "jumlah_soal": jml,
            "rata_rata": round(total_skor / jml, 2),
            "skor_maks_mungkin": jml * 5,
        }
    hasil["catatan"] = "Hasil bersifat simulatif dan tidak menggantikan tes resmi Polri."
    return hasil
