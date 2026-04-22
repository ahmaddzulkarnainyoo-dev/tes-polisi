import streamlit as st
import time
from engine import generate_soal_ai, generate_kecermatan
from database import supabase

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Psychotech Polri | Simulasi CAT Profesional",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- STATE MANAGEMENT (Biar navigasi card jalan) ---
if 'menu_nav' not in st.session_state:
    st.session_state.menu_nav = "Home"
if 'materi_aktif' not in st.session_state:
    st.session_state.materi_aktif = None

# ============================================================
# 1. MODERN CSS INJECTOR — Glassmorphism + Mobile Fix
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Sora:wght@400;600;700;800&display=swap');

:root {
    --primary: #1d4ed8; --primary-dark: #1e3a8a; --primary-light: #3b82f6;
    --accent: #06b6d4; --bg-base: #f0f4ff; --bg-card: rgba(255, 255, 255, 0.65);
    --radius-lg: 20px; --radius-md: 14px; --radius-sm: 10px; --blur: blur(18px);
}

html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif !important; background-color: var(--bg-base) !important; }

/* FIX MOBILE: Maksa kolom pecah ke bawah di HP */
@media (max-width: 768px) {
    [data-testid="stHorizontalBlock"] { flex-direction: column !important; gap: 0px !important; }
    [data-testid="column"] { width: 100% !important; min-width: 100% !important; margin-bottom: 12px !important; }
    .hero-wrap { padding: 36px 18px !important; }
    .hero-title { font-size: 1.8rem !important; }
    .stats-row { gap: 8px !important; }
    .stat-pill { padding: 6px 12px !important; min-width: 100px; }
}

.glass-card {
    background: var(--bg-card); backdrop-filter: var(--blur);
    border: 1px solid rgba(255, 255, 255, 0.5); border-radius: var(--radius-lg);
    padding: 28px; margin-bottom: 20px;
}

.hero-wrap {
    background: linear-gradient(135deg, #1e3a8a 0%, #1d4ed8 45%, #06b6d4 100%);
    border-radius: var(--radius-lg); padding: 56px 32px; text-align: center; color: white;
    box-shadow: 0 20px 60px rgba(29, 78, 216, 0.30); margin-bottom: 32px;
}

.nav-card-wrap {
    background: var(--bg-card); backdrop-filter: var(--blur);
    border: 1px solid rgba(255, 255, 255, 0.5); border-radius: var(--radius-md);
    padding: 28px 20px; text-align: center; height: 100%; transition: 0.3s;
}

.stButton > button {
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%) !important;
    color: white !important; border: none !important; border-radius: var(--radius-sm) !important;
    width: 100%; font-weight: 600 !important;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# 2. FUNGSI AUTH & DATABASE
# ============================================================
def login_user(username, password):
    try:
        res = supabase.table("users").select("*").eq("username", username).eq("password", password).execute()
        if res.data:
            user = res.data[0]
            if user.get('status') == 'pending':
                st.error("⏳ Akun Belum Aktif. Silakan hubungi admin.")
                st.stop()
            return user
    except Exception as e:
        st.error(f"Koneksi DB Gagal: {e}")
    return None

# ============================================================
# 3. RENDER HALAMAN UTAMA (HOME)
# ============================================================
def show_home():
    st.markdown("""
        <div class="hero-wrap">
            <h1 style="color:white; font-family:'Sora';">Psychotech Polri</h1>
            <p>Simulasi CAT Psikotes Terakurat untuk Casis Polri.</p>
        </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown('<div class="nav-card-wrap"><h3>🧠</h3><h4>Kecerdasan</h4><p style="font-size:0.8rem; color:#64748b;">Logika & Numerik Pola Polri</p></div>', unsafe_allow_html=True)
        if st.button("Mulai Latihan", key="btn_cerdas"):
            st.session_state.menu_nav = "Mulai Simulasi"
            st.session_state.materi_aktif = "Kecerdasan"
            st.rerun()

    with c2:
        st.markdown('<div class="nav-card-wrap"><h3>🎯</h3><h4>Kecermatan</h4><p style="font-size:0.8rem; color:#64748b;">Latihan Ketelitian Simbol</p></div>', unsafe_allow_html=True)
        if st.button("Mulai Latihan", key="btn_cermat"):
            st.session_state.menu_nav = "Mulai Simulasi"
            st.session_state.materi_aktif = "Kecermatan"
            st.rerun()

    with c3:
        st.markdown('<div class="nav-card-wrap"><h3>🧬</h3><h4>Kepribadian</h4><p style="font-size:0.8rem; color:#64748b;">Tes Karakter & Psikologi</p></div>', unsafe_allow_html=True)
        if st.button("Mulai Latihan", key="btn_pribadi"):
            st.session_state.menu_nav = "Mulai Simulasi"
            st.session_state.materi_aktif = "Kepribadian"
            st.rerun()

# ============================================================
# 4. HALAMAN SIMULASI
# ============================================================
def show_simulation():
    materi = st.session_state.materi_aktif if st.session_state.materi_aktif else "Kecerdasan"
    
    if st.button("← Kembali ke Home"):
        st.session_state.menu_nav = "Home"
        st.rerun()
        
    st.markdown(f"""<div class="glass-card"><h2>Sesi: {materi}</h2></div>""", unsafe_allow_html=True)
    
    # DI SINI LOGIKA ENGINE LO MASUK
    if materi == "Kecermatan":
        st.info("Sesi Kecermatan sedang disiapkan...")
        # generate_kecermatan()
    elif materi == "Kecerdasan":
        st.info("Memuat Soal Kecerdasan...")
        # generate_soal_ai()
    else:
        st.info(f"Sesi {materi} dalam tahap pengembangan.")

# ============================================================
# 5. AUTH INTERFACE & ROUTER
# ============================================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    # Form Login Sederhana (Bisa lo ganti sesuai UI Auth lo)
    st.markdown("<h2 style='text-align:center;'>🔑 Login Casis</h2>", unsafe_allow_html=True)
    with st.form("auth"):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.form_submit_button("Masuk", use_container_width=True):
            user = login_user(u, p)
            if user:
                st.session_state.logged_in = True
                st.session_state.username = u
                st.rerun()
            else:
                st.error("Login Gagal.")
else:
    # Sidebar
    with st.sidebar:
        st.title("🛡️ Dash")
        menu = st.radio("Navigasi", ["Home", "Mulai Simulasi", "Dashboard Admin"], 
                        index=["Home", "Mulai Simulasi", "Dashboard Admin"].index(st.session_state.menu_nav))
        st.session_state.menu_nav = menu
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

    # Route Berdasarkan State
    if st.session_state.menu_nav == "Home":
        show_home()
    elif st.session_state.menu_nav == "Mulai Simulasi":
        show_simulation()
    else:
        st.write("Panel Admin")
