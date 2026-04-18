import streamlit as st
import time

def start_countdown(seconds):
    timer_slot = st.empty()
    for remaining in range(seconds, -1,-1):
        mins, secs=divmod(remaining,60)
        timer_slot, metric("sisa waktu",f"{mins:02d}:{secs:02d}")
        time.sleep(1)
        if remaining == 0:
            st.error("waktu habis boy!")
            return True
        return False
