import streamlit as st
import time
from engine import generate_soal_ai, generate_kecermatan
from database import supabase

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Tes Psikologi Polri | Simulasi CAT Profesional",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# 1. MODERN CSS INJECTOR — Glassmorphism + Elite Blue-White
# ============================================================
st.markdown("""
<style>
/* ── Google Font Import ── */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Sora:wght@400;600;700;800&display=swap');

/* ── Root Variables ── */
:root {
    --primary:        #1d4ed8;
    --primary-dark:   #1e3a8a;
    --primary-light:  #3b82f6;
    --accent:         #06b6d4;
    --accent-gold:    #f59e0b;
    --bg-base:        #f0f4ff;
    --bg-card:        rgba(255, 255, 255, 0.65);
    --bg-card-dark:   rgba(255, 255, 255, 0.30);
    --border-glass:   rgba(255, 255, 255, 0.50);
    --text-primary:   #0f172a;
    --text-muted:     #64748b;
    --text-white:     #ffffff;
    --shadow-soft:    0 8px 32px rgba(29, 78, 216, 0.10);
    --shadow-card:    0 4px 20px rgba(0, 0, 0, 0.07);
    --radius-lg:      20px;
    --radius-md:      14px;
    --radius-sm:      10px;
    --blur:           blur(18px);
}

/* ── Global Base ── */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    background-color: var(--bg-base) !important;
}

.stApp {
    background:
        radial-gradient(ellipse at 15% 20%, rgba(59, 130, 246, 0.12) 0%, transparent 55%),
        radial-gradient(ellipse at 85% 75%, rgba(6, 182, 212, 0.10) 0%, transparent 55%),
        var(--bg-base) !important;
    min-height: 100vh;
}

/* ── Hide default Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; }

/* ── Glassmorphism Card ── */
.glass-card {
    background: var(--bg-card);
    backdrop-filter: var(--blur);
    -webkit-backdrop-filter: var(--blur);
    border: 1px solid var(--border-glass);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-soft);
    padding: 28px;
    margin-bottom: 20px;
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}
.glass-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 16px 40px rgba(29, 78, 216, 0.14);
}

/* ── Hero Section ── */
.hero-wrap {
    background: linear-gradient(135deg, #1e3a8a 0%, #1d4ed8 45%, #06b6d4 100%);
    border-radius: var(--radius-lg);
    padding: 56px 32px;
    text-align: center;
    position: relative;
    overflow: hidden;
    margin-bottom: 32px;
    box-shadow: 0 20px 60px rgba(29, 78, 216, 0.30);
}
.hero-wrap::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 280px; height: 280px;
    background: rgba(255,255,255,0.06);
    border-radius: 50%;
    pointer-events: none;
}
.hero-wrap::after {
    content: '';
    position: absolute;
    bottom: -80px; left: -40px;
    width: 240px; height: 240px;
    background: rgba(6, 182, 212, 0.12);
    border-radius: 50%;
    pointer-events: none;
}
.hero-badge {
    display: inline-block;
    background: rgba(255,255,255,0.18);
    border: 1px solid rgba(255,255,255,0.35);
    color: #fff;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    padding: 6px 16px;
    border-radius: 999px;
    margin-bottom: 18px;
}
.hero-title {
    font-family: 'Sora', sans-serif;
    font-size: clamp(2rem, 5vw, 3.2rem);
    font-weight: 800;
    color: #fff;
    line-height: 1.15;
    margin: 0 0 14px;
    text-shadow: 0 2px 20px rgba(0,0,0,0.20);
}
.hero-sub {
    font-size: 1.05rem;
    color: rgba(255,255,255,0.85);
    margin: 0 0 32px;
    font-weight: 400;
}

/* ── Trust Signal Stats ── */
.stats-row {
    display: flex;
    justify-content: center;
    gap: 16px;
    flex-wrap: wrap;
    margin-top: 10px;
    position: relative;
    z-index: 1;
}
.stat-pill {
    background: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,0.30);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    border-radius: 999px;
    padding: 10px 22px;
    text-align: center;
    color: #fff;
}
.stat-pill .stat-num {
    font-family: 'Sora', sans-serif;
    font-size: 1.4rem;
    font-weight: 700;
    display: block;
}
.stat-pill .stat-label {
    font-size: 0.75rem;
    opacity: 0.80;
    display: block;
    margin-top: 2px;
}

/* ── News Card ── */
.news-card {
    background: var(--bg-card);
    backdrop-filter: var(--blur);
    -webkit-backdrop-filter: var(--blur);
    border: 1px solid var(--border-glass);
    border-radius: var(--radius-md);
    padding: 22px 20px;
    box-shadow: var(--shadow-card);
    height: 100%;
    transition: transform 0.25s ease, box-shadow 0.25s ease;
    position: relative;
    overflow: hidden;
}
.news-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 32px rgba(29,78,216,0.12);
}
.news-tag {
    display: inline-block;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    padding: 4px 10px;
    border-radius: 999px;
    margin-bottom: 10px;
}
.tag-red    { background: #fee2e2; color: #b91c1c; }
.tag-blue   { background: #dbeafe; color: #1d4ed8; }
.tag-green  { background: #dcfce7; color: #166534; }
.news-title {
    font-family: 'Sora', sans-serif;
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 8px;
    line-height: 1.4;
}
.news-body {
    font-size: 0.83rem;
    color: var(--text-muted);
    line-height: 1.6;
}
.news-date {
    font-size: 0.72rem;
    color: #94a3b8;
    margin-top: 12px;
    display: block;
}

/* ── Nav Cards ── */
.nav-card-wrap {
    background: var(--bg-card);
    backdrop-filter: var(--blur);
    border: 1px solid var(--border-glass);
    border-radius: var(--radius-md);
    padding: 28px 20px;
    text-align: center;
    box-shadow: var(--shadow-card);
    transition: transform 0.25s ease, box-shadow 0.25s ease;
    height: 100%;
}
.nav-card-wrap:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 32px rgba(29,78,216,0.13);
}
.nav-icon { font-size: 2.4rem; display: block; margin-bottom: 10px; }
.nav-title {
    font-family: 'Sora', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 6px;
}
.nav-desc { font-size: 0.8rem; color: var(--text-muted); }

/* ── Score Result Card ── */
.score-card {
    background: linear-gradient(135deg, #1e3a8a 0%, #06b6d4 100%);
    border-radius: var(--radius-lg);
    padding: 36px;
    text-align: center;
    color: white;
    box-shadow: 0 16px 40px rgba(29,78,216,0.25);
}
.score-num {
    font-family: 'Sora', sans-serif;
    font-size: 4rem;
    font-weight: 800;
    line-height: 1;
    margin: 12px 0;
}

/* ── Streamlit Widget Overrides ── */
.stButton > button {
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    padding: 10px 24px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 14px rgba(29, 78, 216, 0.30) !important;
    width: 100%;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 20px rgba(29, 78, 216, 0.40) !important;
}

/* ── FIXED RESPONSIVE (FOR MOBILE) ── */
@media (max-width: 768px) {
    .hero-wrap { padding: 36px 18px; margin-bottom: 20px; }
    .hero-title { font-size: 1.8rem !important; }
    .stats-row { gap: 8px; }
    .stat-pill { padding: 6px 12px; }
    .stat-pill .stat-num { font-size: 1rem; }
    
    /* Supaya kolom gak 'ngilang' atau kepotong di HP */
    [data-testid="column"] {
        width: 100% !important;
        flex: 1 1 auto !important;
        min-width: 100% !important;
        margin-bottom: 15px !important;
    }

    .nav-card-wrap, .news-card {
        margin-bottom: 10px;
        height: auto !important;
    }

    .kunci-grid { gap: 6px; justify-content: center; }
    .kunci-item { min-width: 35px; padding: 6px 8px; font-size: 0.85rem; }
    
    /* Pastikan container utama dapet ruang */
    .block-container { padding-left: 1rem !important; padding-right: 1rem !important; }
}
</style>
""", unsafe_allow_html=True)

# --- LOGIN & DATABASE FUNCTIONS (Pindahkan dari file FUNGSI APP.txt lo) ---
def login_user(username, password):
    res = supabase.table("users").select("*").eq("username", username).eq("password", password).execute()
    if res.data:
        user = res.data[0]
        if user.get('status') == 'pending':
            st.warning("⏳ Akun Belum Aktif. Silakan kirim bukti bayar.")
            st.stop()
        return user
    return None

# --- UI PAGES ---
def show_home():
    # Hero Section
    st.markdown("""
        <div class="hero-wrap">
            <div class="hero-badge">🛡️ Platform Resmi Simulasi CAT Polri</div>
            <h1 class="hero-title">Lolos Psikotes Polri<br>Bukan Sekadar Mimpi</h1>
            <p class="hero-sub">Latihan soal autentik, timer real-time, dan analisis skor.</p>
            <div class="stats-row">
                <div class="stat-pill"><span class="stat-num">1.500+</span><span class="stat-label">Casis Lulus</span></div>
                <div class="stat-pill"><span class="stat-num">98%</span><span class="stat-label">Akurasi Soal</span></div>
                <div class="stat-pill"><span class="stat-num">24/7</span><span class="stat-label">Akses Penuh</span></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Nav Cards (3 Kolom)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""<div class="nav-card-wrap"><span class="nav-icon">🧠</span><div class="nav-title">Kecerdasan</div><div class="nav-desc">Logika & Numerik Pola Polri</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""<div class="nav-card-wrap"><span class="nav-icon">🎯</span><div class="nav-title">Kecermatan</div><div class="nav-desc">Latihan Ketelitian & Kecepatan</div></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown("""<div class="nav-card-wrap"><span class="nav-icon">🧬</span><div class="nav-title">Kepribadian</div><div class="nav-desc">Profil Psikologi Standar Polri</div></div>""", unsafe_allow_html=True)

# --- MAIN APP LOGIC ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    # Tampilkan Login Form (Sederhana untuk contoh)
    with st.form("login"):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.form_submit_button("Masuk"):
            user = login_user(u, p)
            if user:
                st.session_state.logged_in = True
                st.session_state.username = u
                st.rerun()
else:
    # Sidebar Menu
    with st.sidebar:
        st.title("🛡️ Menu")
        menu = st.radio("Navigasi", ["🏠 Home", "📝 Mulai Simulasi"])
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.rerun()
    
    if "Home" in menu:
        show_home()
    else:
        st.write("Halaman Simulasi sedang dalam pengembangan.")
