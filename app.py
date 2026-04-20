import streamlit as st
import json
from timer import start_countdown
from engine import generate_psychogram
from database import supabase

# --- BIKIN MENU NAVIGASI DULU DI SINI ---
st.sidebar.title("🛡️ Psikologi Polri")
menu = st.sidebar.radio("Navigasi", ["Home", "Mulai Simulasi", "Dashboard Admin"])

# --- CSS CUSTOM ---
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background-color: #f8f9fa;
    }

    /* Hero Section */
    .hero-container {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 50px 20px;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    }

    /* Card Navigation */
    .nav-card {
        background: white;
        padding: 30px;
        border-radius: 15px;
        border-bottom: 5px solid #3b82f6;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
        text-align: center;
        cursor: pointer;
        height: 250px;
    }

    .nav-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 15px 30px rgba(0,0,0,0.1);
        border-bottom: 5px solid #1e3a8a;
    }

    .card-icon {
        font-size: 50px;
        margin-bottom: 15px;
    }

    .card-title {
        color: #1e3a8a;
        font-weight: bold;
        font-size: 20px;
    }

    .card-desc {
        color: #6b7280;
        font-size: 14px;
        margin-top: 10px;
    }

    /* Footer */
    .footer {
        text-align: center;
        padding: 20px;
        color: #9ca3af;
        font-size: 12px;
        margin-top: 50px;
    }
    </style>
""", unsafe_allow_html=True)
def show_simulation():
    st.markdown('<div class="hero-container"><h1>📝 Simulasi Psikotes</h1></div>', unsafe_allow_html=True)
    
    # 1. Buka file JSON lo
    try:
        with open('soal.json', 'r') as f:
            data_soal = json.load(f)
    except FileNotFoundError:
        st.error("Waduh bro, file soal.json nggak ketemu di folder!")
        return

    responses = {}
    
    # 2. Tampilin Soal di dalam Form
    with st.form("test_form"):
        for soal in data_soal:
            with st.container():
                st.markdown(f'<div class="soal-card">', unsafe_allow_html=True)
                st.subheader(f"Soal {soal['id']} - {soal.get('kategori', 'Umum')}")
                
                if soal.get('image_url'):
                    st.image(soal['image_url'], use_container_width=True)
                
                st.write(soal['pertanyaan'])
                # Simpan jawaban user ke dictionary responses
                responses[soal['id']] = st.radio(f"Pilih jawaban:", soal['opsi'], key=f"q_{soal['id']}")
                st.markdown('</div>', unsafe_allow_html=True)
        
        # 3. Tombol Submit
        submitted = st.form_submit_button("Selesaikan Tes & Lihat Hasil")

    if submitted:
        # Panggil fungsi hitung skor (nanti kita buat di engine.py atau langsung di sini)
        st.success("Jawaban terkirim! Sekarang AI lagi proses skor lo...")
def show_home():
    # Hero Section
    st.markdown("""
        <div class="hero-container">
            <h1>🛡️ Psychotech Polri v1.0</h1>
            <p>Platform Simulasi Psikotes Terakurat dengan Analisis lengkap</p>
        </div>
    """, unsafe_allow_html=True)

    # Info Singkat (Value Proposition)
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
            <div class="nav-card">
                <div class="card-icon">📝</div>
                <div class="card-title">Simulasi Realistis</div>
                <div class="card-desc">Soal-soal yang dirancang mirip dengan tes asli (Kecerdasan, Kepribadian, Kecermatan).</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div class="nav-card">
                <div class="card-icon">🤖</div>
                <div class="card-title">Analisis AI</div>
                <div class="card-desc">Dapatkan saran langsung dari AI Groq untuk memperbaiki kelemahan lo setelah tes.</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
            <div class="nav-card">
                <div class="card-icon">📊</div>
                <div class="card-title">Psikogram Digital</div>
                <div class="card-desc">Lihat grafik perkembangan mental lo secara visual dan detail.</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # Call to Action
    st.info("💡 **Tips:** Fokuslah pada ketenangan saat mengerjakan soal Kecermatan. Gunakan Sidebar di kiri untuk mulai!")

    # Footer
    st.markdown("""
        <div class="footer">
            Built with ❤️ for Indonesian Casis | © 2026 Psychotech Project
        </div>
    """, unsafe_allow_html=True)

# Panggil fungsi ini di logika routing lo
# --- LOGIKA NAVIGASI ---
if menu == "Home":
    show_home()
elif menu == "Mulai Simulasi":
    show_simulation() # <--- Panggil fungsi yang kita buat tadi
elif menu == "Dashboard Admin":
    # Kalau lo udah bikin admin.py, lo bisa import dan panggil di sini
    import admin
    admin.show_admin_panel()
