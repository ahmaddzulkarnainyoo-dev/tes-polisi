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

/* ── Section Title ── */
.section-title {
    font-family: 'Sora', sans-serif;
    font-size: 1.55rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0 0 6px;
}
.section-subtitle {
    font-size: 0.9rem;
    color: var(--text-muted);
    margin: 0 0 24px;
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

/* ── Testimonial Infinite Slider ── */
.testi-section {
    overflow: hidden;
    position: relative;
    padding: 12px 0;
    mask-image: linear-gradient(to right, transparent 0%, black 8%, black 92%, transparent 100%);
    -webkit-mask-image: linear-gradient(to right, transparent 0%, black 8%, black 92%, transparent 100%);
}
.testi-track {
    display: flex;
    gap: 16px;
    width: max-content;
    animation: scroll-left 38s linear infinite;
}
.testi-track:hover { animation-play-state: paused; }
@keyframes scroll-left {
    0%   { transform: translateX(0); }
    100% { transform: translateX(-50%); }
}
.testi-card {
    background: rgba(255,255,255,0.72);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.55);
    border-radius: var(--radius-md);
    padding: 18px 22px;
    min-width: 270px;
    max-width: 270px;
    box-shadow: 0 4px 16px rgba(29,78,216,0.07);
    flex-shrink: 0;
}
.testi-stars { color: var(--accent-gold); font-size: 0.85rem; margin-bottom: 8px; }
.testi-text {
    font-size: 0.83rem;
    color: var(--text-primary);
    line-height: 1.55;
    margin-bottom: 12px;
    font-style: italic;
}
.testi-author {
    display: flex;
    align-items: center;
    gap: 10px;
}
.testi-avatar {
    width: 34px; height: 34px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.75rem; font-weight: 700;
    color: #fff;
    flex-shrink: 0;
}
.testi-name {
    font-size: 0.8rem;
    font-weight: 700;
    color: var(--text-primary);
}
.testi-meta {
    font-size: 0.7rem;
    color: var(--text-muted);
}

/* ── Auth Card ── */
.auth-wrap {
    max-width: 460px;
    margin: 0 auto;
}
.auth-header {
    text-align: center;
    margin-bottom: 28px;
}
.auth-icon {
    font-size: 3rem;
    display: block;
    margin-bottom: 10px;
}
.auth-title {
    font-family: 'Sora', sans-serif;
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0;
}
.auth-sub {
    font-size: 0.85rem;
    color: var(--text-muted);
    margin-top: 4px;
}

/* ── Payment Instruction Card ── */
.payment-card {
    background: linear-gradient(135deg, #1e3a8a 0%, #1d4ed8 100%);
    border-radius: var(--radius-md);
    padding: 22px 20px;
    color: white;
    margin-top: 20px;
}
.payment-card h4 {
    font-family: 'Sora', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    margin: 0 0 14px;
    display: flex; align-items: center; gap: 8px;
}
.payment-row {
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.20);
    border-radius: var(--radius-sm);
    padding: 10px 14px;
    font-size: 0.85rem;
    margin-bottom: 8px;
    display: flex; align-items: center; gap: 10px;
}
.payment-row strong { font-weight: 700; }

/* ── Simulation ── */
.sim-header {
    background: linear-gradient(135deg, #1e3a8a, #1d4ed8);
    border-radius: var(--radius-md);
    padding: 18px 22px;
    color: white;
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
}
.sim-title {
    font-family: 'Sora', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
}
.timer-badge {
    background: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,0.30);
    border-radius: 999px;
    padding: 6px 18px;
    font-size: 0.9rem;
    font-weight: 700;
    font-family: 'Sora', monospace;
    min-width: 110px;
    text-align: center;
}
.timer-badge.urgent { background: rgba(239,68,68,0.25); border-color: rgba(239,68,68,0.50); }

.kunci-grid {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-bottom: 20px;
}
.kunci-item {
    background: var(--bg-card);
    backdrop-filter: var(--blur);
    border: 1.5px solid var(--primary-light);
    border-radius: var(--radius-sm);
    padding: 10px 18px;
    font-family: 'Sora', monospace;
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--primary-dark);
    min-width: 48px;
    text-align: center;
}

.question-box {
    background: var(--bg-card);
    backdrop-filter: var(--blur);
    border: 1px solid var(--border-glass);
    border-radius: var(--radius-md);
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: var(--shadow-card);
}
.question-label {
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: var(--primary-light);
    margin-bottom: 8px;
}
.question-text {
    font-size: 1rem;
    color: var(--text-primary);
    line-height: 1.65;
    font-weight: 500;
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
    background: linear-gradient(135deg, var(--primary-dark) 0%, var(--primary) 100%) !important;
}
.stTextInput > div > div > input {
    border-radius: var(--radius-sm) !important;
    border: 1.5px solid #e2e8f0 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.9rem !important;
    padding: 10px 14px !important;
    transition: border-color 0.2s !important;
    background: rgba(255,255,255,0.8) !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--primary-light) !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.12) !important;
}
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.50) !important;
    border-radius: var(--radius-sm) !important;
    padding: 4px !important;
    gap: 4px !important;
    border: 1px solid rgba(255,255,255,0.60) !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    padding: 8px 16px !important;
}
.stTabs [aria-selected="true"] {
    background: white !important;
    color: var(--primary) !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
}
.stSelectbox > div > div {
    border-radius: var(--radius-sm) !important;
    border: 1.5px solid #e2e8f0 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    background: rgba(255,255,255,0.80) !important;
}
.stRadio > div { gap: 8px !important; }
.stRadio label {
    background: rgba(255,255,255,0.65) !important;
    border: 1.5px solid #e2e8f0 !important;
    border-radius: var(--radius-sm) !important;
    padding: 10px 14px !important;
    transition: all 0.2s !important;
    cursor: pointer !important;
}
.stRadio label:hover {
    border-color: var(--primary-light) !important;
    background: rgba(219,234,254,0.50) !important;
}
.stSidebar {
    background: rgba(255,255,255,0.70) !important;
    backdrop-filter: var(--blur) !important;
    border-right: 1px solid rgba(255,255,255,0.50) !important;
}
/* Alert overrides */
.stSuccess, .stWarning, .stInfo, .stError {
    border-radius: var(--radius-sm) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

/* ── Footer credit ── */
.ig-credit-box {
    text-align: center;
    padding: 20px;
    color: var(--text-muted);
    font-size: 0.82rem;
}
.ig-credit-box a {
    color: #E1306C;
    font-weight: 700;
    text-decoration: none;
}
.ig-credit-box a:hover { text-decoration: underline; }

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
.score-label {
    font-size: 0.9rem;
    opacity: 0.85;
    text-transform: uppercase;
    letter-spacing: 1px;
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

/* ── PERBAIKAN RESPONSIVE (SELIPAN DI SINI) ── */
@media (max-width: 768px) {
    .hero-wrap { padding: 36px 18px; margin-bottom: 20px; }
    .hero-title { font-size: 1.8rem !important; }
    .stats-row { gap: 10px; justify-content: center; }
    .stat-pill { padding: 8px 14px; }
    .stat-pill .stat-num { font-size: 1.2rem; }
    
    /* FIX: Paksa kolom Streamlit jadi 100% lebar biar berjejer ke bawah */
    [data-testid="column"] {
        width: 100% !important;
        flex: 1 1 auto !important;
        min-width: 100% !important;
        margin-bottom: 15px !important;
    }
    .nav-card-wrap, .news-card {
        height: auto !important;
    }
    .kunci-grid { gap: 8px; justify-content: center; }
    .kunci-item { min-width: 42px; padding: 8px 12px; font-size: 0.95rem; }
    .sim-header { padding: 14px 16px; }
    .block-container { padding-left: 1rem !important; padding-right: 1rem !important; }
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# 2. HELPER DATA & FUNCTIONS (TESTIMONIALS, AUTH, DLL)
# ============================================================
TESTIMONIALS = [
    {"name": "adli66",         "role": "Casis Brimob 2024", "color": "#1d4ed8", "text": "Platform ini keren banget, soal-soalnya mirip banget sama yang keluar aslinya. Lolos psikotes berkat latihan sini tiap hari!"},
    {"name": "rivaldo_polri",  "role": "Polda Sumut",        "color": "#0891b2", "text": "Timer-nya bikin deg-degan, persis kayak kondisi ujian beneran. Mental jadi lebih siap."},
    {"name": "bayu_perkasa",   "role": "Akademi Polisi",     "color": "#7c3aed", "text": "Soal kecermatannya challenging banget, tapi setelah rutin latihan di sini, nilai gue naik drastis."},
    {"name": "nadia_casis",    "role": "Polda Jabar",        "color": "#059669", "text": "Fitur kepribadiannya bagus, ngebantu gue ngerti pola jawaban yang tepat untuk profil polri."},
    {"name": "rafi_pratama",   "role": "Casis Polri 2025",   "color": "#dc2626", "text": "Udah coba banyak aplikasi simulasi, tapi yang ini paling mirip sama format aslinya. Highly recommended!"},
    {"name": "syahrul_ok",     "role": "Polda Kaltim",       "color": "#d97706", "text": "Admin responsif, ada masalah langsung dibantu. Akun aktif cepet. Simulasinya juga update terus."},
    {"name": "dewi_aulia22",   "role": "Polwan Seleksi",     "color": "#db2777", "text": "Sebagai calon polwan, soal-soalnya relevan dan penjelasannya mudah dipahami. Dapet insight baru tiap sesi."},
    {"name": "handoko_bravo",  "role": "Polda Jateng",       "color": "#0f766e", "text": "Latihan kecerdasan di sini bikin kemampuan analitik gue makin tajam. Worth every penny!"},
]

def render_testimonial_slider():
    doubled = TESTIMONIALS * 2
    cards_html = ""
    for t in doubled:
        initials = "".join(w[0].upper() for w in t["name"].replace("_", " ").split()[:2])
        cards_html += f"""
        <div class="testi-card">
            <div class="testi-stars">★★★★★</div>
            <p class="testi-text">"{t['text']}"</p>
            <div class="testi-author">
                <div class="testi-avatar" style="background:{t['color']};">{initials}</div>
                <div>
                    <div class="testi-name">@{t['name']}</div>
                    <div class="testi-meta">{t['role']}</div>
                </div>
            </div>
        </div>
        """
    st.markdown(f"""
        <div class="testi-section">
            <div class="testi-track">{cards_html}</div>
        </div>
    """, unsafe_allow_html=True)

def login_user(username, password):
    res = supabase.table("users").select("*").eq("username", username).eq("password", password).execute()
    if res.data:
        user = res.data[0]
        if user.get('status') == 'pending':
            st.markdown("""
                <div class="payment-card">
                    <h4>⏳ Akun Belum Aktif</h4>
                    <div class="payment-row">📱 <span>Kirim bukti bayar via <strong>WhatsApp</strong></span></div>
                    <div class="payment-row">📞 <strong>0853-6637-4530</strong></div>
                    <div class="payment-row">🏦 Rekening <strong>SEABANK: 901018867564</strong> a.n. ALAN RINANDO </div>
                    <div class="payment-row">💰 Biaya Aktivasi: <strong>Rp 25.000</strong></div>
                </div>
            """, unsafe_allow_html=True)
            st.stop()
        return user
    return None

def register_user(username, password):
    try:
        supabase.table("users").insert({"username": username, "password": password, "status": "pending"}).execute()
        return True
    except:
        return False

def show_auth():
    st.markdown("""
        <div style="text-align:center; padding: 36px 20px 20px;">
            <div style="font-size:3.5rem; margin-bottom:10px;">🛡️</div>
            <div style="font-family:'Sora',sans-serif; font-size:1.9rem; font-weight:800; color:#1e3a8a;">Psychotech Polri</div>
            <div style="font-size:0.9rem; color:#64748b; margin-top:6px;">Platform Simulasi CAT Psikotes Terpercaya</div>
        </div>
    """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="glass-card" style="padding:32px;">', unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["🔑  Masuk", "📝  Daftar"])
        with tab1:
            st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
            with st.form("login_form"):
                u = st.text_input("Username", placeholder="Masukkan username lo")
                p = st.text_input("Password", type="password", placeholder="••••••••")
                if st.form_submit_button("Masuk ke Dashboard →", use_container_width=True):
                    user = login_user(u, p)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.username = u
                        st.rerun()
                    else:
                        st.error("❌ Username atau Password salah, coba lagi.")
        with tab2:
            st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
            with st.form("reg_form", clear_on_submit=True):
                new_u = st.text_input("Username Baru")
                new_p = st.text_input("Password", type="password")
                if st.form_submit_button("Daftar Sekarang →", use_container_width=True):
                    if register_user(new_u, new_p):
                        st.success(f"✅ Akun **{new_u}** berhasil dibuat!")
                    else:
                        st.error("❌ Username sudah dipakai.")
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# 3. PAGE RENDERING (HOME, SIMULATION, DLL)
# ============================================================
def show_home():
    st.markdown("""
        <div class="hero-wrap">
            <div class="hero-badge">🛡️ Platform Resmi Simulasi CAT Polri</div>
            <h1 class="hero-title">Lolos Psikotes Polri<br>Bukan Sekadar Mimpi</h1>
            <p class="hero-sub">Latihan soal autentik, timer real-time, dan analisis skor.</p>
            <div class="stats-row">
                <div class="stat-pill"><span class="stat-num">1.500+</span><span class="stat-label">Casis Lulus</span></div>
                <div class="stat-pill"><span class="stat-num">98%</span><span class="stat-label">Akurasi Soal</span></div>
                <div class="stat-pill"><span class="stat-num">3</span><span class="stat-label">Sesi Ujian</span></div>
                <div class="stat-pill"><span class="stat-num">24/7</span><span class="stat-label">Akses Penuh</span></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    navs = [
        ("🧠", "Kecerdasan", "Logika, numerik & verbal berbasis pola soal asli Polri."),
        ("🎯", "Kecermatan", "Latihan ketelitian dan kecepatan membaca simbol."),
        ("🧬", "Kepribadian", "Profil psikologi berbasis instrumen standar seleksi."),
    ]
    for col, (icon, title, desc) in zip([c1, c2, c3], navs):
        with col:
            st.markdown(f"""<div class="nav-card-wrap"><span class="nav-icon">{icon}</span><div class="nav-title">{title}</div><div class="nav-desc">{desc}</div></div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">📰 Berita & Update Terkini</div>', unsafe_allow_html=True)
    n1, n2, n3 = st.columns(3)
    # ... (Isi news_data lo di sini) ...
    render_testimonial_slider()

def show_simulation():
    st.markdown("""<div style="font-family:'Sora',sans-serif; font-size:1.3rem; font-weight:700; color:#1e3a8a; margin-bottom:16px;">🎯 Mulai Simulasi CAT</div>""", unsafe_allow_html=True)
    sesi = st.selectbox("Pilih Sesi Ujian:", ["Kecerdasan", "Kecermatan", "Kepribadian"], label_visibility="collapsed")
    # ... (Isi logika simulasi lo di sini) ...
    st.info(f"Sesi {sesi} siap dimulai.")

# ============================================================
# 4. MAIN APP ROUTER
# ============================================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    show_auth()
else:
    with st.sidebar:
        st.markdown(f"### 🛡️ Dashboard Casis")
        menu = st.radio("Pilih Menu:", ["🏠  Home", "📝  Mulai Simulasi", "📊  Dashboard Admin"])
        st.divider()
        if st.button("🚪 Keluar (Logout)", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    page = menu.split("  ", 1)[-1]
    if page == "Home":
        show_home()
    elif page == "Mulai Simulasi":
        show_simulation()
    elif page == "Dashboard Admin":
        st.write("Admin Panel")
        
