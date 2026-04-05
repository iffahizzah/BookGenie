import streamlit as st

def show_library_page(st_supabase, df_books):
    st.title("📚 My Library")
    st.write("Your personal collection of rated and reviewed books.")

    user_id = st.session_state.get('user_id')
    if not user_id:
        st.warning("Please log in to view your library.")
        return

    # 1. Get user data
    saved_interactions = get_user_library(st_supabase, user_id)

    if not saved_interactions:
        st.info("Your library is empty. Start rating some books!")
        return

    # 2. Display each book
    for item in saved_interactions:
        # Match the ID from Supabase to your local CSV/Dataframe
        book_data = df_books[df_books['id'] == item['book_id']].iloc[0]
        
        with st.container(border=True):
            col1, col2 = st.columns([1, 3])
            
            with col1:
                # Assuming you have an image URL column
                st.image(book_data['image_url'], width=100) 
            
            with col2:
                st.subheader(book_data['title'])
                st.write(f"**Your Rating:** {'⭐' * item['rating']}")
                st.write(f"**Your Review:** {item['review']}")
                
                # --- The Edit Section ---
                with st.expander("📝 Edit Review"):
                    new_rating = st.slider("Update Rating", 1, 5, int(item['rating']), key=f"rate_{item['id']}")
                    new_review = st.text_area("Update Comment", item['review'], key=f"rev_{item['id']}")
                    
                    if st.button("Update Info", key=f"btn_{item['id']}"):
                        st_supabase.table("user_interaction").update({
                            "rating": new_rating,
                            "review": new_review
                        }).eq("id", item['id']).execute()
                        st.success("Updated!")
                        st.rerun()
