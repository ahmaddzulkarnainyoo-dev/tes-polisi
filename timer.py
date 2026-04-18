import time

# Contoh logic timer sederhana
def start_timer(seconds):
    timer_slot = st.empty()
    for remaining in range(seconds, -1, -1):
        mins, secs = divmod(remaining, 60)
        timer_slot.metric("Sisa Waktu", f"{mins:02d}:{secs:02d}")
        time.sleep(1)
        if remaining == 0:
            st.error("Waktu Habis!")
            return True
    return False
