import streamlit as st
from supabase import create_client, Client

# Panggil "kunci" dari Secrets Streamlit Cloud
# Nama di dalam kurung harus SAMA PERSIS dengan yang di dashboard Secrets
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]

# Bikin koneksi
supabase: Client = create_client(URL, KEY)

def get_user_profile(user_id):
    return supabase.table("profiles").select("*").eq("id", user_id).execute()

def save_test_result(user_id, category, score, psychogram):
    data = {
        "user_id": user_id,
        "category": category,
        "score": score,
        "psychogram_data": psychogram
    }
    return supabase.table("test_results").insert(data).execute()
