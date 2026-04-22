import streamlit as st
import time
from engine import generate_soal_ai 
from database import supabase

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Psychotech Polri", page_icon="🛡️")

# --- CSS CUSTOM ---
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
    .nav-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        height: 100%;
    }
    .card-icon { font-size: 40px; margin-bottom: 10px; }
    .card-title { font-weight: bold; color: #1e3a8a; }
    </style>
""", unsafe_allow_html=True)

# --- FUNGSI AUTH (LOGIN/DAFTAR) ---
def login_user(username, password):
    res = supabase.table("users").select("*").eq("username", username).eq("password", password).execute()
    return res.data[0] if res.data else None

def register_user(username, password):
    try:
        supabase.table("users").insert({"username": username, "password": password}).execute()
        return True
    except:
        return False

def show_auth():
    st.markdown('<div class="hero-container"><h1>🛡️ Akses Psychotech</h1><p>Masuk untuk memulai simulasi</p></div>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Login", "Daftar Akun"])
    
    with tab1:
        with st.form("login_form"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Masuk"):
                user = login_user(u, p)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.username = u
                    st.rerun()
                else:
                    st.error("Username atau Password salah!")
def login_user(username, password):
    res = supabase.table("users").select("*").eq("username", username).eq("password", password).execute()
    if res.data:
        user = res.data[0]
        if user['status'] == 'pending':
            st.warning("⚠️ Akun lo belum aktif, bro. Selesaikan pembayaran dulu.")
            st.info("Kirim bukti bayar ke WA: 0812-xxxx-xxxx")
            st.stop() # Berhenti di sini, ga bakal masuk ke menu
        return user
    return None

    with tab2:
        with st.form("reg_form"):
            new_u = st.text_input("Username Baru")
            new_p = st.text_input("Password Baru", type="password")
            if st.form_submit_button("Daftar"):
                if register_user(new_u, new_p):
                    st.success("Akun berhasil dibuat! Silakan login.")
                else:
                    st.error("Username sudah terdaftar.")

# --- FUNGSI SIMULASI & TIMER ---
def show_simulation():
    st.subheader(f"Sesi: {st.session_state.username}")
    
    if 'step' not in st.session_state:
        st.session_state.step = 1
        st.session_state.skor = 0
        st.session_state.soal_aktif = generate_soal_ai()
        st.session_state.end_time = time.time() + 30 # 30 detik per soal

    TOTAL_SOAL = 10

    if st.session_state.step <= TOTAL_SOAL:
        # Logika Timer Manual (Sidebar)
        remaining = int(st.session_state.end_time - time.time())
        if remaining <= 0:
            st.warning("⏰ Waktu habis! Lanjut ke soal berikutnya.")
            time.sleep(1)
            st.session_state.step += 1
            st.session_state.soal_aktif = generate_soal_ai()
            st.session_state.end_time = time.time() + 30
            st.rerun()

        st.sidebar.metric("⏳ Sisa Waktu", f"{remaining} detik")
        
        soal = st.session_state.soal_aktif
        st.write(f"**Soal {st.session_state.step} / {TOTAL_SOAL}**")
        
        with st.form(key=f"form_{st.session_state.step}"):
            st.write(soal['pertanyaan'])
            pilihan = st.radio("Jawaban:", soal['opsi'])
            if st.form_submit_button("Lanjut ➡️"):
                if pilihan == soal['jawaban']:
                    st.session_state.skor += 10
                st.session_state.step += 1
                if st.session_state.step <= TOTAL_SOAL:
                    st.session_state.soal_aktif = generate_soal_ai()
                    st.session_state.end_time = time.time() + 30
                st.rerun()
    else:
        st.balloons()
        st.success(f"Tes Selesai! Skor: {st.session_state.skor}")
        if st.button("Ulangi Tes"):
            for k in ['step', 'skor', 'soal_aktif', 'end_time']: 
                if k in st.session_state: del st.session_state[k]
            st.rerun()

def show_home():
    st.markdown("""
        <div class="hero-container">
            <h1>🛡️ Psychotech Polri v1.0</h1>
            <p>Platform Asesmen Psikometri Terintegrasi</p>
        </div>
    """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="nav-card"><h3>📝</h3><b>Uji Kompetensi</b><p>Satu soal per halaman.</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="nav-card"><h3>🛡️</h3><b>Standar Presisi</b><p>Sesuai kisi-kisi terbaru.</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="nav-card"><h3>📊</h3><b>Skor Real-time</b><p>Evaluasi langsung.</p></div>', unsafe_allow_html=True)

# --- SIDEBAR & ROUTING ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    show_auth()
else:
    st.sidebar.title("🛡️ Panel Navigasi")
    menu = st.sidebar.radio("Pilih Menu", ["Home", "Mulai Simulasi", "Dashboard Admin"])

if sesi == "Kecermatan":
    soal = generate_kecermatan()
    # Tampilkan KUNCI dengan kotak-kotak rapi
    st.markdown("### TABEL KUNCI")
    cols = st.columns(5)
    for i, char in enumerate(soal['kunci']):
        cols[i].markdown(f"**{char}**")
    
    st.divider()
    st.subheader(f"Soal: {soal['pertanyaan']}")
    # Opsi jawabannya adalah 5 karakter di kunci tadi
    pilihan = st.radio("Karakter mana yang hilang?", soal['opsi'])    
    # Credit IG Temen lo
    st.sidebar.markdown("---")
    st.sidebar.write("🚀 **Project Development**")
    st.sidebar.markdown('<a href="https://www.instagram.com/growing_together369" target="_blank" style="text-decoration:none;color:#E1306C;font-weight:bold;">Made by @growing_together369</a>', unsafe_allow_html=True)
    
    if st.sidebar.button("Keluar (Logout)"):
        st.session_state.logged_in = False
        st.rerun()

    if menu == "Home": show_home()
    elif menu == "Mulai Simulasi": show_simulation()
    elif menu == "Dashboard Admin":
        try:
            import admin
            admin.show_admin_panel()
        except:
            st.error("Gagal memuat panel admin.")
