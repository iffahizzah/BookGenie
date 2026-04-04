import streamlit as st

def apply_custom_css():
    st.markdown("""
        <style>
            /* 1. Set the transition for a smooth grow/shrink */
            [data-testid="stSidebar"] {
                min-width: 80px !important;
                max-width: 80px !important;
                transition: all 0.3s ease-in-out;
                overflow-x: hidden;
            }
            
            /* 2. Expand on hover */
            [data-testid="stSidebar"]:hover {
                min-width: 300px !important;
                max-width: 300px !important;
            }

            /* 3. HIDE TEXT LABELS BY DEFAULT (The "Falling Text" fix) */
            /* This targets the sidebar navigation labels and button text */
            [data-testid="stSidebarNavItems"] span, 
            [data-testid="stSidebar"] .stMarkdown p,
            [data-testid="stSidebar"] button div p {
                opacity: 0;
                transition: opacity 0.2s ease-in-out;
                white-space: nowrap;
            }

            /* 4. SHOW TEXT ON HOVER */
            [data-testid="stSidebar"]:hover [data-testid="stSidebarNavItems"] span,
            [data-testid="stSidebar"]:hover .stMarkdown p,
            [data-testid="stSidebar"]:hover button div p {
                opacity: 1;
            }
            
            /* 5. Fix for the Logout button specifically */
            [data-testid="stSidebar"] button {
                border: none !important;
                justify-content: flex-start !important;
                padding-left: 15px !important;
            }
        </style>
    """, unsafe_allow_html=True)

def show_sidebar():
    """Renders the hoverable sidebar and returns the user's menu choice"""
    with st.sidebar:
        st.markdown(f"### 👤")
        st.write(f"**{st.session_state.full_name}**")
        st.caption(f"{st.session_state.user_email}")
        st.write("---")
        
        choice = st.radio(
            "Menu",
            ["🧞‍♂️ Search", "⚙️ Profile"],
            label_visibility="collapsed"
        )
        
        st.write("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
            
    return choice

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
