import streamlit as st
import time

def get_user_library(st_supabase, user_id):
    try:
        res = st_supabase.table("user_interaction").select("*").eq("user_id", user_id).execute()
        return res.data
    except Exception as e:
        st.error(f"Error fetching library: {e}")
        return []

import time

def show_library_page(st_supabase, df_books):
    st.title("📚 My Library")
    
    user_id = st.session_state.get('user_id')
    if not user_id:
        st.warning("Please log in to see your saved books!")
        return

    user_data = get_user_library(st_supabase, user_id)
    
    if not user_data:
        st.info("Your library is empty. Go find some books to rate!")
        return

    tab1, tab2 = st.tabs(["❤️ Wishlist", "⭐ Reviewed Books",])

    with tab1:
        wishlist_items = [item for item in user_data if item.get('wishlist', False)]
        
        if not wishlist_items:
            st.info("Your wishlist is empty. Heart some books to see them here!")
        else:
            for item in wishlist_items:
                display_book_card(item, df_books, st_supabase, is_wishlist_view=True)

    with tab2:
        reviewed_books = [item for item in user_data if not item.get('wishlist', False)]
        
        if not reviewed_books:
            st.info("You haven't reviewed any books yet.")
        else:
            for item in reviewed_books:
                display_book_card(item, df_books, st_supabase, is_wishlist_view=False)


def display_book_card(item, df_books, st_supabase, is_wishlist_view):
    book_row = df_books[df_books['book_id'] == item['book_id']]
    
    if not book_row.empty:
        book = book_row.iloc[0]
        
        with st.container(border=True):
            col1, col2 = st.columns([1, 4])
            
            with col1:
                st.image("https://cdn-icons-png.flaticon.com/512/3429/3429149.png", use_container_width=True)
            
            with col2:
                st.subheader(book['title'])
                st.caption(f"Description: {book['description']}")
                st.caption(f"Genres: {book['genres']}")
                
                if not is_wishlist_view:
                    st.write(f"**Your Rating:** {'⭐' * item['rating']}")
                    st.info(f"**Review:** {item['review']}")
                else:
                    st.write("📍 *Currently in your reading list.*")

                if is_wishlist_view:
                    sub1, sub2, sub3 = st.columns(3)
                    
                    with sub1:
                        st.link_button("📖 View on Goodreads", book['url'], use_container_width=True)

                    with sub2:
                        with st.expander("⭐ Mark as Read"):
                            w_rating = st.feedback("stars", key=f"wr_{item['id']}")
                            w_review = st.text_area("What did you think?", key=f"wt_{item['id']}")
                            
                            if st.button("Submit & Move", key=f"wb_{item['id']}", use_container_width=True):
                                st_supabase.table("user_interaction").update({
                                    "wishlist": False,
                                    "rating": w_rating if w_rating is not None else 0,
                                    "review": w_review
                                }).eq("id", item['id']).execute()
                                
                                st.success("Moved to library!")
                                time.sleep(1)
                                st.rerun()

                    with sub3:
                        if st.button("🗑️ Remove", key=f"del_{item['id']}", use_container_width=True):
                            st_supabase.table("user_interaction").delete().eq("id", item['id']).execute()
                            st.toast("Removed!")
                            time.sleep(1)
                            st.rerun()
                
                else:
                    sub1, sub2 = st.columns(2)
                    
                    with sub1:
                        st.link_button("📖 View on Goodreads", book['url'], use_container_width=True)

                    with sub2:
                        with st.expander("Edit My Review"):
                            new_rating = st.slider("Rating", 1, 5, int(item['rating']), key=f"r_{item['id']}")
                            new_text = st.text_area("Review", item['review'], key=f"t_{item['id']}")
                            
                            if st.button("Save Changes", key=f"b_{item['id']}", use_container_width=True):
                                st_supabase.table("user_interaction").update({
                                    "rating": new_rating, 
                                    "review": new_text
                                }).eq("id", item['id']).execute()
                                st.toast("Changes saved!")
                                time.sleep(1)
                                st.rerun()
