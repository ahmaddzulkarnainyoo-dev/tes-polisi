"""
engine.py — CAT Psikotes Polri v4.0 (Marathon Edition)
Perubahan v4.0:
- Alur Maraton: Pass Hand → Kecerdasan → Kepribadian → Kecermatan
- Penilaian: 0-100 per sesi, passing grade rata-rata >= 61
- Kecerdasan: Soal Matematika Dasar + Spasial/Mata Angin (update 2025)
- Kepribadian: Likert 5 skala statis, skor adaptif arah
- Kecermatan: Tanpa tanda tanya, auto-submit via button
- Evaluasi: Review jawaban salah di halaman hasil akhir
"""

import json
import re
import random
import time
import math
import fractions as _fractions
from groq import Groq
import streamlit as st


# ──────────────────────────────────────────────
# CLIENT
# ──────────────────────────────────────────────
def get_client() -> Groq:
    return Groq(api_key=st.secrets["GROQ_API_KEY"])


# ══════════════════════════════════════════════
# KONSTANTA GLOBAL
# ══════════════════════════════════════════════
SOAL_PER_SESI   = 10
PASSING_GRADE   = 61       # Rata-rata minimal seluruh sesi
URUTAN_MARATON  = ["Pass Hand", "Kecerdasan", "Kepribadian", "Kecermatan"]

LIKERT_OPSI = [
    "A. Sangat Setuju",
    "B. Setuju",
    "C. Ragu-ragu",
    "D. Tidak Setuju",
    "E. Sangat Tidak Setuju",
]
LIKERT_SKOR_POSITIF = {"A": 5, "B": 4, "C": 3, "D": 2, "E": 1}
LIKERT_SKOR_NEGATIF = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5}


# ══════════════════════════════════════════════
# 1. PASS HAND — YA/TIDAK Profiling
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
        "jawaban_ideal": "YA" if jawaban_ideal else "TIDAK",
        "instruksi": "Jawab dengan jujur sesuai kondisi dan sikap Anda sebenarnya.",
        "sesi": "Pass Hand",
    }

def nilai_pass_hand(jawaban_user: str, jawaban_ideal: str) -> int:
    """Pass Hand: 10 poin jika sesuai profil ideal, 0 jika tidak."""
    return 10 if str(jawaban_user).strip().upper() == str(jawaban_ideal).strip().upper() else 0

def skor_sesi_pass_hand(soal_list: list, jawaban: list) -> dict:
    """Kembalikan skor 0-100 dan detail per soal untuk Pass Hand."""
    detail = []
    total_poin = 0
    for soal, jwb in zip(soal_list, jawaban):
        if jwb is None:
            jwb = "TIDAK"
        ideal  = soal.get("jawaban_ideal", "YA")
        poin   = nilai_pass_hand(jwb, ideal)
        total_poin += poin
        detail.append({
            "pernyataan": soal.get("pernyataan", ""),
            "jawaban_user": jwb,
            "jawaban_ideal": ideal,
            "poin": poin,
            "benar": poin > 0,
            "pembahasan": f"Jawaban ideal adalah '{ideal}'. Pernyataan ini mencerminkan profil integritas dan profesionalisme polisi.",
        })
    skor_100 = round(total_poin / (SOAL_PER_SESI * 10) * 100)
    return {"skor_100": skor_100, "detail": detail}


# ══════════════════════════════════════════════
# 2. KECERDASAN — Matematika + Spasial + AI Verbal/Logika
# ══════════════════════════════════════════════

# ── Matematika Dasar ──
def _soal_matematika() -> dict:
    tipe = random.choice([
        "campuran_kali_tambah", "campuran_kali_kurang",
        "perkalian_dua_digit", "pembagian",
        "pecahan_tambah", "pecahan_kurang",
        "persentase", "rasio",
    ])

    if tipe == "campuran_kali_tambah":
        a, b, c = random.randint(12, 49), random.randint(2, 9), random.randint(5, 50)
        jawaban = a * b + c
        soal = f"Berapakah hasil dari {a} × {b} + {c}?"
        pembahasan = f"{a} × {b} = {a*b}, lalu {a*b} + {c} = {jawaban}"

    elif tipe == "campuran_kali_kurang":
        a, b, c = random.randint(12, 49), random.randint(2, 9), random.randint(5, 50)
        jawaban = a * b - c
        soal = f"Berapakah hasil dari {a} × {b} − {c}?"
        pembahasan = f"{a} × {b} = {a*b}, lalu {a*b} − {c} = {jawaban}"

    elif tipe == "perkalian_dua_digit":
        a, b = random.randint(12, 49), random.randint(11, 25)
        jawaban = a * b
        soal = f"Berapakah hasil dari {a} × {b}?"
        pembahasan = f"{a} × {b} = {jawaban}"

    elif tipe == "pembagian":
        b = random.randint(4, 12)
        jawaban = random.randint(10, 50)
        a = b * jawaban
        soal = f"Berapakah hasil dari {a} ÷ {b}?"
        pembahasan = f"{a} ÷ {b} = {jawaban}"

    elif tipe == "pecahan_tambah":
        b = random.choice([4, 6, 8, 12])
        d = random.choice([3, 4, 6])
        a = random.randint(1, b - 1)
        c = random.randint(1, d - 1)
        val = _fractions.Fraction(a, b) + _fractions.Fraction(c, d)
        jawaban = str(val.numerator) if val.denominator == 1 else f"{val.numerator}/{val.denominator}"
        soal = f"Berapakah hasil dari {a}/{b} + {c}/{d}?"
        pembahasan = f"{a}/{b} + {c}/{d} = {jawaban}"

    elif tipe == "pecahan_kurang":
        b = random.choice([4, 6, 8, 12])
        d = random.choice([3, 4, 6])
        a = random.randint(1, b - 1)
        c = random.randint(1, d - 1)
        val = _fractions.Fraction(a, b) - _fractions.Fraction(c, d)
        jawaban = str(abs(val.numerator)) if val.denominator == 1 else f"{abs(val.numerator)}/{val.denominator}"
        soal = f"Berapakah hasil dari {a}/{b} − {c}/{d}?"
        pembahasan = f"{a}/{b} − {c}/{d} = {jawaban}"

    elif tipe == "persentase":
        persen = random.choice([10, 15, 20, 25, 30, 40, 50, 75])
        total  = random.choice([200, 400, 500, 800, 1000, 1200, 1500, 2000])
        jawaban = total * persen // 100
        soal = f"Berapa {persen}% dari {total}?"
        pembahasan = f"{persen}% × {total} = {persen}/100 × {total} = {jawaban}"

    else:  # rasio
        a, b = random.randint(2, 8), random.randint(2, 8)
        total = (a + b) * random.randint(5, 20)
        bagian_a = total * a // (a + b)
        soal = f"Dua orang berbagi uang Rp {total:,} dengan rasio {a}:{b}. Berapa bagian orang pertama?"
        jawaban = bagian_a
        pembahasan = f"Bagian pertama = {a}/({a}+{b}) × {total} = {a}/{a+b} × {total} = {jawaban}"

    # Buat opsi
    benar = jawaban
    if isinstance(benar, str) and "/" in str(benar):
        base = _fractions.Fraction(benar)
        opsi_vals = [benar]
        for delta in [_fractions.Fraction(1, 4), _fractions.Fraction(-1, 4),
                      _fractions.Fraction(1, 2), _fractions.Fraction(-1, 2)]:
            d = base + delta
            if d > 0 and d != base:
                s = str(d.numerator) if d.denominator == 1 else f"{d.numerator}/{d.denominator}"
                if s not in opsi_vals:
                    opsi_vals.append(s)
        opsi_vals = opsi_vals[:4]
    else:
        benar_int = int(benar) if isinstance(benar, (int, float)) else int(str(benar).replace(",", ""))
        deltas = random.sample([-5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6, 7, 8, -6, -7], 4)
        opsi_vals = [benar_int] + [benar_int + d for d in deltas[:3]]
        benar = benar_int

    random.shuffle(opsi_vals)
    huruf = ["A", "B", "C", "D"]
    opsi = [f"{huruf[i]}. {opsi_vals[i]}" for i in range(min(4, len(opsi_vals)))]
    jawaban_huruf = huruf[opsi_vals.index(benar)]

    return {
        "pertanyaan": soal,
        "opsi": opsi,
        "jawaban": jawaban_huruf,
        "jawaban_teks": str(benar),
        "kategori": "Matematika Dasar",
        "pembahasan": pembahasan,
        "skor_benar": 10,
        "sesi": "Kecerdasan",
    }


# ── Spasial / Mata Angin ──
_ARAH_8 = ["Utara", "Timur Laut", "Timur", "Tenggara",
           "Selatan", "Barat Daya", "Barat", "Barat Laut"]
_ARAH_LAWAN = {a: _ARAH_8[(i + 4) % 8] for i, a in enumerate(_ARAH_8)}
_PUTAR_CW   = {a: _ARAH_8[(i + 1) % 8] for i, a in enumerate(_ARAH_8)}
_PUTAR_CCW  = {a: _ARAH_8[(i - 1) % 8] for i, a in enumerate(_ARAH_8)}

def _putar(arah: str, derajat: int, searah_jarum: bool = True) -> str:
    langkah = derajat // 45
    current = arah
    for _ in range(langkah):
        current = _PUTAR_CW[current] if searah_jarum else _PUTAR_CCW[current]
    return current

def _soal_spasial() -> dict:
    tipe = random.choice([
        "lawan_arah", "putar_cw_45", "putar_cw_90", "putar_ccw_90",
        "denah_jarak", "denah_langkah", "mata_angin_antara",
    ])

    pembahasan = ""

    if tipe == "lawan_arah":
        arah = random.choice(_ARAH_8)
        jawaban_str = _ARAH_LAWAN[arah]
        soal = f"Seseorang menghadap {arah}. Jika ia berbalik 180°, ia kini menghadap ke ....?"
        pembahasan = f"Berlawanan dari {arah} adalah {jawaban_str}."

    elif tipe == "putar_cw_45":
        arah = random.choice(_ARAH_8)
        jawaban_str = _putar(arah, 45, True)
        soal = f"Seseorang menghadap {arah}, lalu berputar 45° searah jarum jam. Sekarang ia menghadap ke ....?"
        pembahasan = f"45° searah jarum jam dari {arah} = {jawaban_str}."

    elif tipe == "putar_cw_90":
        arah = random.choice(_ARAH_8)
        kali = random.choice([1, 2, 3])
        jawaban_str = _putar(arah, 90 * kali, True)
        soal = f"Menghadap {arah}, berputar {90*kali}° searah jarum jam. Menghadap ke ....?"
        pembahasan = f"{90*kali}° CW dari {arah} = {jawaban_str}."

    elif tipe == "putar_ccw_90":
        arah = random.choice(_ARAH_8)
        kali = random.choice([1, 2, 3])
        jawaban_str = _putar(arah, 90 * kali, False)
        soal = f"Menghadap {arah}, berputar {90*kali}° berlawanan jarum jam. Menghadap ke ....?"
        pembahasan = f"{90*kali}° CCW dari {arah} = {jawaban_str}."

    elif tipe == "denah_jarak":
        j1 = random.randint(3, 8)
        j2 = random.randint(3, 8)
        a1 = random.choice(["Utara", "Selatan"])
        a2 = random.choice(["Timur", "Barat"])
        jarak = round(math.sqrt(j1**2 + j2**2), 1)
        jawaban_str = str(jarak)
        soal = (f"Dari Pos A, Budi berjalan {j1} km ke {a1}, "
                f"lalu {j2} km ke {a2}. "
                f"Berapa km jarak lurus Budi dari Pos A?")
        pembahasan = f"Jarak = √({j1}² + {j2}²) = √{j1**2+j2**2} ≈ {jarak} km"

    elif tipe == "denah_langkah":
        a1 = random.choice(["Utara", "Selatan"])
        a2 = random.choice(["Timur", "Barat"])
        a3 = _ARAH_LAWAN[a1]
        j1, j2, j3 = random.randint(2,8), random.randint(2,8), random.randint(1,6)
        sisa_ns = j1 - j3 if a3 == a1 else j1 + j3  # net perpindahan
        # selalu hitung resultante sederhana
        jarak = round(math.sqrt(sisa_ns**2 + j2**2), 1)
        jawaban_str = str(jarak)
        soal = (f"Dari Titik X, Polisi berjalan {j1} km ke {a1}, "
                f"{j2} km ke {a2}, lalu {j3} km ke {a3}. "
                f"Berapa km jarak lurus ke Titik X?")
        pembahasan = f"Net {a1}-{a3}: {sisa_ns} km, Net {a2}: {j2} km → √({sisa_ns}²+{j2}²) = {jarak} km"

    else:  # mata_angin_antara
        arah = random.choice(["Utara", "Timur", "Selatan", "Barat"])
        arah2 = _PUTAR_CW[arah]  # 45 derajat
        jawaban_str = arah2
        soal = f"Arah yang berada di antara {arah} dan {_PUTAR_CW[arah2]} adalah ....?"
        pembahasan = f"Di antara {arah} dan {_PUTAR_CW[arah2]} adalah {arah2}."

    # Buat opsi pilihan
    if tipe in ("denah_jarak", "denah_langkah"):
        base = float(jawaban_str)
        pool = set()
        for d in [-1.5, -1.0, -0.5, 0.5, 1.0, 1.5, 2.0, -2.0]:
            v = round(base + d, 1)
            if v > 0 and str(v) != jawaban_str:
                pool.add(str(v))
        pilihan = [jawaban_str] + list(pool)[:3]
    else:
        pool = [a for a in _ARAH_8 if a != jawaban_str]
        random.shuffle(pool)
        pilihan = [jawaban_str] + pool[:3]

    random.shuffle(pilihan)
    huruf = ["A", "B", "C", "D"]
    opsi = [f"{huruf[i]}. {pilihan[i]}" for i in range(min(4, len(pilihan)))]
    jawaban_huruf = huruf[pilihan.index(jawaban_str)]

    return {
        "pertanyaan": soal,
        "opsi": opsi,
        "jawaban": jawaban_huruf,
        "jawaban_teks": jawaban_str,
        "kategori": "Spasial / Mata Angin",
        "pembahasan": pembahasan,
        "skor_benar": 10,
        "sesi": "Kecerdasan",
    }


_FALLBACK_KECERDASAN = {
    "pertanyaan": "Jika 3x + 7 = 22, berapakah nilai x?",
    "opsi": ["A. 3", "B. 4", "C. 5", "D. 6"],
    "jawaban": "C",
    "jawaban_teks": "5",
    "kategori": "Matematika Dasar",
    "pembahasan": "3x = 22 − 7 = 15, sehingga x = 15 ÷ 3 = 5.",
    "skor_benar": 10,
    "sesi": "Kecerdasan",
}

def generate_soal_kecerdasan(kategori: str = "acak") -> dict:
    roll = random.random()
    if roll < 0.45:
        return _soal_matematika()
    elif roll < 0.70:
        return _soal_spasial()

    # Groq: Verbal / Logika / Analogi / Wawasan
    groq_pool = ["Verbal dan Analogi", "Logika Deduktif", "Wawasan Kebangsaan", "Deret Angka"]
    selected  = random.choice(groq_pool)
    prompt = f"""Buat 1 soal psikotes Polri kategori {selected} tingkat menengah untuk tahun 2025.
HANYA JSON, tanpa markdown backtick:
{{"pertanyaan":"...","opsi":["A. ...","B. ...","C. ...","D. ..."],"jawaban":"huruf satu karakter","kategori":"{selected}","pembahasan":"penjelasan singkat cara menjawab"}}
Pastikan jawaban benar WAJIB ada di opsi. Jawaban hanya satu huruf A/B/C/D."""

    try:
        client = get_client()
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=400,
        )
        raw = resp.choices[0].message.content
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        data  = json.loads(match.group() if match else raw)
        data["skor_benar"] = 10
        data["sesi"] = "Kecerdasan"
        data["jawaban"] = str(data.get("jawaban", "A")).strip().upper()[0]
        data.setdefault("pembahasan", "Lihat kembali materi terkait.")
        data.setdefault("jawaban_teks", "")
        if "opsi" not in data or len(data["opsi"]) < 4:
            raise ValueError("opsi tidak lengkap")
        return data
    except Exception:
        return _FALLBACK_KECERDASAN.copy()


def nilai_jawaban_kecerdasan(jawaban_user: str, jawaban_benar: str) -> int:
    u = str(jawaban_user).strip().upper()
    b = str(jawaban_benar).strip().upper()
    return 10 if (u[0] == b[0]) else 0

def skor_sesi_kecerdasan(soal_list: list, jawaban: list) -> dict:
    detail = []
    benar_count = 0
    for soal, jwb in zip(soal_list, jawaban):
        if jwb is None:
            jwb = ""
        huruf_user  = str(jwb).split(".")[0].strip().upper()
        huruf_benar = str(soal.get("jawaban", "A")).strip().upper()
        is_benar = (huruf_user == huruf_benar) if huruf_user else False
        if is_benar:
            benar_count += 1

        # Cari teks jawaban benar dari opsi
        opsi = soal.get("opsi", [])
        teks_benar = next((o.split(". ", 1)[1] if ". " in o else o
                           for o in opsi if o.startswith(huruf_benar + ".")), soal.get("jawaban_teks", ""))
        teks_user  = next((o.split(". ", 1)[1] if ". " in o else o
                           for o in opsi if o.startswith(huruf_user + ".")), jwb)

        detail.append({
            "pertanyaan":    soal.get("pertanyaan", ""),
            "opsi":          opsi,
            "jawaban_user":  jwb,
            "jawaban_benar": huruf_benar,
            "teks_benar":    teks_benar,
            "teks_user":     teks_user,
            "benar":         is_benar,
            "kategori":      soal.get("kategori", "Kecerdasan"),
            "pembahasan":    soal.get("pembahasan", ""),
        })

    skor_100 = round(benar_count / SOAL_PER_SESI * 100)
    return {"skor_100": skor_100, "benar": benar_count, "detail": detail}


# ══════════════════════════════════════════════
# 3. KEPRIBADIAN — Likert 5 Skala Statis
# ══════════════════════════════════════════════
_FALLBACK_KEPRIBADIAN = {
    "pernyataan": "Saya selalu melaporkan pelanggaran yang saya saksikan meskipun pelakunya adalah rekan dekat.",
    "arah": "positif",
    "kategori": "Kepribadian",
    "sesi": "Kepribadian",
}

def generate_soal_kepribadian() -> dict:
    prompt = """Buat 1 pernyataan tes kepribadian Polri untuk skala Likert 5.
Tema: integritas, kedisiplinan, loyalitas, profesionalisme, atau etika kepolisian.
Tentukan arah: POSITIF = setuju berarti karakter baik; NEGATIF = setuju berarti karakter buruk.
HANYA JSON tanpa markdown backtick:
{"pernyataan":"...","arah":"positif","kategori":"Kepribadian"}
Arah HANYA boleh: "positif" atau "negatif"."""

    try:
        client = get_client()
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.85,
            max_tokens=200,
        )
        raw   = resp.choices[0].message.content
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        data  = json.loads(match.group() if match else raw)
        if "pernyataan" not in data:
            raise ValueError("pernyataan missing")
        arah = str(data.get("arah", "positif")).lower().strip()
        if arah not in ("positif", "negatif"):
            arah = "positif"
        data["arah"] = arah
        data["kategori"] = "Kepribadian"
        data["sesi"] = "Kepribadian"
        return data
    except Exception:
        return _FALLBACK_KEPRIBADIAN.copy()


def nilai_jawaban_kepribadian(jawaban_user: str, arah: str) -> int:
    """Skor 1-5 berdasarkan jawaban Likert dan arah pernyataan."""
    key = str(jawaban_user).strip().upper()[0] if jawaban_user else "C"
    if arah == "negatif":
        return LIKERT_SKOR_NEGATIF.get(key, 3)
    return LIKERT_SKOR_POSITIF.get(key, 3)

def skor_sesi_kepribadian(soal_list: list, jawaban: list) -> dict:
    """
    Skor 0-100: total poin Likert / (soal * 5) * 100
    """
    detail       = []
    total_poin   = 0
    maks_poin    = SOAL_PER_SESI * 5

    for soal, jwb in zip(soal_list, jawaban):
        if jwb is None:
            jwb = "C"
        huruf = str(jwb).strip().upper()[0]
        arah  = soal.get("arah", "positif")
        poin  = nilai_jawaban_kepribadian(huruf, arah)
        total_poin += poin

        # Label pilihan
        label_map = {"A": "Sangat Setuju", "B": "Setuju", "C": "Ragu-ragu",
                     "D": "Tidak Setuju", "E": "Sangat Tidak Setuju"}

        # Jawaban ideal
        ideal_huruf = "A" if arah == "positif" else "E"
        pembahasan = (
            f"Pernyataan ini bersifat {'POSITIF' if arah=='positif' else 'NEGATIF'}. "
            f"Jawaban ideal adalah '{label_map[ideal_huruf]}' untuk mencerminkan profil polisi yang baik."
        )

        detail.append({
            "pernyataan":    soal.get("pernyataan", ""),
            "jawaban_user":  huruf,
            "label_user":    label_map.get(huruf, huruf),
            "arah":          arah,
            "poin":          poin,
            "poin_maks":     5,
            "pembahasan":    pembahasan,
        })

    skor_100 = round(total_poin / maks_poin * 100)
    return {
        "skor_100":   skor_100,
        "total_poin": total_poin,
        "maks_poin":  maks_poin,
        "rata_rata":  round(total_poin / SOAL_PER_SESI, 2),
        "detail":     detail,
    }


# ══════════════════════════════════════════════
# 4. KECERMATAN — Karakter Hilang (format 2025)
# ══════════════════════════════════════════════
_KUNCI_KOLOM = [
    {"nama": "KOLOM 1", "kunci": list("ZPTXQ")},
    {"nama": "KOLOM 2", "kunci": list("YLKJC")},
    {"nama": "KOLOM 3", "kunci": list("OSRVU")},
    {"nama": "KOLOM 4", "kunci": list("BGFHI")},
    {"nama": "KOLOM 5", "kunci": list("SNAWM")},
    {"nama": "KOLOM 6", "kunci": list("DERBP")},
    {"nama": "KOLOM 7", "kunci": list("MNCQW")},
    {"nama": "KOLOM 8", "kunci": list("IFTVA")},
]

def generate_kecermatan() -> dict:
    """
    Tampilkan 4 dari 5 karakter kunci (tanpa tanda tanya).
    User harus memilih karakter yang hilang dari opsi yang disediakan.
    Auto-submit via button klik.
    """
    kolom  = random.choice(_KUNCI_KOLOM)
    kunci  = kolom["kunci"].copy()

    hilang   = random.choice(kunci)
    tampilan = [k for k in kunci if k != hilang]
    random.shuffle(tampilan)

    opsi = kunci.copy()
    random.shuffle(opsi)

    return {
        "nama_kolom":    kolom["nama"],
        "kunci":         kunci,
        "tampilan":      " ".join(tampilan),
        "jawaban":       hilang,
        "opsi":          opsi,
        "timestamp_mulai": time.time(),
        "sesi":          "Kecermatan",
    }


def catat_waktu_jawab(soal: dict) -> float:
    return round(time.time() - soal.get("timestamp_mulai", time.time()), 3)


def hitung_ketahanan(waktu_per_soal: list) -> dict:
    n = len(waktu_per_soal)
    if n == 0:
        return {"jumlah_soal": 0, "rata_rata_detik": 0.0, "std_dev": 0.0,
                "cv_persen": 0.0, "skor_ketahanan": 0, "kategori": "Tidak ada data"}
    rata = sum(waktu_per_soal) / n
    variance = sum((t - rata) ** 2 for t in waktu_per_soal) / n
    std  = math.sqrt(variance)
    cv   = (std / rata * 100) if rata > 0 else 0.0

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
        "jumlah_soal":      n,
        "rata_rata_detik":  round(rata, 3),
        "std_dev":          round(std, 3),
        "cv_persen":        round(cv, 2),
        "skor_ketahanan":   min(skor, 100),
        "kategori":         kategori,
    }


def nilai_jawaban_kecermatan(jawaban_user: str, jawaban_benar: str) -> int:
    return 1 if str(jawaban_user).strip().upper() == str(jawaban_benar).strip().upper() else 0

def skor_sesi_kecermatan(soal_list: list, jawaban: list, waktu_list: list) -> dict:
    detail      = []
    benar_count = 0

    for i, (soal, jwb) in enumerate(zip(soal_list, jawaban)):
        if jwb is None:
            jwb = ""
        is_benar = (str(jwb).strip().upper() == str(soal.get("jawaban", "")).strip().upper())
        if is_benar:
            benar_count += 1

        waktu = waktu_list[i] if i < len(waktu_list) else None
        detail.append({
            "nama_kolom":    soal.get("nama_kolom", ""),
            "kunci":         soal.get("kunci", []),
            "tampilan":      soal.get("tampilan", ""),
            "jawaban_user":  str(jwb).strip().upper(),
            "jawaban_benar": soal.get("jawaban", ""),
            "benar":         is_benar,
            "waktu_detik":   waktu,
            "pembahasan":    f"Kunci {soal.get('nama_kolom','')} adalah {soal.get('kunci',[])}. Karakter hilang: '{soal.get('jawaban','')}'.",
        })

    skor_100 = round(benar_count / SOAL_PER_SESI * 100)
    waktu_valid = [w for w in waktu_list if w is not None]
    ketahanan   = hitung_ketahanan(waktu_valid)

    return {
        "skor_100":  skor_100,
        "benar":     benar_count,
        "ketahanan": ketahanan,
        "detail":    detail,
    }


# ══════════════════════════════════════════════
# DISPATCHER GENERATE
# ══════════════════════════════════════════════
def generate_soal(sesi: str) -> dict:
    if sesi == "Pass Hand":
        return generate_pass_hand()
    elif sesi == "Kecerdasan":
        return generate_soal_kecerdasan()
    elif sesi == "Kepribadian":
        return generate_soal_kepribadian()
    elif sesi == "Kecermatan":
        return generate_kecermatan()
    return generate_soal_kecerdasan()


# ══════════════════════════════════════════════
# REKAP MARATON — SKOR AKHIR + STATUS MS/TMS
# ══════════════════════════════════════════════
def rekap_maraton(hasil_per_sesi: dict) -> dict:
    """
    hasil_per_sesi: {"Pass Hand": skor_100, "Kecerdasan": skor_100, ...}
    Return: rata-rata, status MS/TMS, detail
    """
    skor_list = [v for v in hasil_per_sesi.values() if isinstance(v, (int, float))]
    rata      = round(sum(skor_list) / len(skor_list)) if skor_list else 0
    status    = "MS" if rata >= PASSING_GRADE else "TMS"
    return {
        "skor_per_sesi": hasil_per_sesi,
        "rata_rata":     rata,
        "status":        status,
        "passing_grade": PASSING_GRADE,
        "lulus":         status == "MS",
    }


# ══════════════════════════════════════════════
# HELPER APS (tetap ada untuk kompatibilitas)
# ══════════════════════════════════════════════
def hitung_aps(jumlah_klik: int, durasi_detik: float) -> dict:
    aps = round(jumlah_klik / max(durasi_detik, 0.001), 2)
    if aps >= 3.0:   kategori, deskripsi = "Sangat Baik", "Koordinasi sangat responsif."
    elif aps >= 2.0: kategori, deskripsi = "Baik",        "Koordinasi di atas rata-rata."
    elif aps >= 1.0: kategori, deskripsi = "Cukup",       "Koordinasi rata-rata."
    else:             kategori, deskripsi = "Kurang",      "Perlu latihan koordinasi."
    return {"jumlah_klik": jumlah_klik, "durasi_detik": round(durasi_detik, 2),
            "aps": aps, "kategori": kategori, "deskripsi": deskripsi}

def posisi_target_acak(area_width: int, area_height: int, target_size: int) -> dict:
    x = random.randint(0, max(0, area_width - target_size))
    y = random.randint(0, max(0, area_height - target_size))
    return {"x": x, "y": y}
