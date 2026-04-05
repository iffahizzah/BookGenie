import streamlit as st

def get_user_library(st_supabase, user_id):
    """Fetch all saved rows for this specific user"""
    try:
        res = st_supabase.table("user_interaction").select("*").eq("user_id", user_id).execute()
        return res.data
    except Exception as e:
        st.error(f"Error fetching library: {e}")
        return []

def show_library_page(st_supabase, df_books):
    st.title("📚 My BookGenie Library")
    
    user_id = st.session_state.get('user_id')
    
    if not user_id:
        st.warning("Please log in to see your saved books!")
        return

    # 1. Fetch the data from Supabase
    user_data = get_user_library(st_supabase, user_id)

    if not user_data:
        st.info("Your library is empty. Go find some books to rate!")
        return

    # 2. Loop through and display
    for item in user_data:
        # Find the book details in your dataframe using 'book_id' (Column E in your CSV)
        book_row = df_books[df_books['book_id'] == item['book_id']]
        
        if not book_row.empty:
            book = book_row.iloc[0]
            
            with st.container(border=True):
                col1, col2 = st.columns([1, 4])
                
                with col1:
                    # ✅ FALLBACK: Since we don't have image_url, show a nice icon card
                    st.markdown("""
                        <div style="background-color: #262730; border-radius: 10px; height: 150px; display: flex; align-items: center; justify-content: center; border: 1px solid #464b5d;">
                            <h1 style="margin:0;">📘</h1>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.subheader(book['title'])
                    # We'll use genres as a caption since authors isn't in your main CSV view
                    st.caption(f"Genres: {book['genres']}") 
                    
                    st.write(f"**Your Rating:** {'⭐' * item['rating']}")
                    st.info(f"**Your Review:** {item['review']}")
                    
                    # Buttons for external links and editing
                    sub_col1, sub_col2 = st.columns(2)
                    with sub_col1:
                        # ✅ FIXED: Matches your CSV column 'url'
                        st.link_button("📖 View on Goodreads", book['url'])
                    
                    with sub_col2:
                        with st.expander("Edit My Review"):
                            new_rating = st.slider("Rating", 1, 5, int(item['rating']), key=f"r_{item['id']}")
                            new_text = st.text_area("Review", item['review'], key=f"t_{item['id']}")
                            if st.button("Save Changes", key=f"b_{item['id']}"):
                                st_supabase.table("user_interaction").update({
                                    "rating": new_rating, 
                                    "review": new_text
                                }).eq("id", item['id']).execute()
                                st.success("Updated!")
                                st.rerun()
