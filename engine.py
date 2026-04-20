import streamlit as st
from groq import Groq
import json
import re
import random

# Inisialisasi Client
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def generate_soal_ai():
    # Daftar kategori biar soalnya acak terus
    kategori_pilihan = ["Kecerdasan", "Kepribadian", "Wawasan Kebangsaan"]
    kat = random.choice(kategori_pilihan)
    
    prompt = f"Buat 1 soal psikotes Polri {kat}. Format JSON: {{\"pertanyaan\": \"...\", \"opsi\": [\"A\", \"B\", \"C\", \"D\"], \"jawaban\": \"...\"}}. Berikan HANYA JSON."
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        raw = completion.choices[0].message.content
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        return json.loads(match.group()) if match else json.loads(raw)
    except Exception as e:
        # Fallback kalau AI lagi lemot biar web nggak crash
        return {
            "pertanyaan": "Contoh: 1, 3, 5, ...",
            "opsi": ["6", "7", "8", "9"],
            "jawaban": "7"
        }
