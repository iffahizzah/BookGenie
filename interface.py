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
        
        if "menu_choice" not in st.session_state:
            st.session_state.menu_choice = "Home"

        if st.button("Home", use_container_width=True, 
                     type="primary" if st.session_state.menu_choice == "Home" else "secondary"):
            st.session_state.menu_choice = "Home"
            st.rerun()

        if st.button("My Library", use_container_width=True, 
                     type="primary" if st.session_state.menu_choice == "My Library" else "secondary"):
            st.session_state.menu_choice = "My Library"
            st.rerun()

        if st.button("Profile", use_container_width=True, 
                     type="primary" if st.session_state.menu_choice == "Profile" else "secondary"):
            st.session_state.menu_choice = "Profile"
            st.rerun()
        
        st.write("---")
        
        if st.button("Logout", use_container_width=True):
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
                    from auth import hash_password 
                    hashed = hash_password(new_pw)
                    try:
                        st_supabase.table("users").update({"password_hash": hashed}).eq("email", st.session_state.user_email).execute()
                        st.success("Password updated successfully!")
                    except Exception as e:
                        st.error("Failed to update password.")
                        
def show_main_genie_page(model, tokenizer, mlb, df, library_embeddings, get_predictions, get_recommendations, np, st_supabase):
    st.title("🧞‍♂️ BookGenie: Your AI Librarian")
    st.markdown(f"Welcome back! Type a book summary below, and I'll find its genre and top 5 similar reads!")
    
    user_query = st.text_area(
        "What kind of story is on your mind?", 
        height=150, 
        placeholder="e.g., A detective solving a mystery in a futuristic city..."
    )
    
    # 1. SEARCH SECTION
    if st.button("Submit"):
        if user_query:
            with st.spinner("The Genie is reading..."):
                st.session_state.genres = get_predictions(user_query, model, tokenizer, mlb)
                st.session_state.recs_df, st.session_state.scores = get_recommendations(user_query, model, tokenizer, library_embeddings, df)
                st.session_state.search_done = True
        else:
            st.error("Please enter a description first!")

    # 2. DISPLAY SECTION
    if st.session_state.get("search_done"):
        st.divider()
        col1, col2 = st.columns([1, 2])

        with col1:
            st.subheader("🏷️ Identified Genres")
            for g in st.session_state.genres:
                st.success(f"✅ {g}")

        with col2:
            st.subheader("📚 Top 5 Books that mAtches Your Description")
            for i in range(len(st.session_state.recs_df)):
                book = st.session_state.recs_df.iloc[i]
                book_id = book['book_id']
                
                # Set expanded=False so they don't all pop open at once
                with st.expander(f"📖 {book['title']}", expanded=False):
                    st.write(f"_{book['description']}_")
                    st.divider()
                    
                    st.write("**Book Club Feedback**")
                    u_rating = st.feedback("stars", key=f"star_{book_id}")
                    u_review = st.text_input("Comments:", key=f"rev_{book_id}")

                    if st.button("Submit to Library", key=f"btn_{book_id}"):
                        # Safety check for user_id
                        user_id = st.session_state.get("user_id")
                        if not user_id:
                            st.error("User ID not found. Please log in again.")
                        else:
                            try:
                                data = {
                                    "user_id": user_id,
                                    "book_id": int(book_id),
                                    "rating": u_rating if u_rating is not None else 0,
                                    "review": u_review
                                }
                                st_supabase.table("user_interaction").insert(data).execute()
                                st.success("Saved to the Book Club! 🥂")
                            except Exception as e:
                                st.error(f"Error: {e}")
