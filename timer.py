import streamlit as st
import time

def start_countdown(seconds):
    # Tempat nampilin timer di UI
    timer_display = st.sidebar.empty()
    
    # Simpan waktu akhir di session_state biar ga reset pas refresh
    if 'end_time' not in st.session_state:
        st.session_state.end_time = time.time() + seconds

    while True:
        remaining = int(st.session_state.end_time - time.time())
        
        if remaining <= 0:
            timer_display.error("⏰ Waktu Habis!")
            return True # Kasih sinyal buat auto-submit
        
        # Format menit:detik
        mins, secs = divmod(remaining, 60)
        timer_display.metric("Sisa Waktu", f"{mins:02d}:{secs:02d}")
        
        time.sleep(1)
        # Kita ga pake rerun di sini biar ga berat, 
        # tapi timer bakal update tiap kali ada aksi user juga.
