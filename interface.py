import streamlit as st

def apply_custom_css():
    st.markdown("""
        <style>
        
            [data-testid="stSidebar"] {
                min-width: 250px !important;
            }

            [data-testid="stSidebar"] button {
                border: none !important;
                text-align: left !important;
                justify-content: flex-start !important;
                padding-left: 15px !important;
                height: 45px !important;
                margin-bottom: 5px !important;
            }

            /* 3. HIDE "PRESS ENTER TO APPLY" ON ALL INPUTS */
            [data-testid="stFieldDescription"] {
                display: none !important;
            }

            [data-testid="stSidebar"] p {
                font-size: 1rem !important;
                margin-bottom: 0px !important;
            }

        </style>
    """, unsafe_allow_html=True)

def show_sidebar():
    with st.sidebar:
        st.markdown(f"### 🧞‍♂️")
        st.write(f"**{st.session_state.full_name}**")
        st.caption(f"{st.session_state.user_email}")
        st.write("---")
        
        # Initialize choice if not set
        if "menu_choice" not in st.session_state:
            st.session_state.menu_choice = "🏠 Home"

        # MENU BUTTONS
        # 'primary' makes it blue, 'secondary' makes it gray
        if st.button("🏠 Home", use_container_width=True, 
                     type="primary" if st.session_state.menu_choice == "🏠 Home" else "secondary"):
            st.session_state.menu_choice = "🏠 Home"
            st.rerun()

        if st.button("⚙️ Profile", use_container_width=True, 
                     type="primary" if st.session_state.menu_choice == "⚙️ Profile" else "secondary"):
            st.session_state.menu_choice = "⚙️ Profile"
            st.rerun()
        
        st.write("---")
        
        # LOGOUT BUTTON
        if st.button("🚪 Logout", use_container_width=True):
            # If you implemented Cookie Manager, add deletion here
            if 'cookie_manager' in st.session_state:
                st.session_state.cookie_manager.delete("bookgenie_user_email")
            st.session_state.logged_in = False
            st.rerun()
            
    return st.session_state.menu_choice

def show_profile_page(st_supabase):
    st.title("👤 User Profile")
    st.info(f"Signed in as **{st.session_state.full_name}**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Account Details")
        st.write(f"**Name:** {st.session_state.full_name}")
        st.write(f"**Email:** {st.session_state.user_email}")
        st.caption("Contact the admin to change your registered email.")

    with col2:
        st.subheader("Security")
        with st.expander("🔐 Change Password"):
            new_pw = st.text_input("New Password", type="password")
            confirm_pw = st.text_input("Confirm New Password", type="password")
            
            if st.button("Update Password"):
                if new_pw != confirm_pw:
                    st.error("Passwords do not match!")
                elif len(new_pw) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    from auth import hash_password # Import your hashing function
                    hashed = hash_password(new_pw)
                    try:
                        st_supabase.table("users").update({"password_hash": hashed}).eq("email", st.session_state.user_email).execute()
                        st.success("Password updated successfully!")
                    except Exception as e:
                        st.error("Failed to update password.")
                        
def show_main_genie_page(model, tokenizer, mlb, df, library_embeddings, get_predictions, get_recommendations, np):
    st.title("🧞‍♂️ BookGenie: Your AI Librarian")
    st.markdown(f"Welcome back! Type a book summary below, and I'll find its genre and similar reads!")
    
    user_query = st.text_area(
        "What kind of story is on your mind?", 
        height=150, 
        placeholder="e.g., A detective solving a mystery in a futuristic city..."
    )
    
    if st.button("✨ Work Your Magic"):
        if user_query:
            with st.spinner("The Genie is reading..."):
                genres = get_predictions(user_query, model, tokenizer, mlb)
                recs_df, scores = get_recommendations(user_query, model, tokenizer, library_embeddings, df)
    
                st.divider()
                col1, col2 = st.columns([1, 2])
    
                with col1:
                    st.subheader("🏷️ Identified Genres")
                    if len(genres) > 0:
                        for g in genres:
                            st.success(f"✅ {g}")
                    else:
                        st.warning("General Fiction")
    
                with col2:
                    st.subheader("📚 Top 5 Recommendations")
                    for i in range(len(recs_df)):
                        book = recs_df.iloc[i]
                        score = scores[i]
                        with st.expander(f"📖 {book['title']}"):
                            st.write(f"**Similarity Match:** {np.round(score * 100, 2)}%")
                            st.write(f"**Genres:** {book.get('revised_genres', 'N/A')}")
                            st.write("---")
                            st.write(f"_{book['description']}_")
        else:
            st.error("Please enter a description first!")
