import streamlit as st
from supabase import create_client, Client

# Koneksi (Pastiin di Secrets Streamlit udah bener isinya)
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(URL, KEY)

# --- FUNGSI UNTUK USER ---

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

# --- FUNGSI UNTUK ADMIN (Yang bikin error tadi) ---

def list_all_users():
    # Narik semua data dari tabel profiles
    return supabase.table("profiles").select("*").execute()

def activate_premium(user_id):
    # Update kolom is_premium jadi True buat ID tertentu
    return supabase.table("profiles").update({"is_premium": True}).eq("id", user_id).execute()
