import streamlit as st
from groq import Groq
import json
import re
import random

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def generate_soal_ai():
    # List kategori biar soalnya acak (Random)
    kategori_list = ["Kecerdasan", "Kepribadian", "Wawasan Kebangsaan"]
    kat = random.choice(kategori_list)
    
    prompt = f"""
    Buat 1 soal psikotes Polri kategori {kat}. 
    Format JSON: {{"pertanyaan": "...", "opsi": ["A", "B", "C", "D"], "jawaban": "..."}}.
    Berikan HANYA JSON.
    """
    
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    
    raw = completion.choices[0].message.content
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    return json.loads(match.group()) if match else json.loads(raw)
