import streamlit as st
from database import list_all_users, activate_premium

def show_admin_page():
    st.header("🔑 Admin Control Panel")
    
    # Simple Password Protection
    pw = st.text_input("Masukkan Kode Admin", type="password")
    if pw != "GUEPUNYAPROJEK": # Ganti sesuka lo
        st.error("Kode salah.")
        return

    st.subheader("Daftar Pengguna")
    try:
        users = list_all_users().data
        if users:
            for u in users:
                col1, col2 = st.columns([3, 1])
                status = "✅ Premium" if u['is_premium'] else "❌ Standard"
                col1.write(f"ID: `{u['id']}` | Status: {status}")
                if not u['is_premium']:
                    if col2.button("Aktifkan", key=u['id']):
                        activate_premium(u['id'])
                        st.success("User diaktifkan!")
                        st.rerun()
        else:
            st.info("Belum ada user terdaftar.")
    except Exception as e:
        st.error(f"Gagal narik data: {e}")
        
