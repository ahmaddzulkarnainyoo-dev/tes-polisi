"""
app.py — Psychotech Polri | Arena Kompetisi CAT
Rebuilt: Dark Military aesthetic, stable timer, 4 sesi synced with engine.py
"""

import streamlit as st
import time
from engine import (
    generate_soal_kecerdasan,
    generate_soal_kepribadian,
    generate_kecermatan,
    generate_pass_hand,
    hitung_aps,
    hitung_ketahanan,
    catat_waktu_jawab,
    nilai_jawaban_kecerdasan,
    nilai_jawaban_kepribadian,
    nilai_jawaban_kecermatan,
    posisi_target_acak,
)
from database import supabase

# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Psychotech Polri | Arena CAT",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════
# CSS — DARK ARENA / MILITARY COMMAND
# ══════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Barlow+Condensed:wght@400;600;700;800;900&family=Barlow:wght@300;400;500;600&display=swap');

:root {
    --bg-void:      #080c10;
    --bg-panel:     #0d1117;
    --bg-surface:   #161b22;
    --bg-elevated:  #1c2128;
    --border-dim:   rgba(255,255,255,0.06);
    --border-glow:  rgba(251,107,0,0.35);
    --accent:       #fb6b00;
    --accent-dim:   rgba(251,107,0,0.15);
    --accent-ember: #ff3c00;
    --green-ok:     #39d353;
    --red-alert:    #f85149;
    --gold:         #e3b341;
    --text-pri:     #e6edf3;
    --text-sec:     #7d8590;
    --text-dim:     #484f58;
    --mono:         'JetBrains Mono', monospace;
    --display:      'Barlow Condensed', sans-serif;
    --body:         'Barlow', sans-serif;
    --r-sm:         6px;
    --r-md:         10px;
    --r-lg:         16px;
}

html, body, [class*="css"] {
    font-family: var(--body) !important;
    background-color: var(--bg-void) !important;
    color: var(--text-pri) !important;
}

.stApp {
    background:
        radial-gradient(ellipse at 20% 0%, rgba(251,107,0,0.07) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 100%, rgba(57,211,83,0.04) 0%, transparent 45%),
        var(--bg-void) !important;
    min-height: 100vh;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding-top: 1.2rem !important;
    padding-bottom: 3rem !important;
    max-width: 1200px !important;
}

/* ── Scanline overlay ── */
.stApp::after {
    content: '';
    position: fixed; inset: 0;
    background: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 2px,
        rgba(0,0,0,0.03) 2px,
        rgba(0,0,0,0.03) 4px
    );
    pointer-events: none;
    z-index: 9999;
}

/* ── Panels ── */
.panel {
    background: var(--bg-panel);
    border: 1px solid var(--border-dim);
    border-radius: var(--r-lg);
    padding: 28px;
    margin-bottom: 20px;
}
.panel-elevated {
    background: var(--bg-surface);
    border: 1px solid var(--border-dim);
    border-radius: var(--r-md);
    padding: 20px;
}

/* ── Hero / Command Banner ── */
.hero-command {
    background: linear-gradient(135deg, #0d1117 0%, #161b22 50%, #1a1f2e 100%);
    border: 1px solid var(--border-dim);
    border-top: 2px solid var(--accent);
    border-radius: var(--r-lg);
    padding: 48px 36px 40px;
    position: relative;
    overflow: hidden;
    margin-bottom: 28px;
}
.hero-command::before {
    content: 'PSYCHOTECH';
    position: absolute;
    right: -20px; top: -10px;
    font-family: var(--display);
    font-size: 9rem;
    font-weight: 900;
    color: rgba(255,255,255,0.02);
    line-height: 1;
    pointer-events: none;
    letter-spacing: -4px;
}
.hero-rank {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: var(--accent-dim);
    border: 1px solid var(--border-glow);
    border-radius: 4px;
    padding: 4px 12px;
    font-family: var(--mono);
    font-size: 0.7rem;
    color: var(--accent);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 16px;
}
.hero-rank::before { content: '▶'; font-size: 0.5rem; }
.hero-title {
    font-family: var(--display);
    font-size: clamp(2.4rem, 6vw, 4rem);
    font-weight: 900;
    color: var(--text-pri);
    line-height: 1.0;
    margin: 0 0 12px;
    letter-spacing: -1px;
}
.hero-title span { color: var(--accent); }
.hero-sub {
    font-size: 1rem;
    color: var(--text-sec);
    margin: 0 0 28px;
    font-weight: 300;
    max-width: 520px;
}
.stat-row {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
}
.stat-chip {
    background: var(--bg-elevated);
    border: 1px solid var(--border-dim);
    border-radius: var(--r-sm);
    padding: 10px 18px;
    text-align: center;
    min-width: 90px;
}
.stat-chip .n {
    font-family: var(--display);
    font-size: 1.6rem;
    font-weight: 800;
    color: var(--accent);
    display: block;
    line-height: 1;
}
.stat-chip .l {
    font-size: 0.68rem;
    color: var(--text-sec);
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-top: 3px;
    display: block;
}

/* ── Section header ── */
.sec-head {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 16px;
}
.sec-head-line {
    width: 3px; height: 20px;
    background: var(--accent);
    border-radius: 2px;
    flex-shrink: 0;
}
.sec-head-text {
    font-family: var(--display);
    font-size: 1.2rem;
    font-weight: 700;
    color: var(--text-pri);
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

/* ── Arena Cards (Sesi) ── */
.arena-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 14px;
    margin-bottom: 24px;
}
@media (max-width: 640px) {
    .arena-grid { grid-template-columns: 1fr; }
    .stat-row { flex-direction: column; }
    .stat-chip { min-width: unset; width: 100%; }
}
.arena-card {
    background: var(--bg-surface);
    border: 1px solid var(--border-dim);
    border-radius: var(--r-md);
    padding: 22px 20px 20px;
    cursor: pointer;
    transition: border-color 0.2s, transform 0.2s, box-shadow 0.2s;
    position: relative;
    overflow: hidden;
}
.arena-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: var(--card-accent, var(--accent));
    opacity: 0.7;
}
.arena-card:hover {
    border-color: var(--border-glow);
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(251,107,0,0.12);
}
.arena-card .ac-icon {
    font-size: 2rem;
    display: block;
    margin-bottom: 10px;
}
.arena-card .ac-title {
    font-family: var(--display);
    font-size: 1.1rem;
    font-weight: 800;
    color: var(--text-pri);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 6px;
}
.arena-card .ac-desc {
    font-size: 0.8rem;
    color: var(--text-sec);
    line-height: 1.5;
    margin-bottom: 14px;
}
.arena-card .ac-meta {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}
.meta-tag {
    font-family: var(--mono);
    font-size: 0.65rem;
    color: var(--accent);
    background: var(--accent-dim);
    border: 1px solid var(--border-glow);
    border-radius: 3px;
    padding: 2px 7px;
    text-transform: uppercase;
}

/* ── Leaderboard ── */
.lb-table {
    width: 100%;
    border-collapse: collapse;
    font-family: var(--body);
    font-size: 0.88rem;
}
.lb-table th {
    font-family: var(--mono);
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: var(--text-dim);
    padding: 8px 12px;
    border-bottom: 1px solid var(--border-dim);
    text-align: left;
}
.lb-table td {
    padding: 10px 12px;
    border-bottom: 1px solid var(--border-dim);
    color: var(--text-pri);
    vertical-align: middle;
}
.lb-table tr:last-child td { border-bottom: none; }
.lb-table tr:hover td { background: var(--bg-elevated); }
.lb-rank {
    font-family: var(--mono);
    font-weight: 700;
    font-size: 0.9rem;
}
.lb-rank.r1 { color: var(--gold); }
.lb-rank.r2 { color: #c0c0c0; }
.lb-rank.r3 { color: #cd7f32; }
.lb-rank.rx { color: var(--text-dim); }
.lb-score {
    font-family: var(--display);
    font-size: 1.1rem;
    font-weight: 800;
    color: var(--accent);
}
.lb-sesi {
    font-family: var(--mono);
    font-size: 0.7rem;
    color: var(--text-sec);
    background: var(--bg-elevated);
    border-radius: 3px;
    padding: 2px 7px;
}

/* ── Sim Header ── */
.sim-hdr {
    background: var(--bg-panel);
    border: 1px solid var(--border-dim);
    border-top: 2px solid var(--accent);
    border-radius: var(--r-md);
    padding: 16px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
    margin-bottom: 16px;
}
.sim-hdr-left .sesi-label {
    font-family: var(--mono);
    font-size: 0.65rem;
    color: var(--accent);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 4px;
}
.sim-hdr-left .sesi-title {
    font-family: var(--display);
    font-size: 1.4rem;
    font-weight: 800;
    color: var(--text-pri);
    letter-spacing: 0.5px;
}
.timer-box {
    background: var(--bg-elevated);
    border: 1px solid var(--border-dim);
    border-radius: var(--r-sm);
    padding: 8px 18px;
    font-family: var(--mono);
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--green-ok);
    min-width: 100px;
    text-align: center;
    transition: color 0.3s, border-color 0.3s;
}
.timer-box.warn { color: var(--gold); border-color: rgba(227,179,65,0.4); }
.timer-box.crit { color: var(--red-alert); border-color: rgba(248,81,73,0.4);
    animation: pulse-red 0.5s ease-in-out infinite alternate; }
@keyframes pulse-red {
    from { box-shadow: none; }
    to   { box-shadow: 0 0 12px rgba(248,81,73,0.35); }
}

/* ── Question Box ── */
.q-box {
    background: var(--bg-surface);
    border: 1px solid var(--border-dim);
    border-radius: var(--r-md);
    padding: 26px 24px;
    margin-bottom: 20px;
}
.q-num {
    font-family: var(--mono);
    font-size: 0.65rem;
    color: var(--accent);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 10px;
}
.q-text {
    font-size: 1.02rem;
    color: var(--text-pri);
    line-height: 1.7;
    font-weight: 400;
}

/* ── Kunci Grid ── */
.kunci-grid {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-bottom: 16px;
}
.kunci-char {
    background: var(--bg-elevated);
    border: 1px solid var(--accent);
    border-radius: var(--r-sm);
    padding: 10px 16px;
    font-family: var(--mono);
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--accent);
    min-width: 46px;
    text-align: center;
}
.tampilan-box {
    font-family: var(--mono);
    font-size: 1.4rem;
    letter-spacing: 8px;
    color: var(--text-pri);
    background: var(--bg-elevated);
    border: 1px solid var(--border-dim);
    border-radius: var(--r-sm);
    padding: 14px 20px;
    display: inline-block;
    margin: 12px 0;
}
.tampilan-box .missing {
    color: var(--red-alert);
    font-size: 1.6rem;
}

/* ── Pass Hand ── */
.passhand-area {
    background: var(--bg-elevated);
    border: 1px solid var(--border-dim);
    border-radius: var(--r-md);
    min-height: 280px;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    overflow: hidden;
    margin-bottom: 16px;
}
.ph-target-btn {
    position: absolute;
    width: 64px; height: 64px;
    border-radius: 50%;
    background: radial-gradient(circle at 35% 35%, var(--accent), var(--accent-ember));
    border: 2px solid rgba(255,255,255,0.2);
    cursor: pointer;
    animation: target-pulse 1.2s ease-in-out infinite;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.2rem;
    box-shadow: 0 0 20px rgba(251,107,0,0.5);
    transition: transform 0.1s;
}
.ph-target-btn:active { transform: scale(0.9); }
@keyframes target-pulse {
    0%, 100% { box-shadow: 0 0 12px rgba(251,107,0,0.4); }
    50%       { box-shadow: 0 0 28px rgba(251,107,0,0.8); }
}
.ph-counter {
    font-family: var(--display);
    font-size: 5rem;
    font-weight: 900;
    color: var(--accent);
    text-align: center;
    line-height: 1;
}
.ph-label {
    font-family: var(--mono);
    font-size: 0.7rem;
    color: var(--text-sec);
    text-align: center;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 6px;
}

/* ── Score Result ── */
.result-box {
    background: linear-gradient(135deg, var(--bg-panel) 0%, var(--bg-surface) 100%);
    border: 1px solid var(--border-glow);
    border-top: 3px solid var(--accent);
    border-radius: var(--r-lg);
    padding: 44px 32px;
    text-align: center;
}
.result-label {
    font-family: var(--mono);
    font-size: 0.65rem;
    color: var(--accent);
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 10px;
}
.result-score {
    font-family: var(--display);
    font-size: 5.5rem;
    font-weight: 900;
    color: var(--text-pri);
    line-height: 1;
    margin: 8px 0 4px;
}
.result-verdict {
    font-size: 1rem;
    color: var(--text-sec);
    margin-top: 8px;
}
.result-bar-wrap {
    background: var(--bg-elevated);
    border-radius: 3px;
    height: 6px;
    max-width: 300px;
    margin: 18px auto 0;
    overflow: hidden;
}
.result-bar-fill {
    height: 100%;
    border-radius: 3px;
    background: linear-gradient(90deg, var(--accent), var(--accent-ember));
    transition: width 0.8s ease;
}

/* ── Auth ── */
.auth-shell {
    max-width: 420px;
    margin: 60px auto 0;
}
.auth-logo {
    text-align: center;
    margin-bottom: 28px;
}
.auth-logo .badge {
    font-family: var(--mono);
    font-size: 0.7rem;
    color: var(--accent);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 10px;
    display: block;
}
.auth-logo .name {
    font-family: var(--display);
    font-size: 2.4rem;
    font-weight: 900;
    color: var(--text-pri);
    letter-spacing: -1px;
}
.auth-logo .name span { color: var(--accent); }
.auth-logo .sub {
    font-size: 0.82rem;
    color: var(--text-sec);
    margin-top: 4px;
}

/* ── Payment Steps ── */
.pay-box {
    background: var(--bg-surface);
    border: 1px solid var(--border-glow);
    border-left: 3px solid var(--accent);
    border-radius: var(--r-md);
    padding: 18px 16px;
    margin-top: 16px;
}
.pay-box h5 {
    font-family: var(--display);
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--accent);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin: 0 0 12px;
}
.pay-row {
    font-size: 0.82rem;
    color: var(--text-sec);
    padding: 6px 0;
    border-bottom: 1px solid var(--border-dim);
    display: flex;
    gap: 8px;
}
.pay-row:last-child { border-bottom: none; }
.pay-row strong { color: var(--text-pri); }

/* ── Progress Bar ── */
.prog-wrap {
    background: var(--bg-elevated);
    border-radius: 3px;
    height: 4px;
    margin-bottom: 18px;
    overflow: hidden;
}
.prog-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--accent), var(--accent-ember));
    border-radius: 3px;
    transition: width 0.3s ease;
}

/* ── Streamlit overrides ── */
.stButton > button {
    background: var(--accent) !important;
    color: #000 !important;
    border: none !important;
    border-radius: var(--r-sm) !important;
    font-family: var(--display) !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.5px !important;
    text-transform: uppercase !important;
    padding: 10px 22px !important;
    transition: all 0.15s ease !important;
    width: 100%;
}
.stButton > button:hover {
    background: var(--accent-ember) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 18px rgba(251,107,0,0.35) !important;
}
.stTextInput > div > div > input {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border-dim) !important;
    border-radius: var(--r-sm) !important;
    color: var(--text-pri) !important;
    font-family: var(--body) !important;
    font-size: 0.9rem !important;
    padding: 10px 14px !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px var(--accent-dim) !important;
}
.stTextInput > label, .stSelectbox > label, .stRadio > label {
    color: var(--text-sec) !important;
    font-size: 0.8rem !important;
    font-family: var(--mono) !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
}
.stSelectbox > div > div {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border-dim) !important;
    border-radius: var(--r-sm) !important;
    color: var(--text-pri) !important;
}
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg-elevated) !important;
    border-radius: var(--r-sm) !important;
    padding: 4px !important;
    gap: 4px !important;
    border: 1px solid var(--border-dim) !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 5px !important;
    font-family: var(--display) !important;
    font-size: 0.95rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
    color: var(--text-sec) !important;
    padding: 8px 16px !important;
}
.stTabs [aria-selected="true"] {
    background: var(--bg-panel) !important;
    color: var(--accent) !important;
    border: 1px solid var(--border-glow) !important;
}
.stRadio > div { gap: 8px !important; }
.stRadio label {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border-dim) !important;
    border-radius: var(--r-sm) !important;
    padding: 10px 14px !important;
    color: var(--text-pri) !important;
    font-family: var(--body) !important;
    font-size: 0.9rem !important;
    transition: all 0.15s !important;
    cursor: pointer !important;
}
.stRadio label:hover {
    border-color: var(--border-glow) !important;
    background: var(--bg-surface) !important;
}
.stSidebar {
    background: var(--bg-panel) !important;
    border-right: 1px solid var(--border-dim) !important;
}
.stAlert, .stSuccess, .stWarning, .stInfo, .stError {
    border-radius: var(--r-sm) !important;
    font-family: var(--body) !important;
}
div[data-testid="stProgress"] > div {
    background: var(--bg-elevated) !important;
}
div[data-testid="stProgress"] > div > div {
    background: var(--accent) !important;
}

/* ── Responsive sim layout ── */
@media (max-width: 640px) {
    .sim-hdr { flex-direction: column; align-items: flex-start; }
    .kunci-grid { gap: 6px; }
    .kunci-char { min-width: 38px; padding: 8px 10px; font-size: 0.95rem; }
    .result-score { font-size: 4rem; }
    .ph-counter { font-size: 3.5rem; }
}

/* ── Footer ── */
.footer-credit {
    text-align: center;
    padding: 24px 0 8px;
    font-size: 0.78rem;
    color: var(--text-dim);
}
.footer-credit a { color: var(--accent); text-decoration: none; font-weight: 600; }
.footer-credit a:hover { color: var(--accent-ember); }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════
# DB HELPERS
# ══════════════════════════════════════════════
def login_user(username: str, password: str):
    res = supabase.table("users").select("*").eq("username", username).eq("password", password).execute()
    if res.data:
        user = res.data[0]
        if user.get("status") == "pending":
            st.markdown("""
                <div class="pay-box">
                    <h5>⏳ Akun Belum Aktif</h5>
                    <div class="pay-row">📱 <span>Kirim bukti bayar via <strong>WhatsApp</strong></span></div>
                    <div class="pay-row">📞 <strong>0853-6637-4530</strong></div>
                    <div class="pay-row">🏦 BRI: <strong>1234-5678-9012-3456</strong> a.n. Growing Together</div>
                    <div class="pay-row">💰 Biaya Aktivasi: <strong>Rp 25.000</strong></div>
                </div>
            """, unsafe_allow_html=True)
            st.stop()
        return user
    return None

def register_user(username: str, password: str) -> bool:
    try:
        supabase.table("users").insert({"username": username, "password": password, "status": "pending"}).execute()
        return True
    except Exception:
        return False

def save_score(username: str, sesi: str, skor: int):
    try:
        supabase.table("scores").insert({"username": username, "sesi": sesi, "skor": skor}).execute()
    except Exception:
        pass

def get_leaderboard(sesi: str = "Semua", limit: int = 5) -> list:
    try:
        if sesi == "Semua":
            res = supabase.table("scores").select("username, sesi, skor").order("skor", desc=True).limit(limit).execute()
        else:
            res = supabase.table("scores").select("username, sesi, skor").eq("sesi", sesi).order("skor", desc=True).limit(limit).execute()
        return res.data or []
    except Exception:
        return []


# ══════════════════════════════════════════════
# AUTH PAGE
# ══════════════════════════════════════════════
def show_auth():
    st.markdown("""
        <div class="auth-logo">
            <span class="badge">[ CAT SYSTEM v2.0 ]</span>
            <div class="name">PSYCHO<span>TECH</span></div>
            <div class="sub">Platform Simulasi CAT Psikotes Polri</div>
        </div>
    """, unsafe_allow_html=True)

    col_l, col_m, col_r = st.columns([1, 2.2, 1])
    with col_m:
        with st.container():
            st.markdown('<div class="panel">', unsafe_allow_html=True)
            tab1, tab2 = st.tabs(["🔑  LOGIN", "📝  DAFTAR"])

            with tab1:
                st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
                with st.form("login_form"):
                    u = st.text_input("Username", placeholder="username lo")
                    p = st.text_input("Password", type="password", placeholder="••••••••")
                    if st.form_submit_button("MASUK KE ARENA →", use_container_width=True):
                        user = login_user(u, p)
                        if user:
                            st.session_state.logged_in = True
                            st.session_state.username  = u
                            st.session_state.page      = "home"
                            st.rerun()
                        else:
                            st.error("❌ Kredensial salah.")

            with tab2:
                st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
                with st.form("reg_form", clear_on_submit=True):
                    nu = st.text_input("Username Baru", placeholder="casis_hebat_2025")
                    np = st.text_input("Password", type="password", placeholder="Min 6 karakter")
                    if st.form_submit_button("DAFTAR SEKARANG →", use_container_width=True):
                        if not nu or not np:
                            st.warning("⚠️ Isi semua field.")
                        elif len(np) < 6:
                            st.warning("⚠️ Password minimal 6 karakter.")
                        elif register_user(nu, np):
                            st.success(f"✅ Akun **{nu}** dibuat. Login untuk instruksi aktivasi.")
                        else:
                            st.error("❌ Username sudah dipakai.")

                st.markdown("""
                    <div class="pay-box">
                        <h5>💳 Cara Aktivasi</h5>
                        <div class="pay-row">1. Daftar lalu <strong>Login</strong> dengan akun baru</div>
                        <div class="pay-row">2. Transfer BRI: <strong>1234-5678-9012-3456</strong> — <strong>Rp 25.000</strong></div>
                        <div class="pay-row">3. WA bukti ke: <strong>0853-6637-4530</strong></div>
                        <div class="pay-row">✅ Aktivasi <strong>dalam 1×24 jam</strong></div>
                    </div>
                """, unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""
            <div class="footer-credit">
                🚀 <b>Project Development</b> &nbsp;|&nbsp;
                <a href="https://www.instagram.com/growing_together369" target="_blank">@growing_together369</a>
            </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════
# HOME PAGE
# ══════════════════════════════════════════════
def show_home():
    # ── Command Banner ──
    st.markdown(f"""
        <div class="hero-command">
            <div class="hero-rank">[ SISTEM AKTIF ]</div>
            <h1 class="hero-title">ARENA<br><span>KOMPETISI</span><br>CAT POLRI</h1>
            <p class="hero-sub">Simulasi psikotes paling dekat dengan kondisi ujian asli. Latih dirimu, kalahkan kompetitor.</p>
            <div class="stat-row">
                <div class="stat-chip"><span class="n">1.500+</span><span class="l">Casis Lulus</span></div>
                <div class="stat-chip"><span class="n">4</span><span class="l">Sesi Ujian</span></div>
                <div class="stat-chip"><span class="n">98%</span><span class="l">Akurasi Soal</span></div>
                <div class="stat-chip"><span class="n">24/7</span><span class="l">Akses Penuh</span></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    col_main, col_lb = st.columns([3, 2], gap="large")

    # ── LEFT: Arena Cards ──
    with col_main:
        st.markdown("""
            <div class="sec-head">
                <div class="sec-head-line"></div>
                <div class="sec-head-text">Pilih Sesi Latihan</div>
            </div>
        """, unsafe_allow_html=True)

        sesi_data = [
            {
                "key": "Pass Hand",
                "icon": "⚡",
                "title": "PASS HAND",
                "desc": "Uji koordinasi mata-tangan. Klik target sebanyak mungkin dalam 30 detik. Tidak ada benar/salah — hanya kecepatan.",
                "tags": ["APS", "30 Detik", "Ketangkasan"],
                "accent": "#fb6b00",
            },
            {
                "key": "Kecerdasan",
                "icon": "🧠",
                "title": "KECERDASAN",
                "desc": "Logika, numerik, verbal & Wawasan Kebangsaan. AI-generated soal autentik. Benar +5, Salah 0.",
                "tags": ["10 Soal", "+5 per Benar", "AI Soal"],
                "accent": "#39d353",
            },
            {
                "key": "Kecermatan",
                "icon": "🎯",
                "title": "KECERMATAN",
                "desc": "Temukan karakter yang hilang dari kunci 5-karakter. Kecepatan dan stabilitas diukur (Skor Ketahanan).",
                "tags": ["10 Soal", "Karakter Hilang", "Ketahanan"],
                "accent": "#58a6ff",
            },
            {
                "key": "Kepribadian",
                "icon": "🧬",
                "title": "KEPRIBADIAN",
                "desc": "Profil psikologi berdasarkan respons situasional. Tidak ada jawaban salah — setiap pilihan punya bobot berbeda.",
                "tags": ["10 Soal", "Skor 1–5", "Profiling"],
                "accent": "#bc8cff",
            },
        ]

        st.markdown('<div class="arena-grid">', unsafe_allow_html=True)
        for s in sesi_data:
            tags_html = "".join(f'<span class="meta-tag">{t}</span>' for t in s["tags"])
            st.markdown(f"""
                <div class="arena-card" style="--card-accent:{s['accent']};">
                    <span class="ac-icon">{s['icon']}</span>
                    <div class="ac-title">{s['title']}</div>
                    <div class="ac-desc">{s['desc']}</div>
                    <div class="ac-meta">{tags_html}</div>
                </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Tombol mulai sesi — 2x2 grid via st.columns
        r1c1, r1c2 = st.columns(2)
        r2c1, r2c2 = st.columns(2)
        btn_map = [
            (r1c1, "Pass Hand",   "⚡ MULAI PASS HAND"),
            (r1c2, "Kecerdasan",  "🧠 MULAI KECERDASAN"),
            (r2c1, "Kecermatan",  "🎯 MULAI KECERMATAN"),
            (r2c2, "Kepribadian", "🧬 MULAI KEPRIBADIAN"),
        ]
        for col, sesi_key, label in btn_map:
            with col:
                if st.button(label, key=f"start_{sesi_key}", use_container_width=True):
                    _init_sesi(sesi_key)
                    st.session_state.page = "simulasi"
                    st.rerun()

    # ── RIGHT: Leaderboard ──
    with col_lb:
        st.markdown("""
            <div class="sec-head">
                <div class="sec-head-line"></div>
                <div class="sec-head-text">🏆 Leaderboard</div>
            </div>
        """, unsafe_allow_html=True)

        filter_sesi = st.selectbox(
            "Filter:",
            ["Semua", "Pass Hand", "Kecerdasan", "Kecermatan", "Kepribadian"],
            label_visibility="collapsed",
            key="lb_filter"
        )
        rows = get_leaderboard(filter_sesi, limit=10)

        medal_map = {1: ("🥇", "r1"), 2: ("🥈", "r2"), 3: ("🥉", "r3")}
        rows_html = ""
        for i, row in enumerate(rows, 1):
            medal, cls = medal_map.get(i, ("", "rx"))
            uname = row.get("username", "—")
            skor  = row.get("skor", 0)
            sesi  = row.get("sesi", "—")
            rows_html += f"""
            <tr>
                <td><span class="lb-rank {cls}">{medal or f'#{i}'}</span></td>
                <td style="font-weight:600;">{uname}</td>
                <td><span class="lb-sesi">{sesi}</span></td>
                <td><span class="lb-score">{skor}</span></td>
            </tr>
            """

        if not rows_html:
            rows_html = '<tr><td colspan="4" style="text-align:center; color:var(--text-dim); padding:28px 0;">Belum ada data</td></tr>'

        st.markdown(f"""
            <div class="panel" style="padding:20px;">
                <table class="lb-table">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Username</th>
                            <th>Sesi</th>
                            <th>Skor</th>
                        </tr>
                    </thead>
                    <tbody>{rows_html}</tbody>
                </table>
            </div>
        """, unsafe_allow_html=True)

        # Highlight skor user sendiri
        my_scores = []
        try:
            res = supabase.table("scores")\
                .select("sesi, skor")\
                .eq("username", st.session_state.get("username", ""))\
                .order("skor", desc=True)\
                .limit(4)\
                .execute()
            my_scores = res.data or []
        except Exception:
            pass

        if my_scores:
            st.markdown("""
                <div class="sec-head" style="margin-top:20px;">
                    <div class="sec-head-line"></div>
                    <div class="sec-head-text">Skor Terbaik Lo</div>
                </div>
            """, unsafe_allow_html=True)
            my_rows = ""
            for s in my_scores:
                my_rows += f'<tr><td><span class="lb-sesi">{s["sesi"]}</span></td><td><span class="lb-score">{s["skor"]}</span></td></tr>'
            st.markdown(f"""
                <div class="panel" style="padding:16px 20px;">
                    <table class="lb-table">
                        <thead><tr><th>Sesi</th><th>Best</th></tr></thead>
                        <tbody>{my_rows}</tbody>
                    </table>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("""
        <div class="footer-credit">
            🚀 <b>Project Development</b> &nbsp;|&nbsp;
            <a href="https://www.instagram.com/growing_together369" target="_blank">@growing_together369</a>
        </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════
# SIMULASI HELPERS
# ══════════════════════════════════════════════
SOAL_TOTAL = 10
TIMER_DETIK = 30

SESI_CONFIG = {
    "Pass Hand":   {"icon": "⚡", "label": "PASS HAND",   "timer": 30},
    "Kecerdasan":  {"icon": "🧠", "label": "KECERDASAN",  "timer": 30},
    "Kecermatan":  {"icon": "🎯", "label": "KECERMATAN",  "timer": 25},
    "Kepribadian": {"icon": "🧬", "label": "KEPRIBADIAN", "timer": 45},
}

def _next_soal(sesi: str):
    if sesi == "Kecerdasan":
        return generate_soal_kecerdasan()
    elif sesi == "Kecermatan":
        return generate_kecermatan()
    elif sesi == "Kepribadian":
        return generate_soal_kepribadian()
    else:  # Pass Hand — config statis
        return generate_pass_hand()

def _init_sesi(sesi: str):
    cfg = SESI_CONFIG[sesi]
    st.session_state.sim_sesi      = sesi
    st.session_state.sim_step      = 1
    st.session_state.sim_skor      = 0
    st.session_state.sim_done      = False
    st.session_state.sim_end_time  = time.time() + cfg["timer"]
    st.session_state.sim_soal      = _next_soal(sesi)
    st.session_state.sim_waktu_kecermatan = []  # track ketahanan
    # Pass Hand state
    st.session_state.ph_klik       = 0
    st.session_state.ph_start      = time.time()
    st.session_state.ph_done       = False


def _advance_soal(sesi: str, skor_tambah: int = 0, waktu_jawab: float = 0.0):
    """Catat skor, maju ke soal berikutnya atau selesai."""
    st.session_state.sim_skor += skor_tambah
    if sesi == "Kecermatan" and waktu_jawab > 0:
        st.session_state.sim_waktu_kecermatan.append(waktu_jawab)

    if st.session_state.sim_step >= SOAL_TOTAL:
        st.session_state.sim_done = True
        save_score(
            st.session_state.get("username", "guest"),
            sesi,
            st.session_state.sim_skor,
        )
    else:
        st.session_state.sim_step     += 1
        cfg = SESI_CONFIG[sesi]
        st.session_state.sim_end_time  = time.time() + cfg["timer"]
        st.session_state.sim_soal      = _next_soal(sesi)


# ══════════════════════════════════════════════
# SIMULASI — MAIN RENDERER
# ══════════════════════════════════════════════
def show_simulation():
    sesi = st.session_state.get("sim_sesi", "Kecerdasan")
    cfg  = SESI_CONFIG[sesi]

    # ── Done Screen ──
    if st.session_state.get("sim_done", False):
        _show_result(sesi)
        return

    soal  = st.session_state.sim_soal
    step  = st.session_state.sim_step

    # ── Sim Header ──
    st.markdown(f"""
        <div class="sim-hdr">
            <div class="sim-hdr-left">
                <div class="sesi-label">[ SESI AKTIF ]</div>
                <div class="sesi-title">{cfg['icon']} {cfg['label']}</div>
            </div>
            <div style="display:flex; align-items:center; gap:14px; flex-wrap:wrap;">
                <div style="font-family:var(--mono); font-size:0.75rem; color:var(--text-sec);">
                    SOAL {step}/{SOAL_TOTAL if sesi != 'Pass Hand' else '—'}
                </div>
                <div id="timer-display" class="timer-box">--</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # ── Progress ──
    if sesi != "Pass Hand":
        pct = (step - 1) / SOAL_TOTAL * 100
        st.markdown(f"""
            <div class="prog-wrap">
                <div class="prog-fill" style="width:{pct}%;"></div>
            </div>
        """, unsafe_allow_html=True)

    # ── Timer live update via st.empty ──
    timer_slot = st.empty()

    # ── Sesi-specific rendering ──
    if sesi == "Pass Hand":
        _render_pass_hand(timer_slot)
    elif sesi == "Kecerdasan":
        _render_kecerdasan(soal, step, timer_slot)
    elif sesi == "Kecermatan":
        _render_kecermatan(soal, step, timer_slot)
    elif sesi == "Kepribadian":
        _render_kepribadian(soal, step, timer_slot)

    # ── Back button ──
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    if st.button("← Kembali ke Home", key="back_home"):
        st.session_state.page = "home"
        st.rerun()


def _timer_html(remaining: int) -> str:
    if remaining <= 5:
        cls = "crit"
    elif remaining <= 10:
        cls = "warn"
    else:
        cls = ""
    mins, secs = divmod(max(remaining, 0), 60)
    display = f"{mins:02d}:{secs:02d}"
    return f'<div class="timer-box {cls}" style="text-align:center;">{display}</div>'


# ── PASS HAND ──
def _render_pass_hand(timer_slot):
    if st.session_state.get("ph_done", False):
        elapsed = time.time() - st.session_state.ph_start
        result  = hitung_aps(st.session_state.ph_klik, elapsed)
        save_score(st.session_state.get("username","guest"), "Pass Hand", int(result["aps"] * 100))
        st.session_state.sim_done = True
        st.rerun()
        return

    dur   = SESI_CONFIG["Pass Hand"]["timer"]
    start = st.session_state.ph_start
    elapsed  = time.time() - start
    remaining = max(0, int(dur - elapsed))

    timer_slot.markdown(_timer_html(remaining), unsafe_allow_html=True)

    if remaining <= 0:
        st.session_state.ph_done = True
        st.rerun()
        return

    kliks = st.session_state.ph_klik
    pos   = st.session_state.get("ph_pos", {"x": 50, "y": 50})

    col_ph, col_info = st.columns([3, 1])
    with col_ph:
        st.markdown(f"""
            <div class="q-box" style="text-align:center; padding:36px 24px;">
                <div class="q-num">KLIK TARGET SECEPAT MUNGKIN</div>
                <div class="ph-counter">{kliks}</div>
                <div class="ph-label">KLIK VALID</div>
            </div>
        """, unsafe_allow_html=True)
        # Target button — position pseudo-random via re-render
        st.markdown(f"""
            <style>
            .target-btn-wrap {{ 
                display:flex; 
                justify-content:center; 
                margin: 16px 0;
                padding: {pos['y']}px 0 0 {pos['x']}px;
            }}
            </style>
        """, unsafe_allow_html=True)

        if st.button("🎯", key=f"ph_target_{kliks}", use_container_width=False):
            st.session_state.ph_klik += 1
            new_pos = posisi_target_acak(400, 100, 64)
            st.session_state.ph_pos  = new_pos
            st.rerun()

    with col_info:
        aps_live = round(kliks / max(elapsed, 0.1), 2)
        st.markdown(f"""
            <div class="panel-elevated" style="text-align:center;">
                <div style="font-family:var(--mono);font-size:0.6rem;color:var(--text-sec);letter-spacing:2px;text-transform:uppercase;">APS Live</div>
                <div style="font-family:var(--display);font-size:2.5rem;font-weight:900;color:var(--accent);line-height:1.1;margin-top:6px;">{aps_live}</div>
                <div style="font-family:var(--mono);font-size:0.6rem;color:var(--text-dim);margin-top:4px;">AKSI/DETIK</div>
            </div>
        """, unsafe_allow_html=True)

    # Refresh timer setiap detik
    time.sleep(0.9)
    st.rerun()


# ── KECERDASAN ──
def _render_kecerdasan(soal: dict, step: int, timer_slot):
    remaining = int(st.session_state.sim_end_time - time.time())
    timer_slot.markdown(_timer_html(remaining), unsafe_allow_html=True)

    # Auto-submit jika waktu habis
    if remaining <= 0:
        _advance_soal("Kecerdasan", skor_tambah=0)
        st.rerun()
        return

    st.markdown(f"""
        <div class="q-box">
            <div class="q-num">SOAL {step} &nbsp;/&nbsp; {soal.get('kategori','Kecerdasan')}</div>
            <div class="q-text">{soal.get('pertanyaan','—')}</div>
        </div>
    """, unsafe_allow_html=True)

    with st.form(key=f"form_kec_{step}"):
        pilihan = st.radio("Pilih jawaban:", soal.get("opsi", []), label_visibility="collapsed")
        if st.form_submit_button("KONFIRMASI →", use_container_width=True):
            huruf = pilihan.split(".")[0].strip()
            skor  = nilai_jawaban_kecerdasan(huruf, soal.get("jawaban","A"))
            _advance_soal("Kecerdasan", skor_tambah=skor)
            st.rerun()

    # Refresh timer
    time.sleep(1)
    st.rerun()


# ── KECERMATAN ──
def _render_kecermatan(soal: dict, step: int, timer_slot):
    remaining = int(st.session_state.sim_end_time - time.time())
    timer_slot.markdown(_timer_html(remaining), unsafe_allow_html=True)

    if remaining <= 0:
        # Auto-submit salah, catat waktu maksimal
        _advance_soal("Kecermatan", skor_tambah=0, waktu_jawab=float(SESI_CONFIG["Kecermatan"]["timer"]))
        st.rerun()
        return

    kunci_html = "".join(f'<div class="kunci-char">{c}</div>' for c in soal.get("kunci", []))
    st.markdown(f"""
        <div class="q-box">
            <div class="q-num">KUNCI REFERENSI — SOAL {step}</div>
            <div style="margin-bottom:14px;">
                <div class="kunci-grid">{kunci_html}</div>
            </div>
            <div class="q-text">Karakter apa yang <b style="color:var(--red-alert);">HILANG</b> dari tampilan berikut?</div>
            <div class="tampilan-box">{soal.get('tampilan','')}&nbsp;<span class="missing">?</span></div>
        </div>
    """, unsafe_allow_html=True)

    with st.form(key=f"form_cer_{step}"):
        pilihan = st.radio("Pilih karakter:", soal.get("opsi", []), label_visibility="collapsed", horizontal=True)
        if st.form_submit_button("KONFIRMASI →", use_container_width=True):
            waktu = catat_waktu_jawab(soal)
            skor  = nilai_jawaban_kecermatan(str(pilihan).strip(), soal.get("jawaban",""))
            _advance_soal("Kecermatan", skor_tambah=skor, waktu_jawab=waktu)
            st.rerun()

    time.sleep(1)
    st.rerun()


# ── KEPRIBADIAN ──
def _render_kepribadian(soal: dict, step: int, timer_slot):
    remaining = int(st.session_state.sim_end_time - time.time())
    timer_slot.markdown(_timer_html(remaining), unsafe_allow_html=True)

    if remaining <= 0:
        _advance_soal("Kepribadian", skor_tambah=1)
        st.rerun()
        return

    st.markdown(f"""
        <div class="q-box">
            <div class="q-num">SITUASI {step} &nbsp;/&nbsp; KEPRIBADIAN</div>
            <div class="q-text">{soal.get('pertanyaan','—')}</div>
        </div>
    """, unsafe_allow_html=True)

    with st.form(key=f"form_kep_{step}"):
        pilihan = st.radio("Pilih respons:", soal.get("opsi", []), label_visibility="collapsed")
        if st.form_submit_button("KONFIRMASI →", use_container_width=True):
            huruf = pilihan.split(".")[0].strip()
            skor  = nilai_jawaban_kepribadian(huruf, soal.get("skor", {}))
            _advance_soal("Kepribadian", skor_tambah=skor)
            st.rerun()

    time.sleep(1)
    st.rerun()


# ── RESULT SCREEN ──
def _show_result(sesi: str):
    skor = st.session_state.sim_skor

    # Kalkulasi konteks sesi
    if sesi == "Pass Hand":
        elapsed = time.time() - st.session_state.get("ph_start", time.time())
        result  = hitung_aps(st.session_state.get("ph_klik", 0), elapsed)
        skor_display = result["aps"]
        unit = "APS"
        max_ref = 5.0
        verdict = result["kategori"]
        extra_html = f"""
            <div style="font-family:var(--mono);font-size:0.75rem;color:var(--text-sec);margin-top:16px;">
                {result['jumlah_klik']} klik &nbsp;/&nbsp; {result['durasi_detik']}s &nbsp;/&nbsp; {result['deskripsi']}
            </div>
        """
    elif sesi == "Kecerdasan":
        skor_display = skor
        unit = "PTS"
        max_ref = SOAL_TOTAL * 5
        if skor >= max_ref * 0.8:   verdict = "🏆 EXCELLENT — Performa sangat tinggi"
        elif skor >= max_ref * 0.6: verdict = "✅ BAIK — Di atas rata-rata"
        else:                        verdict = "📈 PERLU LATIHAN LEBIH"
        extra_html = ""
    elif sesi == "Kecermatan":
        skor_display = skor
        unit = "BENAR"
        max_ref = SOAL_TOTAL
        ketahanan_data = hitung_ketahanan(st.session_state.get("sim_waktu_kecermatan", []))
        if skor >= max_ref * 0.8:   verdict = "🏆 CERMAT & CEPAT"
        elif skor >= max_ref * 0.6: verdict = "✅ CUKUP BAIK"
        else:                        verdict = "📈 TINGKATKAN KETELITIAN"
        extra_html = f"""
            <div style="margin-top:16px; background:var(--bg-elevated); border-radius:6px; padding:12px 16px; display:inline-block;">
                <span style="font-family:var(--mono);font-size:0.7rem;color:var(--accent);">KETAHANAN</span>
                <div style="font-family:var(--display);font-size:2rem;font-weight:900;color:var(--text-pri);">
                    {ketahanan_data['skor_ketahanan']}<span style="font-size:1rem;color:var(--text-sec);">/100</span>
                </div>
                <div style="font-size:0.75rem;color:var(--text-sec);">{ketahanan_data['kategori']}</div>
            </div>
        """
    else:  # Kepribadian
        skor_display = skor
        unit = "PTS"
        max_ref = SOAL_TOTAL * 5
        rata = round(skor / SOAL_TOTAL, 2)
        if rata >= 4:   verdict = "🏆 PROFIL SANGAT SESUAI"
        elif rata >= 3: verdict = "✅ PROFIL BAIK"
        else:            verdict = "📊 PERLU EVALUASI DIRI"
        extra_html = f'<div style="font-family:var(--mono);font-size:0.75rem;color:var(--text-sec);margin-top:10px;">Rata-rata per soal: {rata}</div>'

    pct = min(int(float(skor_display) / max_ref * 100), 100)

    st.markdown(f"""
        <div class="result-box">
            <div class="result-label">[ SESI {sesi.upper()} — SELESAI ]</div>
            <div class="result-score">{skor_display}</div>
            <div style="font-family:var(--mono);font-size:0.75rem;color:var(--text-sec);">{unit}</div>
            <div class="result-bar-wrap">
                <div class="result-bar-fill" style="width:{pct}%;"></div>
            </div>
            <div class="result-verdict">{verdict}</div>
            {extra_html}
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 ULANGI SESI INI", use_container_width=True):
            _init_sesi(sesi)
            st.rerun()
    with col2:
        if st.button("🏠 KEMBALI KE HOME", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()


# ══════════════════════════════════════════════
# MAIN ROUTING
# ══════════════════════════════════════════════
def main():
    # Init state
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "page" not in st.session_state:
        st.session_state.page = "home"

    if not st.session_state.logged_in:
        show_auth()
        return

    # ── Sidebar ──
    with st.sidebar:
        st.markdown("""
            <div style="text-align:center; padding:20px 0 14px;">
                <div style="font-family:'JetBrains Mono',monospace; font-size:0.6rem;
                     color:#fb6b00; letter-spacing:2px; text-transform:uppercase; margin-bottom:8px;">
                    [ SISTEM AKTIF ]
                </div>
                <div style="font-family:'Barlow Condensed',sans-serif; font-size:1.5rem;
                     font-weight:900; color:#e6edf3; letter-spacing:-0.5px;">
                    PSYCHOTECH
                </div>
            </div>
        """, unsafe_allow_html=True)
        st.divider()

        if st.button("🏠  HOME", use_container_width=True, key="nav_home"):
            st.session_state.page = "home"
            st.rerun()

        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        st.markdown("<div style='font-family:JetBrains Mono;font-size:0.6rem;color:#484f58;letter-spacing:2px;text-transform:uppercase;margin-bottom:6px;'>MULAI SESI</div>", unsafe_allow_html=True)
        for sesi_key in ["Pass Hand", "Kecerdasan", "Kecermatan", "Kepribadian"]:
            cfg = SESI_CONFIG[sesi_key]
            if st.button(f"{cfg['icon']}  {cfg['label']}", use_container_width=True, key=f"nav_{sesi_key}"):
                _init_sesi(sesi_key)
                st.session_state.page = "simulasi"
                st.rerun()

        st.divider()
        st.markdown(f"<div style='font-size:0.78rem;color:#7d8590;'>👤 <b style='color:#e6edf3;'>{st.session_state.get('username','—')}</b></div>", unsafe_allow_html=True)
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button("🚪 LOGOUT", use_container_width=True, key="nav_logout"):
            st.session_state.logged_in = False
            st.rerun()

        st.markdown("""
            <div style="text-align:center; margin-top:16px; font-size:0.72rem; color:#484f58;">
                🚀 <a href="https://www.instagram.com/growing_together369" target="_blank"
                   style="color:#fb6b00;text-decoration:none;font-weight:700;">@growing_together369</a>
            </div>
        """, unsafe_allow_html=True)

    # ── Page Router ──
    page = st.session_state.page
    if page == "home":
        show_home()
    elif page == "simulasi":
        show_simulation()


if __name__ == "__main__":
    main()
