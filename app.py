import streamlit as st
import time
from engine import generate_soal_ai, generate_kecermatan
from database import supabase

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Psychotech Polri", page_icon="🛡️", layout="wide")

# --- CSS CUSTOM ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .hero-container {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 40px 20px;
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
        margin-bottom: 20px;
    }
    .ig-credit {
        text-align: center;
        margin-top: 20px;
        font-size: 14px;
    }
    </style>
""", unsafe_allow_html=True)

# --- FUNGSI AUTH (Satu Fungsi untuk Semua) ---
def login_user(username, password):
    res = supabase.table("users").select("*").eq("username", username).eq("password", password).execute()
    if res.data:
        user = res.data[0]
        if user.get('status') == 'pending':
            st.warning("⚠️ Akun lo belum aktif, bro. Selesaikan pembayaran dulu.")
            st.info("Kirim bukti bayar ke WA: 0853-6637-4530")
            st.stop()
        return user
    return None

def register_user(username, password):
    try:
        # Default status adalah 'pending'
        supabase.table("users").insert({"username": username, "password": password, "status": "pending"}).execute()
        return True
    except:
        return False

def show_auth():
    st.markdown('<div class="hero-container"><h1>🛡️ Akses Psychotech</h1><p>Masuk untuk memulai simulasi</p></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["🔑 Login", "📝 Daftar Akun"])
        
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

        with tab2:
            with st.form("reg_form"):
                new_u = st.text_input("Username Baru")
                new_p = st.text_input("Password Baru", type="password")
                if st.form_submit_button("Daftar Akun"):
                    if register_user(new_u, new_p):
                        st.success("Akun berhasil dibuat! Status: Pending. Silakan hubungi admin.")
                    else:
                        st.error("Username sudah terdaftar atau terjadi gangguan.")
        
        # Nama IG Temen lo di Dashboard Login
        st.markdown("""
            <div class="ig-credit">
                🚀 <b>Project Development</b><br>
                <a href="https://www.instagram.com/growing_together369" target="_blank" style="text-decoration:none;color:#E1306C;font-weight:bold;">
                    Made by @growing_together369
                </a>
            </div>
        """, unsafe_allow_html=True)

# --- FUNGSI SIMULASI ---
def show_simulation():
    # Pilih Sesi di dalam menu simulasi
    sesi = st.selectbox("Pilih Sesi Ujian:", ["Kecerdasan", "Kecermatan", "Kepribadian"])
    st.divider()

    if 'step' not in st.session_state or st.session_state.get('current_sesi') != sesi:
        st.session_state.step = 1
        st.session_state.skor = 0
        st.session_state.current_sesi = sesi
        st.session_state.end_time = time.time() + 30
        if sesi == "Kecermatan":
            st.session_state.soal_aktif = generate_kecermatan()
        else:
            st.session_state.soal_aktif = generate_soal_ai(sesi)

    # Logika Timer
    remaining = int(st.session_state.end_time - time.time())
    if remaining <= 0:
        st.warning("⏰ Waktu habis!")
        time.sleep(1)
        st.session_state.step += 1
        st.session_state.end_time = time.time() + 30
        st.session_state.soal_aktif = generate_kecermatan() if sesi == "Kecermatan" else generate_soal_ai(sesi)
        st.rerun()

    st.sidebar.metric("⏳ Sisa Waktu", f"{remaining} detik")

    if st.session_state.step <= 10:
        soal = st.session_state.soal_aktif
        
        if sesi == "Kecermatan":
            st.markdown("### 📋 TABEL KUNCI")
            cols = st.columns(5)
            for i, char in enumerate(soal['kunci']):
                cols[i].info(f"**{char}**")
            st.write(f"**Soal {st.session_state.step}:** Karakter apa yang hilang dari: `{soal['pertanyaan']}`?")
        else:
            st.write(f"**Soal {st.session_state.step} ({sesi})**")
            st.write(soal['pertanyaan'])

        with st.form(key=f"form_{st.session_state.step}"):
            pilihan = st.radio("Pilih Jawaban:", soal['opsi'])
            if st.form_submit_button("Lanjut ➡️"):
                # Hitung skor (Kecerdasan/Kecermatan pakai jawaban benar, Kepribadian pakai bobot)
                if sesi == "Kepribadian":
                    idx = soal['opsi'].index(pilihan)
                    st.session_state.skor += soal['skor'][idx]
                elif pilihan == soal['jawaban']:
                    st.session_state.skor += 10
                
                st.session_state.step += 1
                st.session_state.end_time = time.time() + 30
                st.session_state.soal_aktif = generate_kecermatan() if sesi == "Kecermatan" else generate_soal_ai(sesi)
                st.rerun()
    else:
        st.success(f"Sesi {sesi} Selesai! Skor lo: {st.session_state.skor}")
        if st.button("Ulangi Sesi"):
            del st.session_state.step
            st.rerun()

def show_home():
    st.markdown("""
        <div class="hero-container">
            <h1>🛡️ Psychotech Polri v1.0</h1>
            <p>Platform Asesmen Psikometri Terintegrasi</p>
        </div>
    """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    # ... isi nav-card lo ...

# --- ROUTING UTAMA ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    show_auth()
else:
    st.sidebar.title("🛡️ Panel Navigasi")
    menu = st.sidebar.radio("Pilih Menu", ["Home", "Mulai Simulasi", "Dashboard Admin"])
    
    st.sidebar.markdown("---")
    st.sidebar.write("🚀 **Project Development**")
    st.sidebar.markdown('<a href="https://www.instagram.com/growing_together369" target="_blank" style="text-decoration:none;color:#E1306C;font-weight:bold;">Made by @growing_together369</a>', unsafe_allow_html=True)
    
    if st.sidebar.button("Keluar (Logout)"):
        st.session_state.logged_in = False
        st.rerun()

    if menu == "Home": show_home()
    elif menu == "Mulai Simulasi": show_simulation()
    elif menu == "Dashboard Admin":
        st.info("Halaman Admin dalam pengembangan.")
