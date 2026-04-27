"""
app.py — Psychotech Polri | Arena CAT v4.0 (Marathon Edition)
Changelog v4.0:
- HTML Cleaned: Tidak ada lagi <div> terekspos karena salah parsing Markdown
- JS Injected: Anti-Click Kanan, Anti-Copy, Auto-Scroll tiap render
- Alur Maraton: Pass Hand → Kecerdasan → Kepribadian → Kecermatan (satu alur kontinu)
- Nilai hanya muncul di akhir semua sesi, dengan status MS/TMS (passing grade 61)
- Halaman Evaluasi: Review jawaban salah per sesi setelah nilai akhir keluar
- Skor 0-100 per sesi: Kecerdasan & Kecermatan (Benar/Total*100), Kepribadian (Likert→100)
- Pass Hand: skor ideal-match ke 0-100
"""

import streamlit as st
import time
import random
import streamlit.components.v1 as components
from engine import (
    generate_soal,
    skor_sesi_pass_hand,
    skor_sesi_kecerdasan,
    skor_sesi_kepribadian,
    skor_sesi_kecermatan,
    rekap_maraton,
    catat_waktu_jawab,
    LIKERT_OPSI,
    URUTAN_MARATON,
    SOAL_PER_SESI,
    PASSING_GRADE,
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
# JAVASCRIPT PROTEKSI & AUTO-SCROLL
# ══════════════════════════════════════════════
components.html(
    """
    <script>
    const parentDoc = window.parent.document;
    
    // Anti klik kanan
    parentDoc.addEventListener('contextmenu', event => event.preventDefault());
    
    // Anti select, copy, print (Ctrl+C, Ctrl+S, dll)
    parentDoc.addEventListener('keydown', event => {
        if (event.ctrlKey || event.metaKey) {
            if (['c', 'p', 's', 'u', 'a'].includes(event.key.toLowerCase())) {
                event.preventDefault();
            }
        }
    });

    // Auto scroll ke paling atas tiap halaman render ulang
    window.parent.scrollTo({top: 0, behavior: 'smooth'});
    </script>
    """,
    height=0, width=0,
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
    --blue-info:    #58a6ff;
    --purple-kep:   #bc8cff;
    --text-pri:     #e6edf3;
    --text-sec:     #7d8590;
    --text-dim:     #484f58;
    --mono:         'JetBrains Mono', monospace;
    --display:      'Barlow Condensed', sans-serif;
    --body:         'Barlow', sans-serif;
    --r-sm: 6px; --r-md: 10px; --r-lg: 16px;
}
html, body, [class*="css"] { font-family: var(--body) !important; background-color: var(--bg-void) !important; color: var(--text-pri) !important; }
.stApp {
    background:
        radial-gradient(ellipse at 20% 0%, rgba(251,107,0,0.07) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 100%, rgba(57,211,83,0.04) 0%, transparent 45%),
        var(--bg-void) !important;
    min-height: 100vh;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.2rem !important; padding-bottom: 3rem !important; max-width: 1200px !important; }
.stApp::after {
    content: '';
    position: fixed; inset: 0;
    background: repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.03) 2px, rgba(0,0,0,0.03) 4px);
    pointer-events: none; z-index: 9999;
}

/* ── Anti-Copas (Layer 2 CSS) ── */
.no-select, .q-box, .pernyataan-box, .kunci-grid, .tampilan-box, .q-text, p, div, span {
    -webkit-user-select: none !important;
    -moz-user-select: none !important;
    -ms-user-select: none !important;
    user-select: none !important;
}

/* ── Watermark ── */
.sim-watermark {
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    display: flex; align-items: center; justify-content: center;
    pointer-events: none; z-index: 1000; overflow: hidden;
}
.sim-watermark-text {
    font-family: var(--display); font-size: 4.5rem; font-weight: 900;
    color: rgba(251,107,0,0.045); text-transform: uppercase;
    letter-spacing: 6px; transform: rotate(-30deg);
    white-space: nowrap;
    text-align: center; line-height: 1.2;
}
.sim-watermark-text span {
    display: block; font-size: 2rem; letter-spacing: 10px;
    color: rgba(255,255,255,0.025);
    margin-top: 6px;
}

/* ── Panels ── */
.panel { background: var(--bg-panel); border: 1px solid var(--border-dim); border-radius: var(--r-lg); padding: 28px; margin-bottom: 20px; }
.panel-sm { background: var(--bg-surface); border: 1px solid var(--border-dim); border-radius: var(--r-md); padding: 18px; }

/* ── Hero ── */
.hero-command {
    background: linear-gradient(135deg,#0d1117 0%,#161b22 50%,#1a1f2e 100%);
    border: 1px solid var(--border-dim);
    border-top: 2px solid var(--accent);
    border-radius: var(--r-lg); padding: 40px 32px 36px;
    position: relative; overflow: hidden; margin-bottom: 24px;
}
.hero-command::before {
    content: 'PSYCHOTECH'; position: absolute; right: -20px; top: -10px;
    font-family: var(--display); font-size: 9rem; font-weight: 900;
    color: rgba(255,255,255,0.02); pointer-events: none; letter-spacing: -4px;
}
.hero-rank { display:inline-flex; align-items:center; gap:8px; background:var(--accent-dim); border:1px solid var(--border-glow); border-radius:4px; padding:4px 12px; font-family:var(--mono); font-size:0.7rem; color:var(--accent); letter-spacing:2px; text-transform:uppercase; margin-bottom:14px; }
.hero-title { font-family:var(--display); font-size:clamp(2.2rem,5vw,3.6rem); font-weight:900; color:var(--text-pri); line-height:1.0; margin:0 0 10px; letter-spacing:-1px; }
.hero-title span { color:var(--accent); }
.hero-sub { font-size:0.95rem; color:var(--text-sec); margin:0 0 24px; font-weight:300; max-width:520px; }
.stat-row { display:flex; gap:10px; flex-wrap:wrap; }
.stat-chip { background:var(--bg-elevated); border:1px solid var(--border-dim); border-radius:var(--r-sm); padding:10px 16px; text-align:center; min-width:80px; }
.stat-chip .n { font-family:var(--display); font-size:1.5rem; font-weight:800; color:var(--accent); display:block; line-height:1; }
.stat-chip .l { font-size:0.65rem; color:var(--text-sec); text-transform:uppercase; letter-spacing:0.8px; margin-top:3px; display:block; }

/* ── Section header ── */
.sec-head { display:flex; align-items:center; gap:10px; margin-bottom:14px; }
.sec-head-line { width:3px; height:20px; background:var(--accent); border-radius:2px; flex-shrink:0; }
.sec-head-text { font-family:var(--display); font-size:1.15rem; font-weight:700; color:var(--text-pri); letter-spacing:0.5px; text-transform:uppercase; }

/* ── Arena Cards ── */
.arena-grid { display:grid; grid-template-columns:repeat(2,1fr); gap:12px; margin-bottom:20px; }
.arena-card { background:var(--bg-surface); border:1px solid var(--border-dim); border-radius:var(--r-md); padding:20px 18px 18px; position:relative; overflow:hidden; }
.arena-card::before { content:''; position:absolute; top:0; left:0; right:0; height:2px; background:var(--card-accent,var(--accent)); opacity:0.7; }
.arena-card .ac-icon { font-size:1.8rem; display:block; margin-bottom:8px; }
.arena-card .ac-title { font-family:var(--display); font-size:1.05rem; font-weight:800; color:var(--text-pri); text-transform:uppercase; letter-spacing:0.5px; margin-bottom:5px; }
.arena-card .ac-desc { font-size:0.78rem; color:var(--text-sec); line-height:1.5; margin-bottom:12px; }
.arena-card .ac-meta { display:flex; gap:6px; flex-wrap:wrap; }
.meta-tag { font-family:var(--mono); font-size:0.63rem; color:var(--accent); background:var(--accent-dim); border:1px solid var(--border-glow); border-radius:3px; padding:2px 6px; text-transform:uppercase; }

/* ── Maraton Progress Bar ── */
.maraton-track { display:flex; gap:8px; margin-bottom:20px; flex-wrap:wrap; }
.maraton-step { flex:1; min-width:100px; background:var(--bg-elevated); border:1px solid var(--border-dim); border-radius:var(--r-sm); padding:10px 12px; text-align:center; position:relative; }
.maraton-step.active { border-color:var(--accent); background:var(--accent-dim); }
.maraton-step.done { border-color:rgba(57,211,83,0.4); background:rgba(57,211,83,0.07); }
.maraton-step .ms-icon { font-size:1.3rem; display:block; }
.maraton-step .ms-label { font-family:var(--display); font-size:0.75rem; font-weight:700; text-transform:uppercase; letter-spacing:0.5px; color:var(--text-sec); margin-top:4px; display:block; }
.maraton-step.active .ms-label { color:var(--accent); }
.maraton-step.done .ms-label { color:var(--green-ok); }
.maraton-step .ms-skor { font-family:var(--mono); font-size:0.65rem; color:var(--green-ok); display:block; margin-top:2px; }

/* ── Leaderboard ── */
.lb-table { width:100%; border-collapse:collapse; font-size:0.86rem; }
.lb-table th { font-family:var(--mono); font-size:0.62rem; text-transform:uppercase; letter-spacing:1px; color:var(--text-dim); padding:8px 10px; border-bottom:1px solid var(--border-dim); text-align:left; }
.lb-table td { padding:9px 10px; border-bottom:1px solid var(--border-dim); color:var(--text-pri); vertical-align:middle; }
.lb-table tr:last-child td { border-bottom:none; }
.lb-table tr:hover td { background:var(--bg-elevated); }
.lb-rank { font-family:var(--mono); font-weight:700; font-size:0.9rem; }
.lb-rank.r1{color:var(--gold);} .lb-rank.r2{color:#c0c0c0;} .lb-rank.r3{color:#cd7f32;} .lb-rank.rx{color:var(--text-dim);}
.lb-score { font-family:var(--display); font-size:1.1rem; font-weight:800; color:var(--accent); }
.lb-sesi { font-family:var(--mono); font-size:0.68rem; color:var(--text-sec); background:var(--bg-elevated); border-radius:3px; padding:2px 6px; }
.lb-row-1 td{background:rgba(227,179,65,0.05)!important;}
.lb-row-2 td{background:rgba(192,192,192,0.04)!important;}
.lb-row-3 td{background:rgba(205,127,50,0.04)!important;}

/* ── Sim Header ── */
.sim-hdr { background:var(--bg-panel); border:1px solid var(--border-dim); border-top:2px solid var(--accent); border-radius:var(--r-md); padding:14px 18px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; margin-bottom:14px; }
.sim-hdr-left .sesi-label { font-family:var(--mono); font-size:0.62rem; color:var(--accent); letter-spacing:2px; text-transform:uppercase; margin-bottom:4px; }
.sim-hdr-left .sesi-title { font-family:var(--display); font-size:1.35rem; font-weight:800; color:var(--text-pri); letter-spacing:0.5px; }
.timer-box { background:var(--bg-elevated); border:1px solid var(--border-dim); border-radius:var(--r-sm); padding:7px 16px; font-family:var(--mono); font-size:1.4rem; font-weight:700; color:var(--green-ok); min-width:90px; text-align:center; transition:color 0.3s,border-color 0.3s; }
.timer-box.warn { color:var(--gold); border-color:rgba(227,179,65,0.4); }
.timer-box.crit { color:var(--red-alert); border-color:rgba(248,81,73,0.4); animation:pulse-red 0.5s ease-in-out infinite alternate; }
@keyframes pulse-red { from{box-shadow:none;} to{box-shadow:0 0 12px rgba(248,81,73,0.35);} }

/* ── Question Box ── */
.q-box { background:var(--bg-surface); border:1px solid var(--border-dim); border-radius:var(--r-md); padding:24px 22px; margin-bottom:18px; }
.q-num { font-family:var(--mono); font-size:0.63rem; color:var(--accent); letter-spacing:2px; text-transform:uppercase; margin-bottom:10px; }
.q-text { font-size:1rem; color:var(--text-pri); line-height:1.7; font-weight:400; }

/* ── Likert ── */
.likert-label { font-family:var(--mono); font-size:0.62rem; color:var(--text-sec); letter-spacing:1.5px; text-transform:uppercase; margin-bottom:10px; }
.arah-badge { display:inline-block; font-family:var(--mono); font-size:0.6rem; letter-spacing:1px; text-transform:uppercase; padding:2px 8px; border-radius:3px; margin-top:8px; }
.arah-badge.positif { background:rgba(57,211,83,0.12); border:1px solid rgba(57,211,83,0.3); color:#39d353; }
.arah-badge.negatif { background:rgba(248,81,73,0.12); border:1px solid rgba(248,81,73,0.3); color:#f85149; }

/* ── Kecermatan ── */
.kunci-grid { display:flex; gap:7px; flex-wrap:wrap; margin-bottom:14px; }
.kunci-char { background:var(--bg-elevated); border:1px solid var(--accent); border-radius:var(--r-sm); padding:9px 14px; font-family:var(--mono); font-size:1.05rem; font-weight:700; color:var(--accent); min-width:42px; text-align:center; }
.tampilan-box { font-family:var(--mono); font-size:1.3rem; letter-spacing:7px; color:var(--text-pri); background:var(--bg-elevated); border:1px solid var(--border-dim); border-radius:var(--r-sm); padding:12px 18px; display:inline-block; margin:10px 0; }
.missing-hint { font-family:var(--mono); font-size:0.68rem; color:var(--text-sec); margin-top:6px; }

/* ── Pass Hand ── */
.pernyataan-box { background:var(--bg-surface); border:1px solid var(--border-dim); border-left:3px solid var(--accent); border-radius:var(--r-md); padding:24px 22px; margin-bottom:18px; font-size:1.05rem; color:var(--text-pri); line-height:1.7; }

/* ── Nav ── */
.nav-progress { font-family:var(--mono); font-size:0.68rem; color:var(--text-sec); text-align:center; margin-bottom:10px; }
.answered-badge { display:inline-block; background:var(--accent-dim); border:1px solid var(--border-glow); border-radius:3px; padding:2px 8px; font-family:var(--mono); font-size:0.62rem; color:var(--accent); text-transform:uppercase; margin-left:8px; }

/* ── Progress Bar ── */
.prog-wrap { background:var(--bg-elevated); border-radius:3px; height:4px; margin-bottom:16px; overflow:hidden; }
.prog-fill { height:100%; background:linear-gradient(90deg,var(--accent),var(--accent-ember)); border-radius:3px; transition:width 0.3s ease; }

/* ── Hasil Akhir ── */
.final-box { background:linear-gradient(135deg,var(--bg-panel) 0%,var(--bg-surface) 100%); border:1px solid var(--border-glow); border-top:3px solid var(--accent); border-radius:var(--r-lg); padding:40px 28px; text-align:center; margin-bottom:24px; }
.final-label { font-family:var(--mono); font-size:0.63rem; color:var(--accent); letter-spacing:3px; text-transform:uppercase; margin-bottom:10px; }
.final-score { font-family:var(--display); font-size:5rem; font-weight:900; color:var(--text-pri); line-height:1; margin:6px 0 4px; }
.final-status-ms  { font-family:var(--display); font-size:1.8rem; font-weight:900; color:var(--green-ok); letter-spacing:2px; }
.final-status-tms { font-family:var(--display); font-size:1.8rem; font-weight:900; color:var(--red-alert); letter-spacing:2px; }
.final-bar-wrap { background:var(--bg-elevated); border-radius:3px; height:8px; max-width:320px; margin:16px auto 0; overflow:hidden; }
.final-bar-fill-ms  { height:100%; border-radius:3px; background:linear-gradient(90deg,#39d353,#2ea043); transition:width 0.8s ease; }
.final-bar-fill-tms { height:100%; border-radius:3px; background:linear-gradient(90deg,#f85149,#da3633); transition:width 0.8s ease; }

/* ── Skor Per Sesi ── */
.skor-grid { display:grid; grid-template-columns:repeat(2,1fr); gap:12px; margin:20px 0; }
.skor-card { background:var(--bg-elevated); border:1px solid var(--border-dim); border-radius:var(--r-md); padding:16px; text-align:center; }
.skor-card .sk-label { font-family:var(--mono); font-size:0.6rem; color:var(--text-sec); letter-spacing:1.5px; text-transform:uppercase; display:block; margin-bottom:6px; }
.skor-card .sk-val { font-family:var(--display); font-size:2.2rem; font-weight:900; color:var(--accent); display:block; line-height:1; }
.skor-card .sk-bar-wrap { background:var(--bg-surface); border-radius:2px; height:4px; margin-top:8px; overflow:hidden; }
.skor-card .sk-bar-fill { height:100%; border-radius:2px; background:var(--accent); }

/* ── Evaluasi / Review ── */
.eval-item { background:var(--bg-surface); border:1px solid var(--border-dim); border-radius:var(--r-md); padding:16px 18px; margin-bottom:10px; }
.eval-item.salah { border-left:3px solid var(--red-alert); }
.eval-item.benar { border-left:3px solid var(--green-ok); }
.eval-q { font-size:0.9rem; color:var(--text-pri); line-height:1.6; margin-bottom:8px; }
.eval-ans { font-family:var(--mono); font-size:0.75rem; display:flex; gap:12px; flex-wrap:wrap; margin-bottom:6px; }
.eval-ans .user-ans { color:var(--red-alert); }
.eval-ans .correct-ans { color:var(--green-ok); }
.eval-pembahasan { font-size:0.8rem; color:var(--text-sec); line-height:1.6; background:var(--bg-elevated); border-radius:var(--r-sm); padding:10px 12px; margin-top:8px; }

/* ── Auth ── */
.auth-shell { max-width:420px; margin:60px auto 0; }
.auth-logo { text-align:center; margin-bottom:26px; }
.auth-logo .badge { font-family:var(--mono); font-size:0.7rem; color:var(--accent); letter-spacing:2px; text-transform:uppercase; margin-bottom:10px; display:block; }
.auth-logo .name { font-family:var(--display); font-size:2.3rem; font-weight:900; color:var(--text-pri); letter-spacing:-1px; }
.auth-logo .name span { color:var(--accent); }
.auth-logo .sub { font-size:0.8rem; color:var(--text-sec); margin-top:4px; }
.pay-box { background:var(--bg-surface); border:1px solid var(--border-glow); border-left:3px solid var(--accent); border-radius:var(--r-md); padding:16px 14px; margin-top:14px; }
.pay-box h5 { font-family:var(--display); font-size:0.92rem; font-weight:700; color:var(--accent); text-transform:uppercase; letter-spacing:1px; margin:0 0 10px; }
.pay-row { font-size:0.8rem; color:var(--text-sec); padding:5px 0; border-bottom:1px solid var(--border-dim); display:flex; gap:7px; }
.pay-row:last-child { border-bottom:none; }
.pay-row strong { color:var(--text-pri); }

/* ── Streamlit overrides ── */
.stButton > button {
    background:var(--accent) !important; color:#000 !important; border:none !important;
    border-radius:var(--r-sm) !important; font-family:var(--display) !important;
    font-size:0.95rem !important; font-weight:700 !important; letter-spacing:0.5px !important;
    text-transform:uppercase !important; padding:9px 20px !important;
    transition:all 0.15s ease !important; width:100%;
}
.stButton > button:hover { background:var(--accent-ember) !important; transform:translateY(-1px) !important; box-shadow:0 6px 18px rgba(251,107,0,0.35) !important; }
.stTextInput > div > div > input { background:var(--bg-elevated) !important; border:1px solid var(--border-dim) !important; border-radius:var(--r-sm) !important; color:var(--text-pri) !important; font-family:var(--body) !important; font-size:0.88rem !important; padding:9px 13px !important; }
.stTextInput > div > div > input:focus { border-color:var(--accent) !important; box-shadow:0 0 0 2px var(--accent-dim) !important; }
.stTextInput > label,.stSelectbox > label,.stRadio > label { color:var(--text-sec) !important; font-size:0.78rem !important; font-family:var(--mono) !important; letter-spacing:1px !important; text-transform:uppercase !important; }
.stSelectbox > div > div { background:var(--bg-elevated) !important; border:1px solid var(--border-dim) !important; border-radius:var(--r-sm) !important; color:var(--text-pri) !important; }
.stTabs [data-baseweb="tab-list"] { background:var(--bg-elevated) !important; border-radius:var(--r-sm) !important; padding:4px !important; gap:4px !important; border:1px solid var(--border-dim) !important; }
.stTabs [data-baseweb="tab"] { border-radius:5px !important; font-family:var(--display) !important; font-size:0.92rem !important; font-weight:700 !important; text-transform:uppercase !important; letter-spacing:0.5px !important; color:var(--text-sec) !important; padding:7px 14px !important; }
.stTabs [aria-selected="true"] { background:var(--bg-panel) !important; color:var(--accent) !important; border:1px solid var(--border-glow) !important; }
.stRadio > div { gap:7px !important; }
.stRadio label { background:var(--bg-elevated) !important; border:1px solid var(--border-dim) !important; border-radius:var(--r-sm) !important; padding:9px 13px !important; color:var(--text-pri) !important; font-family:var(--body) !important; font-size:0.88rem !important; transition:all 0.15s !important; cursor:pointer !important; }
.stRadio label:hover { border-color:var(--border-glow) !important; background:var(--bg-surface) !important; }
.stSidebar { background:var(--bg-panel) !important; border-right:1px solid var(--border-dim) !important; }
div[data-testid="stProgress"] > div { background:var(--bg-elevated) !important; }
div[data-testid="stProgress"] > div > div { background:var(--accent) !important; }

/* ── Footer ── */
.footer-credit { text-align:center; padding:22px 0 8px; font-size:0.76rem; color:var(--text-dim); }
.footer-credit a { color:var(--accent); text-decoration:none; font-weight:600; }

@media (max-width:640px) {
    .arena-grid,.skor-grid,.maraton-track { grid-template-columns:1fr; flex-direction:column; }
    .stat-row { flex-direction:column; }
    .final-score { font-size:3.8rem; }
    .hero-command { padding:28px 20px 24px; }
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════
# SESI CONFIG
# ══════════════════════════════════════════════
SESI_CONFIG = {
    "Pass Hand":   {"icon": "📋", "label": "PASS HAND",   "timer": 45, "color": "#fb6b00"},
    "Kecerdasan":  {"icon": "🧠", "label": "KECERDASAN",  "timer": 35, "color": "#39d353"},
    "Kepribadian": {"icon": "🧬", "label": "KEPRIBADIAN", "timer": 45, "color": "#bc8cff"},
    "Kecermatan":  {"icon": "🎯", "label": "KECERMATAN",  "timer": 20, "color": "#58a6ff"},
}

# ══════════════════════════════════════════════
# DB HELPERS
# ══════════════════════════════════════════════
def login_user(username: str, password: str):
    res = supabase.table("users").select("*").eq("username", username).eq("password", password).execute()
    if res.data:
        user = res.data[0]
        if user.get("status") == "pending":
            st.markdown(
'<div class="pay-box">'
'<h5>⏳ Akun Belum Aktif</h5>'
'<div class="pay-row">📱 Kirim bukti bayar via <strong>WhatsApp</strong></div>'
'<div class="pay-row">📞 <strong>0853-6637-4530</strong></div>'
'<div class="pay-row">🏦 SEABANK: <strong>1234-5678-9012-3456</strong> a.n. Growing Together</div>'
'<div class="pay-row">💰 Biaya Aktivasi: <strong>Rp 25.000</strong></div>'
'</div>', unsafe_allow_html=True)
            st.stop()
        return user
    return None

def register_user(username: str, password: str) -> bool:
    try:
        supabase.table("users").insert({"username": username, "password": password, "status": "pending"}).execute()
        return True
    except Exception:
        return False

def save_score_maraton(username: str, rata_rata: int, status: str):
    try:
        supabase.table("scores").insert({
            "username": username,
            "sesi": "MARATON",
            "skor": rata_rata,
            "status": status,
        }).execute()
    except Exception:
        pass

def get_leaderboard(limit: int = 5) -> list:
    try:
        res = supabase.table("scores").select("username, skor, status").eq("sesi", "MARATON").order("skor", desc=True).limit(limit).execute()
        return res.data or []
    except Exception:
        return []

# ══════════════════════════════════════════════
# LEADERBOARD COMPONENT
# ══════════════════════════════════════════════
def display_leaderboard():
    rows = get_leaderboard(limit=5)
    medal_map = {1: ("🥇", "r1"), 2: ("🥈", "r2"), 3: ("🥉", "r3")}
    rows_html = ""
    for i, row in enumerate(rows, 1):
        medal, cls = medal_map.get(i, ("", "rx"))
        uname  = row.get("username", "—")
        skor   = row.get("skor", 0)
        status = row.get("status", "—")
        st_color = "#39d353" if status == "MS" else "#f85149"
        row_cls = f"lb-row-{i}" if i <= 3 else ""
        
        # Flushed to avoid markdown block rendering
        rows_html += f'<tr class="{row_cls}">'
        rows_html += f'<td><span class="lb-rank {cls}">{medal or f"#{i}"}</span></td>'
        rows_html += f'<td style="font-weight:600;">{uname}</td>'
        rows_html += f'<td><span style="font-family:var(--mono);font-size:0.72rem;color:{st_color};font-weight:700;">{status}</span></td>'
        rows_html += f'<td><span class="lb-score">{skor}</span></td>'
        rows_html += '</tr>'

    if not rows_html:
        rows_html = '<tr><td colspan="4" style="text-align:center;color:var(--text-dim);padding:24px 0;">Belum ada data</td></tr>'

    st.markdown(
'<div class="panel" style="padding:18px;">'
'<table class="lb-table">'
'<thead><tr><th>#</th><th>Username</th><th>Status</th><th>Rata-rata</th></tr></thead>'
f'<tbody>{rows_html}</tbody>'
'</table>'
'</div>', unsafe_allow_html=True)

    try:
        res = supabase.table("scores").select("skor, status").eq("username", st.session_state.get("username", "")).eq("sesi", "MARATON").order("skor", desc=True).limit(1).execute()
        my = res.data or []
    except Exception:
        my = []

    if my:
        best = my[0]
        st_color = "#39d353" if best.get("status") == "MS" else "#f85149"
        st.markdown(
'<div class="panel-sm" style="margin-top:12px;text-align:center;">'
'<span style="font-family:var(--mono);font-size:0.62rem;color:var(--text-sec);letter-spacing:1.5px;text-transform:uppercase;">BEST SCORE LO</span>'
f'<div style="font-family:var(--display);font-size:2.4rem;font-weight:900;color:{st_color};">{best["skor"]}</div>'
f'<div style="font-family:var(--mono);font-size:0.75rem;color:{st_color};">● {best.get("status","—")}</div>'
'</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════
# AUTH PAGE
# ══════════════════════════════════════════════
def show_auth():
    st.markdown(
'<div class="auth-logo">'
'<span class="badge">[ CAT SYSTEM v4.0 ]</span>'
'<div class="name">PSYCHO<span>TECH</span></div>'
'<div class="sub">Platform Simulasi CAT Psikotes Polri — Marathon Edition</div>'
'</div>', unsafe_allow_html=True)

    col_l, col_m, col_r = st.columns([1, 2.2, 1])
    with col_m:
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
            st.markdown(
'<div class="pay-box">'
'<h5>💳 Cara Aktivasi</h5>'
'<div class="pay-row">1. Daftar lalu <strong>Login</strong> dengan akun baru</div>'
'<div class="pay-row">2. Transfer BRI: <strong>1234-5678-9012-3456</strong> — <strong>Rp 25.000</strong></div>'
'<div class="pay-row">3. WA bukti ke: <strong>0853-6637-4530</strong></div>'
'<div class="pay-row">✅ Aktivasi <strong>dalam 1×24 jam</strong></div>'
'</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
'<div class="footer-credit">'
'🚀 <b>Project Development</b> &nbsp;|&nbsp;'
'<a href="https://www.instagram.com/growing_together369" target="_blank">@growing_together369</a>'
'</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════
# HOME PAGE
# ══════════════════════════════════════════════
def show_home():
    st.markdown(
'<div class="hero-command">'
'<div class="hero-rank">[ MARATON v4.0 — SEMUA SESI ]</div>'
'<h1 class="hero-title">ARENA<br><span>MARATON</span><br>CAT POLRI</h1>'
f'<p class="hero-sub">Simulasi 4 sesi berurutan: Pass Hand → Kecerdasan → Kepribadian → Kecermatan. Nilai hanya muncul di akhir. Passing Grade rata-rata <b style="color:var(--accent);">≥ {PASSING_GRADE}</b>.</p>'
'<div class="stat-row">'
'<div class="stat-chip"><span class="n">4</span><span class="l">Sesi Ujian</span></div>'
f'<div class="stat-chip"><span class="n">{SOAL_PER_SESI*4}</span><span class="l">Total Soal</span></div>'
f'<div class="stat-chip"><span class="n">{PASSING_GRADE}</span><span class="l">Passing Grade</span></div>'
'<div class="stat-chip"><span class="n">24/7</span><span class="l">Akses Penuh</span></div>'
'</div>'
'</div>', unsafe_allow_html=True)

    col_main, col_lb = st.columns([3, 2], gap="large")

    with col_main:
        st.markdown(
'<div class="sec-head"><div class="sec-head-line"></div>'
'<div class="sec-head-text">Urutan Sesi Maraton</div></div>', unsafe_allow_html=True)

        sesi_data = [
            {"key": "Pass Hand",   "icon": "📋", "title": "PASS HAND",   "desc": "10 pernyataan YA/TIDAK profiling polisi. Kejujuran adalah kuncinya.", "tags": ["Sesi 1", "10 Soal", "45 Dtk/Soal"], "accent": "#fb6b00"},
            {"key": "Kecerdasan",  "icon": "🧠", "title": "KECERDASAN",  "desc": "Matematika dasar, spasial, verbal, logika & mata angin 2025.", "tags": ["Sesi 2", "10 Soal", "+10 per Benar"], "accent": "#39d353"},
            {"key": "Kepribadian", "icon": "🧬", "title": "KEPRIBADIAN", "desc": "Skala Likert 5 tingkat. Skor adaptif berdasarkan arah pernyataan.", "tags": ["Sesi 3", "10 Soal", "Likert 1-5"], "accent": "#bc8cff"},
            {"key": "Kecermatan",  "icon": "🎯", "title": "KECERMATAN",  "desc": "Temukan karakter hilang dari kunci kolom. Auto-submit via klik.", "tags": ["Sesi 4", "10 Soal", "Auto-Submit"], "accent": "#58a6ff"},
        ]

        st.markdown('<div class="arena-grid">', unsafe_allow_html=True)
        for s in sesi_data:
            tags_html = "".join(f'<span class="meta-tag">{t}</span>' for t in s["tags"])
            st.markdown(
f'<div class="arena-card" style="--card-accent:{s["accent"]};">'
f'<span class="ac-icon">{s["icon"]}</span>'
f'<div class="ac-title">{s["title"]}</div>'
f'<div class="ac-desc">{s["desc"]}</div>'
f'<div class="ac-meta">{tags_html}</div>'
'</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if st.button("🚀 MULAI MARATON — 4 SESI BERURUTAN", key="start_maraton", use_container_width=True):
            _init_maraton()
            st.session_state.page = "simulasi"
            st.rerun()

    with col_lb:
        st.markdown(
'<div class="sec-head"><div class="sec-head-line"></div>'
'<div class="sec-head-text">🏆 Leaderboard Maraton</div></div>', unsafe_allow_html=True)
        display_leaderboard()

    st.markdown(
'<div class="footer-credit">'
'🚀 <b>Project Development</b> &nbsp;|&nbsp;'
'<a href="https://www.instagram.com/growing_together369" target="_blank">@growing_together369</a>'
'</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════
# INISIASI MARATON
# ══════════════════════════════════════════════
def _init_maraton():
    st.session_state.mar_sesi_idx   = 0
    st.session_state.mar_step       = 0
    st.session_state.mar_done       = False
    st.session_state.mar_hasil      = {}
    st.session_state.mar_start_sesi = time.time()

    # Generate AND Shuffle biar beda terus tiap main
    st.session_state.mar_soal = {}
    for sesi in URUTAN_MARATON:
        soals = [generate_soal(sesi) for _ in range(SOAL_PER_SESI)]
        random.shuffle(soals)
        st.session_state.mar_soal[sesi] = soals

    st.session_state.mar_jawaban    = {s: [None] * SOAL_PER_SESI for s in URUTAN_MARATON}
    st.session_state.mar_waktu_soal = {s: [None] * SOAL_PER_SESI for s in URUTAN_MARATON}
    st.session_state.mar_waktu_kecermatan = []

def _sesi_aktif() -> str:
    return URUTAN_MARATON[st.session_state.mar_sesi_idx]

def _selesai_sesi():
    sesi      = _sesi_aktif()
    soal_list = st.session_state.mar_soal[sesi]
    jawaban   = st.session_state.mar_jawaban[sesi]

    if sesi == "Pass Hand":
        hasil = skor_sesi_pass_hand(soal_list, jawaban)
    elif sesi == "Kecerdasan":
        hasil = skor_sesi_kecerdasan(soal_list, jawaban)
    elif sesi == "Kepribadian":
        hasil = skor_sesi_kepribadian(soal_list, jawaban)
    else:
        waktu = st.session_state.mar_waktu_kecermatan
        hasil = skor_sesi_kecermatan(soal_list, jawaban, waktu)

    st.session_state.mar_hasil[sesi] = hasil

    next_idx = st.session_state.mar_sesi_idx + 1
    if next_idx >= len(URUTAN_MARATON):
        st.session_state.mar_done = True
        rekap = rekap_maraton({s: v["skor_100"] for s, v in st.session_state.mar_hasil.items()})
        save_score_maraton(
            st.session_state.get("username", "guest"),
            rekap["rata_rata"],
            rekap["status"],
        )
        st.session_state.mar_rekap = rekap
    else:
        st.session_state.mar_sesi_idx   = next_idx
        st.session_state.mar_step       = 0
        st.session_state.mar_start_sesi = time.time()

# ══════════════════════════════════════════════
# SIMULASI — MAIN
# ══════════════════════════════════════════════
def show_simulation():
    if st.session_state.get("mar_done", False):
        _show_hasil_akhir()
        return

    sesi  = _sesi_aktif()
    cfg   = SESI_CONFIG[sesi]
    step  = st.session_state.mar_step
    soal  = st.session_state.mar_soal[sesi][step]

    # Watermark
    username_wm = st.session_state.get("username", "USER").upper()
    st.markdown(
'<div class="sim-watermark">'
'<div class="sim-watermark-text">'
f'{username_wm}'
'<span>PSYCHOTECH POLRI</span>'
'</div>'
'</div>', unsafe_allow_html=True)

    _render_maraton_track(sesi)

    # Timer
    elapsed   = time.time() - st.session_state.mar_start_sesi
    total_dur = cfg["timer"] * SOAL_PER_SESI
    remaining = max(0, int(total_dur - elapsed))

    if remaining <= 0:
        _selesai_sesi()
        st.rerun()
        return

    timer_cls = "crit" if remaining <= 30 else ("warn" if remaining <= 60 else "")
    mins, secs = divmod(remaining, 60)
    timer_str  = f"{mins:02d}:{secs:02d}"

    sesi_no = URUTAN_MARATON.index(sesi) + 1
    st.markdown(
'<div class="sim-hdr">'
'<div class="sim-hdr-left">'
f'<div class="sesi-label">[ SESI {sesi_no}/4 — MARATON ]</div>'
f'<div class="sesi-title">{cfg["icon"]} {cfg["label"]}</div>'
'</div>'
'<div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;">'
f'<div style="font-family:var(--mono);font-size:0.72rem;color:var(--text-sec);">SOAL {step+1}/{SOAL_PER_SESI}</div>'
f'<div class="timer-box {timer_cls}">{timer_str}</div>'
'</div>'
'</div>', unsafe_allow_html=True)

    pct = step / SOAL_PER_SESI * 100
    st.markdown(f'<div class="prog-wrap"><div class="prog-fill" style="width:{pct}%;"></div></div>', unsafe_allow_html=True)

    if sesi == "Pass Hand":
        _render_pass_hand(soal, step)
    elif sesi == "Kecerdasan":
        _render_kecerdasan(soal, step)
    elif sesi == "Kepribadian":
        _render_kepribadian(soal, step)
    elif sesi == "Kecermatan":
        _render_kecermatan(soal, step)

    time.sleep(1)
    st.rerun()

def _render_maraton_track(sesi_aktif: str):
    steps_html = ""
    for s in URUTAN_MARATON:
        idx_s    = URUTAN_MARATON.index(s)
        idx_aktif = URUTAN_MARATON.index(sesi_aktif)
        cfg_s    = SESI_CONFIG[s]

        if idx_s < idx_aktif:
            css   = "done"
            skor_html = f'<span class="ms-skor">✓ {st.session_state.mar_hasil.get(s, {{}}).get("skor_100", 0)}</span>'
        elif idx_s == idx_aktif:
            css   = "active"
            skor_html = '<span class="ms-skor">▶ Aktif</span>'
        else:
            css   = ""
            skor_html = ""

        steps_html += f'<div class="maraton-step {css}">'
        steps_html += f'<span class="ms-icon">{cfg_s["icon"]}</span>'
        steps_html += f'<span class="ms-label">{cfg_s["label"]}</span>'
        steps_html += f'{skor_html}'
        steps_html += '</div>'

    st.markdown(f'<div class="maraton-track">{steps_html}</div>', unsafe_allow_html=True)

# ── NAV BUTTONS ──
def _nav_buttons(step: int, sesi: str):
    jawaban_step  = st.session_state.mar_jawaban[sesi][step]
    sudah_jawab   = jawaban_step is not None
    is_last       = (step == SOAL_PER_SESI - 1)
    answered_count = sum(1 for j in st.session_state.mar_jawaban[sesi] if j is not None)

    badge = '<span class="answered-badge">✓ Terjawab</span>' if sudah_jawab else ''
    st.markdown(f'<div class="nav-progress">{answered_count}/{SOAL_PER_SESI} soal terjawab {badge}</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        if step > 0:
            if st.button("← Sebelumnya", key=f"prev_{sesi}_{step}", use_container_width=True):
                st.session_state.mar_step -= 1
                st.rerun()
    with c2:
        if not is_last:
            if st.button("Selanjutnya →", key=f"next_{sesi}_{step}", use_container_width=True):
                st.session_state.mar_step += 1
                st.rerun()
    with c3:
        if is_last or answered_count == SOAL_PER_SESI:
            lbl = f"✅ SELESAI SESI" if is_last else f"SELESAI ({answered_count}/{SOAL_PER_SESI})"
            if st.button(lbl, key=f"finish_{sesi}_{step}", use_container_width=True):
                _selesai_sesi()
                st.rerun()

# ── PASS HAND ──
def _render_pass_hand(soal: dict, step: int):
    st.markdown(
'<div class="q-box no-select">'
f'<div class="q-num">PERNYATAAN {step+1} &nbsp;/&nbsp; PROFILING POLISI</div>'
f'<div class="pernyataan-box">{soal.get("pernyataan","—")}</div>'
f'<div style="font-size:0.78rem;color:var(--text-sec);margin-top:8px;">{soal.get("instruksi","")}</div>'
'</div>', unsafe_allow_html=True)

    opsi    = ["YA", "TIDAK"]
    current = st.session_state.mar_jawaban["Pass Hand"][step]
    idx     = opsi.index(current) if current in opsi else None

    with st.form(key=f"form_ph_{step}"):
        pilihan = st.radio("Jawaban:", opsi, index=idx, label_visibility="collapsed", horizontal=True)
        if st.form_submit_button("SIMPAN JAWABAN", use_container_width=True):
            st.session_state.mar_jawaban["Pass Hand"][step] = pilihan
            st.rerun()

    _nav_buttons(step, "Pass Hand")

# ── KECERDASAN ──
def _render_kecerdasan(soal: dict, step: int):
    st.markdown(
'<div class="q-box no-select">'
f'<div class="q-num">SOAL {step+1} &nbsp;/&nbsp; {soal.get("kategori","Kecerdasan")}</div>'
f'<div class="q-text">{soal.get("pertanyaan","—")}</div>'
'</div>', unsafe_allow_html=True)

    opsi    = soal.get("opsi", [])
    current = st.session_state.mar_jawaban["Kecerdasan"][step]
    idx     = opsi.index(current) if current in opsi else None

    with st.form(key=f"form_kec_{step}"):
        pilihan = st.radio("Pilih jawaban:", opsi, index=idx, label_visibility="collapsed")
        if st.form_submit_button("SIMPAN JAWABAN", use_container_width=True):
            st.session_state.mar_jawaban["Kecerdasan"][step] = pilihan
            st.rerun()

    _nav_buttons(step, "Kecerdasan")

# ── KEPRIBADIAN ──
def _render_kepribadian(soal: dict, step: int):
    arah       = soal.get("arah", "positif")
    arah_label = "Pernyataan Positif" if arah == "positif" else "Pernyataan Negatif"
    arah_css   = arah

    st.markdown(
'<div class="q-box no-select">'
f'<div class="q-num">PERNYATAAN {step+1} &nbsp;/&nbsp; KEPRIBADIAN</div>'
f'<div class="q-text">{soal.get("pernyataan","—")}</div>'
f'<div><span class="arah-badge {arah_css}">{arah_label}</span></div>'
'</div>', unsafe_allow_html=True)

    likert_labels = ["A. Sangat Setuju", "B. Setuju", "C. Ragu-ragu", "D. Tidak Setuju",  "E. Sangat Tidak Setuju"]
    current = st.session_state.mar_jawaban["Kepribadian"][step]
    
    if current and len(current) == 1:
        label_match = [l for l in likert_labels if l.startswith(current.upper() + ".")]
        current = label_match[0] if label_match else None
    idx = likert_labels.index(current) if current in likert_labels else None

    with st.form(key=f"form_kep_{step}"):
        st.markdown('<div class="likert-label">Pilih Respons Anda:</div>', unsafe_allow_html=True)
        pilihan = st.radio("Respons:", likert_labels, index=idx, label_visibility="collapsed")
        if st.form_submit_button("SIMPAN JAWABAN", use_container_width=True):
            st.session_state.mar_jawaban["Kepribadian"][step] = pilihan[0]
            st.rerun()

    _nav_buttons(step, "Kepribadian")

# ── KECERMATAN ──
def _render_kecermatan(soal: dict, step: int):
    kunci_html = "".join(f'<div class="kunci-char">{c}</div>' for c in soal.get("kunci", []))
    kolom_nama = soal.get("nama_kolom", "KUNCI")

    st.markdown(
'<div class="q-box no-select">'
f'<div class="q-num">SOAL {step+1} &nbsp;/&nbsp; {kolom_nama}</div>'
'<div style="margin-bottom:12px;">'
'<div style="font-family:var(--mono);font-size:0.65rem;color:var(--text-sec);letter-spacing:1px;margin-bottom:8px;">KUNCI REFERENSI</div>'
f'<div class="kunci-grid">{kunci_html}</div>'
'</div>'
'<div class="q-text">Karakter apa yang <b style="color:var(--red-alert);">tidak ada</b> di baris berikut?</div>'
f'<div class="tampilan-box">{soal.get("tampilan","")}</div>'
'<div class="missing-hint">Bandingkan dengan kunci referensi di atas — pilih karakter yang hilang.</div>'
'</div>', unsafe_allow_html=True)

    opsi = soal.get("opsi", [])
    
    # Kolom agar horizontal sesuai gambar teman user
    cols = st.columns(len(opsi))
    for i, op in enumerate(opsi):
        with cols[i]:
            if st.button(str(op), key=f"cer_{step}_{i}", use_container_width=True):
                waktu = catat_waktu_jawab(soal)
                st.session_state.mar_jawaban["Kecermatan"][step]   = op
                st.session_state.mar_waktu_soal["Kecermatan"][step] = waktu
                st.session_state.mar_waktu_kecermatan.append(waktu)

                if step >= SOAL_PER_SESI - 1:
                    _selesai_sesi()
                else:
                    st.session_state.mar_step += 1
                st.rerun()

# ══════════════════════════════════════════════
# HASIL AKHIR MARATON
# ══════════════════════════════════════════════
def _show_hasil_akhir():
    rekap = st.session_state.get("mar_rekap", {})
    rata  = rekap.get("rata_rata", 0)
    lulus = rekap.get("lulus", False)
    pg    = rekap.get("passing_grade", PASSING_GRADE)

    status_cls  = "final-status-ms"  if lulus else "final-status-tms"
    status_txt  = "✅ MS — MEMENUHI SYARAT" if lulus else "❌ TMS — TIDAK MEMENUHI SYARAT"
    bar_cls     = "final-bar-fill-ms" if lulus else "final-bar-fill-tms"
    pct         = min(int(rata / 100 * 100), 100)
    verdict_txt = "Selamat! Performa Anda di atas passing grade." if lulus else f"Rata-rata {rata} belum mencapai passing grade {pg}. Tetap semangat!"

    st.markdown(
'<div class="final-box">'
'<div class="final-label">[ MARATON SELESAI — HASIL AKHIR ]</div>'
f'<div class="final-score">{rata}</div>'
'<div style="font-family:var(--mono);font-size:0.72rem;color:var(--text-sec);">RATA-RATA / 100</div>'
f'<div class="final-bar-wrap"><div class="{bar_cls}" style="width:{pct}%;"></div></div>'
f'<div style="margin-top:14px;"><span class="{status_cls}">{status_txt}</span></div>'
f'<div style="font-size:0.88rem;color:var(--text-sec);margin-top:8px;">{verdict_txt}</div>'
f'<div style="font-family:var(--mono);font-size:0.65rem;color:var(--text-dim);margin-top:6px;">Passing Grade: {pg} &nbsp;|&nbsp; Skor ini telah disimpan ke Leaderboard</div>'
'</div>', unsafe_allow_html=True)

    st.markdown(
'<div class="sec-head"><div class="sec-head-line"></div>'
'<div class="sec-head-text">Skor Per Sesi</div></div>', unsafe_allow_html=True)

    skor_cards = ""
    for sesi in URUTAN_MARATON:
        cfg_s = SESI_CONFIG[sesi]
        hasil_s = st.session_state.mar_hasil.get(sesi, {})
        s100  = hasil_s.get("skor_100", 0)
        s_pct = min(s100, 100)
        skor_cards += f'<div class="skor-card">'
        skor_cards += f'<span class="sk-label">{cfg_s["icon"]} {cfg_s["label"]}</span>'
        skor_cards += f'<span class="sk-val">{s100}</span>'
        skor_cards += f'<div class="sk-bar-wrap"><div class="sk-bar-fill" style="width:{s_pct}%;background:{cfg_s["color"]};"></div></div>'
        skor_cards += '</div>'
        
    st.markdown(f'<div class="skor-grid">{skor_cards}</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔄 ULANG MARATON", use_container_width=True):
            _init_maraton()
            st.session_state.page = "simulasi"
            st.rerun()
    with c2:
        if st.button("🏠 KEMBALI HOME", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    st.markdown(
'<div class="sec-head"><div class="sec-head-line"></div>'
'<div class="sec-head-text">📖 Evaluasi & Pembahasan</div></div>'
'<div style="font-size:0.83rem;color:var(--text-sec);margin-bottom:16px;">Review soal yang jawabannya belum optimal. Pelajari pembahasannya untuk performa lebih baik di sesi berikutnya.</div>', unsafe_allow_html=True)

    tab_labels = [f"{SESI_CONFIG[s]['icon']} {s}" for s in URUTAN_MARATON]
    tabs = st.tabs(tab_labels)

    for tab, sesi in zip(tabs, URUTAN_MARATON):
        with tab:
            hasil_s = st.session_state.mar_hasil.get(sesi, {})
            detail  = hasil_s.get("detail", [])
            _render_evaluasi(sesi, detail)

def _render_evaluasi(sesi: str, detail: list):
    if not detail:
        st.markdown('<div style="color:var(--text-dim);font-size:0.85rem;padding:16px 0;">Tidak ada data evaluasi.</div>', unsafe_allow_html=True)
        return

    salah_count = sum(1 for d in detail if not d.get("benar", True))
    benar_count = len(detail) - salah_count
    
    st.markdown(
'<div style="display:flex;gap:16px;margin-bottom:14px;flex-wrap:wrap;">'
f'<div style="font-family:var(--mono);font-size:0.72rem;color:#39d353;">✓ Benar: {benar_count}</div>'
f'<div style="font-family:var(--mono);font-size:0.72rem;color:#f85149;">✗ Salah/Sub-optimal: {salah_count}</div>'
'</div>', unsafe_allow_html=True)

    for i, d in enumerate(detail, 1):
        is_benar = d.get("benar", True)
        css_cls  = "benar" if is_benar else "salah"
        icon     = "✓" if is_benar else "✗"
        icon_col = '#39d353' if is_benar else '#f85149'

        if sesi == "Pass Hand":
            q_html = f"<b>{i}.</b> {d.get('pernyataan','')}"
            ans_html = f'<span class="user-ans">Jawaban Lo: {d.get("jawaban_user","—")}</span><span class="correct-ans">Ideal: {d.get("jawaban_ideal","—")}</span>'
        elif sesi == "Kecerdasan":
            q_html   = f"<b>{i}.</b> {d.get('pertanyaan','')}"
            ans_html = f'<span class="user-ans">Lo: {d.get("teks_user","—")}</span><span class="correct-ans">Benar: {d.get("teks_benar","—")}</span>'
        elif sesi == "Kepribadian":
            label_map = {"A": "Sangat Setuju", "B": "Setuju", "C": "Ragu-ragu", "D": "Tidak Setuju",  "E": "Sangat Tidak Setuju"}
            jwb_huruf = d.get("jawaban_user", "C")
            q_html    = f"<b>{i}.</b> {d.get('pernyataan','')}"
            ans_html  = f'<span class="user-ans">Lo: {label_map.get(jwb_huruf, jwb_huruf)} (+{d.get("poin",0)} poin)</span><span class="correct-ans">Arah: {d.get("arah","").upper()}</span>'
        else:
            q_html   = f"<b>{i}.</b> Kunci <b>{d.get('nama_kolom','')}</b>: tampilan <code>{d.get('tampilan','')}</code>"
            ans_html = f'<span class="user-ans">Lo: {d.get("jawaban_user","—")}</span><span class="correct-ans">Benar: {d.get("jawaban_benar","—")}</span>'

        pembahasan = d.get("pembahasan", "")
        pemb_div = f'<div class="eval-pembahasan">💡 {pembahasan}</div>' if pembahasan else ''
        
        st.markdown(
f'<div class="eval-item {css_cls}">'
f'<div style="font-family:var(--mono);font-size:0.6rem;color:{icon_col};letter-spacing:1px;margin-bottom:6px;">{icon} SOAL {i}</div>'
f'<div class="eval-q">{q_html}</div>'
f'<div class="eval-ans">{ans_html}</div>'
f'{pemb_div}'
'</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════
# MAIN ROUTING
# ══════════════════════════════════════════════
def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "page" not in st.session_state:
        st.session_state.page = "home"

    if not st.session_state.logged_in:
        show_auth()
        return

    with st.sidebar:
        st.markdown(
'<div style="text-align:center;padding:20px 0 14px;">'
'<div style="font-family:\'JetBrains Mono\',monospace;font-size:0.58rem;color:#fb6b00;letter-spacing:2px;text-transform:uppercase;margin-bottom:7px;">[ MARATON v4.0 ]</div>'
'<div style="font-family:\'Barlow Condensed\',sans-serif;font-size:1.45rem;font-weight:900;color:#e6edf3;letter-spacing:-0.5px;">PSYCHOTECH</div>'
'</div>', unsafe_allow_html=True)
        st.divider()

        if st.button("🏠  HOME", use_container_width=True, key="nav_home"):
            st.session_state.page = "home"
            st.rerun()

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button("🚀  MULAI MARATON", use_container_width=True, key="nav_maraton"):
            _init_maraton()
            st.session_state.page = "simulasi"
            st.rerun()

        st.divider()
        st.markdown(f"<div style='font-size:0.76rem;color:#7d8590;'>👤 <b style='color:#e6edf3;'>{st.session_state.get('username','—')}</b></div>", unsafe_allow_html=True)
        st.markdown("<div style='height:7px'></div>", unsafe_allow_html=True)
        if st.button("🚪 LOGOUT", use_container_width=True, key="nav_logout"):
            st.session_state.logged_in = False
            st.rerun()

        st.markdown(
'<div style="text-align:center;margin-top:14px;font-size:0.7rem;color:#484f58;">'
'🚀 <a href="https://www.instagram.com/growing_together369" target="_blank" style="color:#fb6b00;text-decoration:none;font-weight:700;">@growing_together369</a>'
'</div>', unsafe_allow_html=True)

    page = st.session_state.page
    if page == "home":
        show_home()
    elif page == "simulasi":
        show_simulation()

if __name__ == "__main__":
    main()
