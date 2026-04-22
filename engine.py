"""
engine.py — CAT Psikotes Polri
Berisi semua logika generasi soal & kalkulasi skor untuk 4 sesi:
  1. Pass Hand  (ketangkasan — APS)
  2. Kecerdasan (Groq/Llama, benar +5 salah 0)
  3. Kecermatan (karakter hilang + Ketahanan)
  4. Kepribadian (Groq/Llama, skor unik per opsi)
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
# 1. PASS HAND
# ══════════════════════════════════════════════

def generate_pass_hand(durasi_detik: int = 30) -> dict:
    """
    Hasilkan konfigurasi sesi Pass Hand.

    Mekanisme (dihandle di UI, bukan di sini):
      - Tampilkan target (lingkaran/kotak) di posisi acak setiap kali diklik.
      - Hitung jumlah klik valid selama `durasi_detik`.
      - Panggil hitung_aps() di akhir sesi untuk mendapat skor APS.

    Return:
        {
            "durasi_detik": int,
            "instruksi": str,
            "target_size_px": int,       # ukuran target di layar
            "area_width": int,           # lebar area bermain (px logical)
            "area_height": int,
        }
    """
    return {
        "durasi_detik": durasi_detik,
        "instruksi": (
            "Klik target yang muncul secepat mungkin. "
            "Target akan berpindah posisi setiap kali Anda klik. "
            f"Sesi berlangsung selama {durasi_detik} detik."
        ),
        "target_size_px": 60,
        "area_width": 600,
        "area_height": 400,
    }


def hitung_aps(jumlah_klik: int, durasi_detik: float) -> dict:
    """
    Kalkulasi Aksi Per Detik (APS) dari Pass Hand.

    Args:
        jumlah_klik: total klik valid selama sesi
        durasi_detik: durasi aktual sesi (bisa lebih presisi dari target)

    Return:
        {
            "jumlah_klik": int,
            "durasi_detik": float,
            "aps": float,           # dibulatkan 2 desimal
            "kategori": str,        # "Sangat Baik" / "Baik" / "Cukup" / "Kurang"
            "deskripsi": str,
        }
    """
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
    """
    Generate posisi acak untuk target Pass Hand agar tidak keluar area.

    Return: {"x": int, "y": int}  (top-left corner dalam px)
    """
    x = random.randint(0, max(0, area_width - target_size))
    y = random.randint(0, max(0, area_height - target_size))
    return {"x": x, "y": y}


# ══════════════════════════════════════════════
# 2. KECERDASAN (Groq)
# ══════════════════════════════════════════════

_FALLBACK_KECERDASAN = {
    "pertanyaan": "Jika 3x + 7 = 22, berapakah nilai x?",
    "opsi": ["A. 3", "B. 4", "C. 5", "D. 6", "E. 7"],
    "jawaban": "C",
    "kategori": "Kecerdasan",
    "skor_benar": 5,
    "skor_salah": 0,
}


def generate_soal_kecerdasan(kategori: str = "acak") -> dict:
    """
    Hasilkan 1 soal Kecerdasan via Groq (Llama 3).

    Args:
        kategori: "Numerik" | "Verbal" | "Logika" | "Wawasan Kebangsaan" | "acak"

    Return:
        {
            "pertanyaan": str,
            "opsi": ["A. ...", "B. ...", "C. ...", "D. ...", "E. ..."],
            "jawaban": "A"|"B"|"C"|"D"|"E",
            "kategori": str,
            "skor_benar": 5,
            "skor_salah": 0,
        }
    """
    pilihan = ["Numerik", "Verbal", "Logika", "Wawasan Kebangsaan"]
    if kategori == "acak":
        kategori = random.choice(pilihan)

    prompt = f"""Buat 1 soal psikotes Polri kategori {kategori} (tingkat menengah).
Berikan HANYA JSON tanpa teks lain, tanpa markdown:
{{
  "pertanyaan": "teks soal",
  "opsi": ["A. pilihan1", "B. pilihan2", "C. pilihan3", "D. pilihan4", "E. pilihan5"],
  "jawaban": "huruf jawaban benar (A/B/C/D/E)",
  "kategori": "{kategori}"
}}
Pastikan jawaban benar PASTI ada di dalam opsi."""

    try:
        client = get_client()
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        raw = resp.choices[0].message.content
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        data = json.loads(match.group()) if match else json.loads(raw)

        # Normalisasi & validasi
        data["skor_benar"] = 5
        data["skor_salah"] = 0
        data["jawaban"] = str(data.get("jawaban", "A")).strip().upper()[0]
        if "opsi" not in data or len(data["opsi"]) < 4:
            raise ValueError("opsi tidak lengkap")
        return data

    except Exception:
        return _FALLBACK_KECERDASAN.copy()


def nilai_jawaban_kecerdasan(jawaban_user: str, jawaban_benar: str) -> int:
    """Return 5 jika benar, 0 jika salah."""
    return 5 if str(jawaban_user).strip().upper()[0] == str(jawaban_benar).strip().upper()[0] else 0


# ══════════════════════════════════════════════
# 3. KECERMATAN (Karakter Hilang + Ketahanan)
# ══════════════════════════════════════════════

def generate_kecermatan() -> dict:
    """
    Buat 1 soal Kecermatan: karakter hilang dari kunci 5-karakter.

    Logika:
      - Ambil 5 karakter unik acak dari pool alfanumerik.
      - Pilih 1 sebagai yang 'hilang'.
      - Soal menampilkan 4 karakter sisanya (diacak urutannya).
      - Opsi = semua 5 karakter kunci (diacak).

    Return:
        {
            "kunci": ["X", "3", "A", "7", "M"],   # 5 karakter lengkap
            "tampilan": "3 M A 7",                  # 4 karakter (tanpa yang hilang), diacak
            "jawaban": "X",
            "opsi": ["A", "3", "7", "M", "X"],     # 5 opsi (diacak)
            "timestamp_mulai": float,               # time.time() saat soal dibuat
        }
    """
    pool = list("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    kunci = random.sample(pool, 5)

    hilang = random.choice(kunci)
    tampilan = [k for k in kunci if k != hilang]
    random.shuffle(tampilan)

    opsi = kunci.copy()
    random.shuffle(opsi)

    return {
        "kunci": kunci,
        "tampilan": " ".join(tampilan),
        "jawaban": hilang,
        "opsi": opsi,
        "timestamp_mulai": time.time(),
    }


def catat_waktu_jawab(soal: dict) -> float:
    """
    Hitung waktu (detik) sejak soal dibuat sampai fungsi ini dipanggil.
    Panggil ini tepat setelah user memilih jawaban.

    Return: durasi_detik (float)
    """
    return round(time.time() - soal["timestamp_mulai"], 3)


def hitung_ketahanan(waktu_per_soal: list[float]) -> dict:
    """
    Hitung skor Ketahanan dari daftar waktu jawab per soal.

    Ketahanan = stabilitas kecepatan jawab: makin kecil koefisien variasi (CV),
    makin stabil, makin tinggi skor ketahanan.

    CV = standar_deviasi / rata_rata * 100

    Skor ketahanan (0–100):
      CV < 20%  → 90–100 (sangat stabil)
      CV 20–40% → 70–89
      CV 40–60% → 50–69
      CV > 60%  → < 50

    Args:
        waktu_per_soal: list durasi (detik) tiap soal dijawab

    Return:
        {
            "jumlah_soal": int,
            "rata_rata_detik": float,
            "std_dev": float,
            "cv_persen": float,
            "skor_ketahanan": int,      # 0–100
            "kategori": str,
        }
    """
    n = len(waktu_per_soal)
    if n == 0:
        return {
            "jumlah_soal": 0,
            "rata_rata_detik": 0.0,
            "std_dev": 0.0,
            "cv_persen": 0.0,
            "skor_ketahanan": 0,
            "kategori": "Tidak ada data",
        }

    rata = sum(waktu_per_soal) / n
    variance = sum((t - rata) ** 2 for t in waktu_per_soal) / n
    std = math.sqrt(variance)
    cv = (std / rata * 100) if rata > 0 else 0.0

    if cv < 20:
        skor = int(90 + (20 - cv) / 20 * 10)   # 90–100
        kategori = "Sangat Stabil"
    elif cv < 40:
        skor = int(70 + (40 - cv) / 20 * 19)   # 70–89
        kategori = "Stabil"
    elif cv < 60:
        skor = int(50 + (60 - cv) / 20 * 19)   # 50–69
        kategori = "Cukup Stabil"
    else:
        skor = max(0, int(50 - (cv - 60) / 40 * 50))  # 0–49
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
    """Return 1 jika benar, 0 jika salah (skor kecermatan dihitung per soal)."""
    return 1 if str(jawaban_user).strip().upper() == str(jawaban_benar).strip().upper() else 0


# ══════════════════════════════════════════════
# 4. KEPRIBADIAN (Groq)
# ══════════════════════════════════════════════

_FALLBACK_KEPRIBADIAN = {
    "pertanyaan": "Jika Anda melihat rekan kerja berbuat curang, apa yang Anda lakukan?",
    "opsi": ["A. Melaporkan langsung ke atasan", "B. Menegur secara personal", "C. Diam dan mengamati lebih lanjut", "D. Ikut-ikutan saja"],
    "skor": {"A": 5, "B": 4, "C": 2, "D": 1},
    "kategori": "Kepribadian",
}


def generate_soal_kepribadian() -> dict:
    """
    Hasilkan 1 soal Kepribadian via Groq.
    Tiap opsi punya skor unik (dari set {1,2,3,4,5}, pilih 4).

    Return:
        {
            "pertanyaan": str,
            "opsi": ["A. ...", "B. ...", "C. ...", "D. ..."],
            "skor": {"A": int, "B": int, "C": int, "D": int},  # nilai unik 1–5
            "kategori": "Kepribadian",
        }
    """
    prompt = """Buat 1 soal tes kepribadian Polri yang mengukur integritas/kedisiplinan.
4 pilihan jawaban, masing-masing punya bobot skor BERBEDA dari set {1, 2, 3, 4, 5} (tidak boleh sama).
Berikan HANYA JSON tanpa teks lain, tanpa markdown:
{
  "pertanyaan": "teks soal",
  "opsi": ["A. pilihan1", "B. pilihan2", "C. pilihan3", "D. pilihan4"],
  "skor": {"A": 5, "B": 4, "C": 2, "D": 1},
  "kategori": "Kepribadian"
}
Urutan skor boleh berbeda, tapi tiap huruf HARUS punya nilai unik dari set tersebut."""

    try:
        client = get_client()
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
        )
        raw = resp.choices[0].message.content
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        data = json.loads(match.group()) if match else json.loads(raw)

        # Validasi: pastikan skor adalah dict dengan 4 kunci unik
        skor = data.get("skor", {})
        if not isinstance(skor, dict) or len(set(skor.values())) < 4:
            # Assign ulang skor acak jika tidak valid
            huruf = ["A", "B", "C", "D"]
            nilai = random.sample([1, 2, 3, 4, 5], 4)
            data["skor"] = dict(zip(huruf, nilai))

        data["kategori"] = "Kepribadian"
        if "opsi" not in data or len(data["opsi"]) < 4:
            raise ValueError("opsi tidak lengkap")
        return data

    except Exception:
        return _FALLBACK_KEPRIBADIAN.copy()


def nilai_jawaban_kepribadian(jawaban_user: str, skor_opsi: dict) -> int:
    """
    Return skor kepribadian berdasarkan pilihan user.

    Args:
        jawaban_user: huruf pilihan ("A", "B", "C", atau "D")
        skor_opsi: dict skor dari soal, mis. {"A": 5, "B": 4, "C": 2, "D": 1}

    Return: int skor (1–5), default 1 jika tidak ditemukan
    """
    key = str(jawaban_user).strip().upper()[0]
    return skor_opsi.get(key, 1)


# ══════════════════════════════════════════════
# DISPATCHER — generate_soal_ai (backward compat)
# ══════════════════════════════════════════════

def generate_soal_ai(sesi: str = "Kecerdasan") -> dict:
    """
    Dispatcher utama. Panggil fungsi yang sesuai berdasarkan nama sesi.

    Args:
        sesi: "Kecerdasan" | "Kepribadian" | "Kecermatan" | "Pass Hand"

    Return: dict soal sesuai sesi
    """
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

def rekap_sesi(
    pass_hand: dict | None = None,       # output hitung_aps()
    kecerdasan: dict | None = None,      # {"benar": int, "salah": int, "total": int}
    kecermatan: dict | None = None,      # {"benar": int, "total": int, "ketahanan": dict}
    kepribadian: dict | None = None,     # {"total_skor": int, "jumlah_soal": int}
) -> dict:
    """
    Rangkum hasil semua sesi menjadi satu laporan.

    Return:
        {
            "pass_hand":   {...} | None,
            "kecerdasan":  {"skor": int, "benar": int, ...} | None,
            "kecermatan":  {"skor_akurasi": int, "ketahanan": {...}} | None,
            "kepribadian": {"skor_total": int, "rata_rata": float} | None,
            "catatan": str,
        }
    """
    hasil = {}

    if pass_hand:
        hasil["pass_hand"] = pass_hand

    if kecerdasan:
        total = max(kecerdasan.get("total", 1), 1)
        benar = kecerdasan.get("benar", 0)
        hasil["kecerdasan"] = {
            "skor": benar * 5,
            "benar": benar,
            "salah": kecerdasan.get("salah", total - benar),
            "total_soal": total,
            "akurasi_persen": round(benar / total * 100, 1),
        }

    if kecermatan:
        total = max(kecermatan.get("total", 1), 1)
        benar = kecermatan.get("benar", 0)
        hasil["kecermatan"] = {
            "skor_akurasi": benar,
            "total_soal": total,
            "akurasi_persen": round(benar / total * 100, 1),
            "ketahanan": kecermatan.get("ketahanan", {}),
        }

    if kepribadian:
        jml = max(kepribadian.get("jumlah_soal", 1), 1)
        total_skor = kepribadian.get("total_skor", 0)
        hasil["kepribadian"] = {
            "skor_total": total_skor,
            "jumlah_soal": jml,
            "rata_rata": round(total_skor / jml, 2),
            "skor_maks_mungkin": jml * 5,
        }

    hasil["catatan"] = "Hasil bersifat simulatif dan tidak menggantikan tes resmi Polri."
    return hasil
