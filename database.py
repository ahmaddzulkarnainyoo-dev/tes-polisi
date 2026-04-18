# database.py
import os
from supabase import create_client, Client

# Ambil dari environment variables (keamanan nomor 1!)
URL = os.environ.get("SUPABASE_URL")
KEY = os.environ.get("sb_publishable_SUaYNqk-K3Y-T8YDM9BEJw_6dlMXh1G")
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
