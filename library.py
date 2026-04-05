import streamlit as st
import time

def get_user_library(st_supabase, user_id):
    try:
        res = st_supabase.table("user_interaction").select("*").eq("user_id", user_id).execute()
        return res.data
    except Exception as e:
        st.error(f"Error fetching library: {e}")
        return []

def show_library_page(st_supabase, df_books):
    st.title("My Library")
    
    user_id = st.session_state.get('user_id')
    if not user_id:
        st.warning("Please log in to see your saved books!")
        return

    user_data = get_user_library(st_supabase, user_id)

    if not user_data:
        st.info("Your library is empty. Go find some books to rate!")
        return

    for item in user_data:
        book_row = df_books[df_books['book_id'] == item['book_id']]
        
        if not book_row.empty:
            book = book_row.iloc[0]
            
            with st.container(border=True):
                col1, col2 = st.columns([1, 4])
                
                with col1:
                    # Balanced placeholder image
                    st.image("https://cdn-icons-png.flaticon.com/512/3429/3429149.png", use_container_width=True)
                
                with col2:
                    st.subheader(book['title'])
                    st.caption(f"Book Description: {book['description']}")
                    st.caption(f"Genres: {book['genres']}")
                    st.write(f"**Your Rating:** {'⭐' * item['rating']}")
                    st.info(f"**Review:** {item['review']}")
                    
                    sub1, sub2 = st.columns(2)
                    with sub1:
                        st.link_button("📖 View on Goodreads", book['url'])
                    
                    with sub2:
                        with st.expander("Edit My Review"):
                            new_rating = st.slider("Rating", 1, 5, int(item['rating']), key=f"r_{item['id']}")
                            new_text = st.text_area("Review", item['review'], key=f"t_{item['id']}")
                            
                            if st.button("Save Changes", key=f"b_{item['id']}"):
                                st_supabase.table("user_interaction").update({
                                    "rating": new_rating, 
                                    "review": new_text
                                }).eq("id", item['id']).execute()
                                
                                st.toast(f"Changed saved for {book['title']}!")
                                time.sleep(1)
                                st.rerun()
