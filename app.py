import streamlit as st
from timer import start_countdown # Asumsi fungsi di timer.py lo
from engine import generate_psychogram
from database import supabase

# Sidebar Navigasi
st.sidebar.title("🛡️ Psychotech Polri")
page = st.sidebar.radio("Navigasi", ["Home", "Mulai Simulasi", "Dashboard Admin"])

if page == "Home":
    st.markdown("# Selamat Datang di Psychotech")
    st.write("Persiapkan dirimu untuk seleksi Polri dengan simulasi akurat.")
    
elif page == "Mulai Simulasi":
    # Panggil fungsi simulasi lo di sini
    # Jangan lupa panggil timer.py pas tes dimulai
    pass

elif page == "Dashboard Admin":
    # Import admin logic
    import admin
    admin.show_admin_page()

# Load Data Soal
def load_data():
    with open('soal.json', 'r') as f:
        return json.load(f)

def main():
    st.set_page_config(page_title="Psychotech - Prep Polri", layout="centered")
    
    
    st.markdown("""
        <style>
        .main { background-color: #f5f7f9; }
        .stButton>button { width: 100%; border-radius: 20px; height: 3em; background-color: #007bff; color: white; }
        </style>
    """, unsafe_allow_html=True)

    st.title("🛡️ Simulasi Psikotes Polri")
    st.write("Uji kesiapan mental dan intelegensimu di sini.")

    data_soal = load_data()
    score = 0
    responses = {}

    with st.form("test_form"):
        for soal in data_soal:
            st.subheader(f"Soal {soal['id']}")
            st.write(soal['pertanyaan'])
            responses[soal['id']] = st.radio("Pilih jawaban:", soal['opsi'], key=soal['id'])
            st.divider()
        
        submitted = st.form_submit_button("Selesaikan Tes")
        
        if submitted:
            for soal in data_soal:
                if responses[soal['id']] == soal['jawaban']:
                    score += soal['poin']
            
            st.success(f"Tes Selesai! Skor Total Anda: {score}")
            if score >= 70:
                st.balloons()
                st.markdown("### Status: **MEMENUHI SYARAT (MS)**")
            else:
                st.error("Status: TIDAK MEMENUHI SYARAT (TMS)")

if __name__ == "__main__":
    main()
