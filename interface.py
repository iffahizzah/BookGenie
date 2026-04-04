import streamlit as st

def apply_custom_css():
    st.markdown("""
        <style>
            /* 1. Sidebar Width */
            [data-testid="stSidebar"] {
                min-width: 250px !important;
            }

            /* 2. THE CIRCLE VANISHER */
            /* This hides the radio button circle container entirely */
            [data-testid="stSidebar"] [data-testid="stWidgetLabel"] + div div[data-baseweb="radio"] > div:first-child {
                display: none !important;
            }
            
            /* Remove the default dot/circle padding */
            [data-testid="stSidebar"] label[data-baseweb="radio"] {
                padding-left: 0px !important;
            }

            /* 3. MENU ITEM STYLING */
            [data-testid="stSidebar"] div[role="radiogroup"] label {
                padding: 12px 15px !important;
                border-radius: 8px !important;
                margin-bottom: 6px !important;
                transition: all 0.2s ease;
                cursor: pointer;
                width: 100% !important;
            }

            /* Hover Effect */
            [data-testid="stSidebar"] div[role="radiogroup"] label:hover {
                background-color: rgba(151, 166, 195, 0.1) !important;
            }

            /* Active/Selected Effect (Blue highlight with bar) */
            [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
                background-color: rgba(0, 123, 255, 0.15) !important;
                border-left: 5px solid #007bff !important;
                border-radius: 2px 8px 8px 2px !important;
            }

            /* 4. Text Alignment Fix */
            /* Ensures text stays left-aligned now that the circle is gone */
            [data-testid="stSidebar"] div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p {
                font-size: 1.1rem !important;
                margin-left: 0px !important;
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
