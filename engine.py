import streamlit as st
from groq import Groq
import json

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def generate_soal_ai(kategori="Kecerdasan"):
    prompt = f"""
    Buat 1 soal psikotes Polri kategori {kategori} dalam format JSON.
    Format harus: {{"pertanyaan": "...", "opsi": ["A", "B", "C", "D"], "jawaban": "..."}}
    Berikan hanya JSON saja tanpa penjelasan.
    """
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return json.loads(completion.choices[0].message.content)
    
