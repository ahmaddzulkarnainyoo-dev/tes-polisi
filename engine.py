import streamlit as st
from groq import Groq
import json
import re

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def generate_soal_ai(kategori):
    prompt = f"Buat 1 soal psikotes Polri {kategori}. JSON format: {{\"pertanyaan\": \"...\", \"opsi\": [\"A\", \"B\", \"C\", \"D\"], \"jawaban\": \"...\"}}. Berikan JSON saja."
    
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    
    raw = completion.choices[0].message.content
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    return json.loads(match.group()) if match else json.loads(raw)
