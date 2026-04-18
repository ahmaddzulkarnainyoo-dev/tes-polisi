import streamlit as st
from database import list_all_users, activate_premium

# Pastiin nama fungsinya PERSIS kayak gini
def show_admin_panel():
    st.title("🔑 Admin Control Panel")
    
    pw = st.text_input("Masukkan Kode Admin", type="password")
    
    if pw == "GUEPUNYAPROJEK": # Ganti sesuai kode lo
        st.success("Akses Diterima")
        # Logika nampilin user dari database
        users = list_all_users()
        st.table(users)
    elif pw != "":
        st.error("Kode salah.")
