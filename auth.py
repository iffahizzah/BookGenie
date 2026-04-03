import streamlit as st
import bcrypt

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

def show_auth_page(st_supabase):
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.title("🔐 BookGenie Access")
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab2:
            new_user = st.text_input("Choose Username", key="signup_user")
            new_pass = st.text_input("Choose Password", type="password", key="signup_pass")
            if st.button("Create Account"):
                hashed = hash_password(new_pass)
                st_supabase.table("users").insert({"username": new_user, "password_hash": hashed}).execute()
                st.success("Account created! Please log in.")

        with tab1:
            user = st.text_input("Username", key="login_user")
            pw = st.text_input("Password", type="password", key="login_pass")
            if st.button("Login"):
                res = st_supabase.table("users").select("*").eq("username", user).execute()
                if res.data and check_password(pw, res.data[0]['password_hash']):
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Invalid credentials")
        return False # Tells app.py: "Stop! They aren't logged in yet."
    
    return True # Tells app.py: "Keep going, they're in!"
