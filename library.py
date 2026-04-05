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

    # 1. Fetch the data
    user_data = get_user_library(st_supabase, user_id)

    if not user_data:
        st.info("Your library is empty. Go find some books to rate!")
        return

    # 2. Loop through and display
    for item in user_data:
        # Find the book details in your dataframe using the book_id
        # We use .get() or a filter to find the row
        book_row = df_books[df_books['id'] == item['book_id']]
        
        if not book_row.empty:
            book = book_row.iloc[0]
            
            with st.container(border=True):
                col1, col2 = st.columns([1, 4])
                
                with col1:
                    # Using the Goodreads image if you have it
                    st.image(book['image_url'], use_container_width=True)
                
                with col2:
                    st.subheader(book['title'])
                    st.caption(f"By {book['authors']}")
                    st.write(f"**Your Rating:** {'⭐' * item['rating']}")
                    st.write(f"**Your Review:** {item['review']}")
                    
                    # Buttons for external links and editing
                    sub_col1, sub_col2 = st.columns(2)
                    with sub_col1:
                        st.link_button("📖 View on Goodreads", book['goodreads_url'])
                    
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
