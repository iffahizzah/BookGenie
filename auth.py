import streamlit as st
import bcrypt
import extra_streamlit_components as stx

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

def show_auth_page(st_supabase, cookie_manager):
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.title("🔐 BookGenie Access")
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab2:
            st.subheader("Create New Account")
            new_name = st.text_input("Full Name")
            new_email = st.text_input("Email Address")
            new_pass = st.text_input("Password", type="password")
            confirm_pass = st.text_input("Confirm Password", type="password")
            
            if st.button("Register Account"):
                if not new_name or not new_email or not new_pass:
                    st.error("Please fill in all fields.")
                elif new_pass != confirm_pass:
                    st.error("Passwords do not match!")
                else:
                    try:
                        hashed = hash_password(new_pass)
                        st_supabase.table("users").insert({
                            "full_name": new_name, 
                            "email": new_email.lower().strip(), 
                            "password_hash": hashed
                        }).execute()
                        st.success("Registration successful! Switch to the Login tab.")
                    except Exception as e:
                        st.error("This email might already be registered.")

        with tab1:
            st.subheader("Welcome Back")
            login_email = st.text_input("Email Address", key="l_email")
            login_pw = st.text_input("Password", type="password", key="l_pass")
            
            if st.button("Login"):
                res = st_supabase.table("users").select("*").eq("email", login_email.lower().strip()).execute()
                
                if res.data and check_password(login_pw, res.data[0]['password_hash']):
                    st.session_state.logged_in = True
                    st.session_state.full_name = res.data[0]['full_name']
                    st.session_state.user_email = res.data[0]['email']

                    cookie_manager.set("bookgenie_user_email", res.data[0]['email'], key="set_login_cookie")
                    
                    st.rerun()
                else:
                    st.error("Invalid email or password")
        return False
    
    return True
