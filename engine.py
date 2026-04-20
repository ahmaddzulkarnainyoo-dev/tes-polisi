import streamlit as st
from groq import Groq
import json
import re

# Inisialisasi Client Groq menggunakan secrets
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("Konfigurasi GROQ_API_KEY tidak ditemukan di Secrets!")

def generate_soal_ai(kategori="Kecerdasan"):
    """
    Fungsi untuk generate soal psikotes secara otomatis menggunakan Llama 3.
    """
    prompt = f"""
    Buatlah 1 soal psikotes Polri untuk kategori {kategori}.
    Berikan respon HANYA dalam format JSON mentah seperti contoh ini:
    {{
        "pertanyaan": "Isi soal di sini",
        "opsi": ["Pilihan A", "Pilihan B", "Pilihan C", "Pilihan D"],
        "jawaban": "Pilihan yang benar (harus sama persis dengan salah satu di opsi)",
        "kategori": "{kategori}"
    }}
    Pastikan soal berkualitas tinggi dan menantang.
    """
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an expert psychometrician for police recruitment."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        # Ambil teks respon
        raw_response = completion.choices[0].message.content
        
        # Bersihkan jika ada teks tambahan di luar JSON (pake regex biar aman)
        json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        else:
            return json.loads(raw_response)
            
    except Exception as e:
        st.error(f"Gagal generate soal: {str(e)}")
        # Fallback soal manual jika AI gagal biar web gak crash
        return {
            "pertanyaan": "Mobil : Bensin = Manusia : ....",
            "opsi": ["Sepatu", "Makanan", "Jalan", "Oksigen"],
            "jawaban": "Makanan",
            "kategori": "Kecerdasan"
        }

def generate_psychogram(skor_data):
    """
    Fungsi untuk membuat analisis naratif hasil tes (Optional).
    """
    # Logika analisis AI bisa ditaruh di sini nanti
    pass
