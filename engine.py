import streamlit as st
from groq import Groq
import json
import re
import random

# Inisialisasi Client
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def generate_soal_ai(sesi="Umum"):
    # Logika untuk Sesi Kepribadian (Scoring 1-5)
    if sesi == "Kepribadian":
        prompt = """
        Buat 1 soal tes kepribadian Polri. Berikan 4 pilihan jawaban. 
        Tiap pilihan HARUS punya bobot skor unik antara 1 sampai 5.
        Berikan HANYA JSON: {"pertanyaan": "...", "opsi": ["A", "B", "C", "D"], "skor": [5, 4, 3, 2]}
        """
    else:
        # Sesi Kecerdasan / Wawasan Kebangsaan
        kategori_pilihan = ["Kecerdasan", "Wawasan Kebangsaan"]
        kat = random.choice(kategori_pilihan)
        prompt = f"Buat 1 soal psikotes Polri {kat}. Format JSON: {{\"pertanyaan\": \"...\", \"opsi\": [\"A\", \"B\", \"C\", \"D\"], \"jawaban\": \"...\", \"kategori\": \"{kat}\"}}. Berikan HANYA JSON."

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        raw = completion.choices[0].message.content
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        return json.loads(match.group()) if match else json.loads(raw)
    except Exception as e:
        return {
            "pertanyaan": "Jika Anda melihat rekan kerja berbuat curang, apa yang Anda lakukan?",
            "opsi": ["Melaporkan", "Menegur", "Diam saja", "Ikut-ikutan"],
            "skor": [5, 4, 2, 1],
            "kategori": "Kepribadian"
        }

def generate_kecermatan():
    # Menggunakan alfabet dan angka agar lebih variatif
    pool = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    kunci = random.sample(pool, 5) 
    
    hilang = random.choice(kunci)
    # Karakter yang ditampilkan di soal (4 karakter)
    soal_tampilan = [x for x in kunci if x != hilang]
    random.shuffle(soal_tampilan)
    
    return {
        "kunci": kunci,         
        "pertanyaan": " ".join(soal_tampilan), 
        "jawaban": hilang,       
        "opsi": kunci            
    }
