# Bagian di sidebar app.py
menu = st.sidebar.selectbox("Menu", ["Simulasi Tes", "Admin Panel"])

if menu == "Admin Panel":
    st.header("Admin Control - Aktivasi User")
    access_code = st.text_input("Admin Code", type="password")
    
    if access_code == "GUEPUNYAPROJEK": # Ganti password rahasia lo
        users = list_all_users().data
        for u in users:
            col1, col2 = st.columns([3, 1])
            col1.write(f"{u['full_name']} | Premium: {u['is_premium']}")
            if col2.button("Aktifkan", key=u['id']):
                activate_premium(u['id'])
                st.success(f"User {u['id']} Aktif!")
                
