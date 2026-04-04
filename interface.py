import streamlit as st

def apply_custom_css():
    st.markdown("""
        <style>
            /* 1. HIDE THE CIRCLE WITHOUT HIDING TEXT */
            /* This targets the SVG circle specifically */
            [data-testid="stSidebar"] div[role="radiogroup"] label [data-baseweb="radio"] div:first-child {
                display: none !important;
            }
            
            /* Remove the gap left by the missing circle */
            [data-testid="stSidebar"] div[role="radiogroup"] label {
                padding-left: 10px !important;
                margin-left: -15px !important;
                min-height: 45px !important;
                display: flex !important;
                align-items: center !important;
            }

            /* 2. REMOVE "PRESS ENTER TO APPLY" */
            [data-testid="stFieldDescription"] {
                display: none !important;
            }

            /* 3. ENSURE TEXT IS VISIBLE */
            [data-testid="stSidebar"] p {
                opacity: 1 !important;
                color: white !important; /* Force visibility */
                font-size: 1.1rem !important;
                margin: 0 !important;
            }

            /* 4. HOVER & ACTIVE STATE */
            [data-testid="stSidebar"] div[role="radiogroup"] label:hover {
                background-color: rgba(255, 255, 255, 0.1) !important;
                border-radius: 8px;
            }

            [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
                background-color: rgba(0, 123, 255, 0.2) !important;
                border-left: 5px solid #007bff !important;
                border-radius: 2px 8px 8px 2px;
            }
        </style>
    """, unsafe_allow_html=True)

def show_sidebar():
    with st.sidebar:
        st.markdown(f"### 👤")
        st.write(f"**{st.session_state.full_name}**")
        st.caption(f"{st.session_state.user_email}")
        st.write("---")
        
        # Initialize the menu choice if it doesn't exist
        if "menu_choice" not in st.session_state:
            st.session_state.menu_choice = "🧞‍♂️ Search"

        # Create custom buttons that look like menu items
        if st.button("🧞‍♂️ Search", use_container_width=True, type="primary" if st.session_state.menu_choice == "🧞‍♂️ Search" else "secondary"):
            st.session_state.menu_choice = "🧞‍♂️ Search"
            st.rerun()

        if st.button("⚙️ Profile", use_container_width=True, type="primary" if st.session_state.menu_choice == "⚙️ Profile" else "secondary"):
            st.session_state.menu_choice = "⚙️ Profile"
            st.rerun()
        
        st.write("---")
        if st.button("🚪 Logout", use_container_width=True):
            # If using Cookie Manager, remember to delete cookie here too!
            st.session_state.logged_in = False
            st.rerun()
            
    return st.session_state.menu_choice

def show_profile_page():
    """Renders the actual Profile UI"""
    st.title("👤 User Profile")
    st.info(f"Welcome to your settings, **{st.session_state.full_name}**.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Account Details")
        st.write(f"**Name:** {st.session_state.full_name}")
        st.write(f"**Email:** {st.session_state.user_email}")
    with col2:
        st.subheader("Preferences")
        st.toggle("Dark Mode (Auto)", value=True, disabled=True)
        st.button("Update Password", disabled=True)

def show_main_genie_page(model, tokenizer, mlb, df, library_embeddings, get_predictions, get_recommendations, np):
    """Renders the Search and Results UI"""
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
                # A. Call the Identifier
                genres = get_predictions(user_query, model, tokenizer, mlb)
    
                # B. Call the Recommender
                recs_df, scores = get_recommendations(user_query, model, tokenizer, library_embeddings, df)
    
                # C. DISPLAY RESULTS
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
