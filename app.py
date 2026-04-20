import streamlit as st
# Hapus import json karena kita pake AI sekarang
from engine import generate_soal_ai 
from database import supabase

# --- BIKIN MENU NAVIGASI ---
st.sidebar.title("🛡️ Psikologi Polri")
menu = st.sidebar.radio("Navigasi", ["Home", "Mulai Simulasi", "Dashboard Admin"])
# --- SIDEBAR FOOTER ---
st.sidebar.markdown("---") # Garis pembatas
st.sidebar.write("🚀 **Project Development**")
st.sidebar.markdown(
    """
    <a href="https://www.instagram.com/growing_together369?igsh=ZXV1eXpreXkweGh5" target="_blank" style="text-decoration: none; color: #E1306C; font-weight: bold;">
        Made by @username_temen_lo
    </a>
    """, 
    unsafe_allow_html=True
)

# --- CSS CUSTOM (Tetap gue pertahankan gaya lo) ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .hero-container {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 50px 20px;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    }
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
    st.markdown('<div class="hero-container"><h1>📝 Simulasi Real-Time</h1></div>', unsafe_allow_html=True)
    
    # 1. Inisialisasi State agar data tidak hilang saat pindah halaman
    if 'step' not in st.session_state:
        st.session_state.step = 1
        st.session_state.skor = 0
        with st.spinner("tunggu sebentar"):
            st.session_state.soal_aktif = generate_soal_ai()

    # Batas simulasi, misal 10 soal
    TOTAL_SOAL = 10

    if st.session_state.step <= TOTAL_SOAL:
        soal = st.session_state.soal_aktif
        
        st.subheader(f"Soal Nomor {st.session_state.step} dari {TOTAL_SOAL}")
        st.info(f"Kategori: {soal.get('kategori', 'Umum')}")
        
        # 2. Tampilin Soal per Halaman menggunakan Form
        with st.form(key=f"ujian_form_{st.session_state.step}"):
            st.write(soal['pertanyaan'])
            
            pilihan = st.radio("Pilih jawaban:", soal['opsi'], key=f"radio_{st.session_state.step}")
            
            submitted = st.form_submit_button("Lanjut ke Soal Berikutnya ➡️")

            if submitted:
                # 3. Cek Skor Langsung
                if pilihan == soal['jawaban']:
                    st.session_state.skor += 10
                
                # Update ke langkah berikutnya
                st.session_state.step += 1
                if st.session_state.step <= TOTAL_SOAL:
                    with st.spinner("Menyiapkan soal baru..."):
                        st.session_state.soal_aktif = generate_soal_ai()
                st.rerun()
    else:
        # 4. Hasil Akhir
        st.balloons()
        st.success(f"🔥 Tes Selesai! Skor total lo: {st.session_state.skor} / 100")
        
        # Opsi simpan ke database atau balik ke home
        if st.button("Ulangi Tes dari Awal"):
            del st.session_state.step
            del st.session_state.skor
            del st.session_state.soal_aktif
            st.rerun()

def show_home():
    st.markdown("""
        <div class="hero-container">
            <h1>🛡️ tes Psikologi Polri v1.0</h1>
            <p>Platform Simulasi Psikotes Terakurat dilengkapi dengan analisi</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="nav-card"><div class="card-icon">📝</div><div class="card-title">Simulasi Realistis</div><div class="card-desc">Satu soal per halaman untuk fokus maksimal.</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="nav-card"><div class="card-icon">🤖</div><div class="card-title">Dynamic AI</div><div class="card-desc">Soal di acak setiap kali lo lathan.</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="nav-card"><div class="card-icon">📊</div><div class="card-title">Leaderboard</div><div class="card-desc">Buktikan lo Casis paling siap tahun ini.</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.info("💡 **Tips:** Kerjakan dengan tenang. Sistem akan mengacak soal secara otomatis.")

# --- LOGIKA ROUTING ---
if menu == "Home":
    show_home()
elif menu == "Mulai Simulasi":
    show_simulation()
elif menu == "Dashboard Admin":
    try:
        import admin
        admin.show_admin_panel()
    except Exception as e:
        st.error(f"Gagal memuat panel admin: {e}")
