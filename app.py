import streamlit as st
import torch
import pandas as pd
import numpy as np
import joblib
from transformers import BertTokenizer, BertForSequenceClassification
from engine import get_predictions, get_recommendations

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="BookGenie AI", page_icon="🧞‍♂️", layout="wide")

# 2. ASSET LOADING (Cached for speed)
@st.cache_resource
def load_assets():
    token = st.secrets["HF_TOKEN"]
    model_id = "iffahizzah23/BERT_BookGenie"
    model = BertForSequenceClassification.from_pretrained(model_id, token=token)
    model.eval()
    tokenizer = BertTokenizer.from_pretrained(model_id, token=token)
    mlb = joblib.load('mlb_model.pkl')
    df = pd.read_csv('book_details.csv')
    embeddings = np.load('book_embeddings.npy')
    return model, tokenizer, mlb, df, embeddings

# Initialize assets
model, tokenizer, mlb, df, library_embeddings = load_assets()

# 3. SIDEBAR
with st.sidebar:
    st.title("📖 About BookGenie")
    st.info("This AI uses a BERT model to analyze story summaries and recommend similar books.")
    st.write("---")
    st.caption("Final Year Project 2026")

# 4. MAIN INTERFACE
st.title("🧞‍♂️ BookGenie: Your AI Librarian")
st.markdown("Type a book summary or a story idea below, and I'll find its genre and similar reads!")

user_query = st.text_area("What kind of story is on your mind?", height=150, placeholder="e.g., A detective solving a mystery in a futuristic city...")

if st.button("✨ Work Your Magic"):
    if user_query:
        with st.spinner("The Genie is reading..."):
            # A. Call the Identifier from engine.py
            genres = get_predictions(user_query, model, tokenizer, mlb)

            # B. Call the Recommender from engine.py
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
                        st.write(f"**Genres:** {book['revised_genres']}")
                        st.write("---")
                        st.write(f"_{book['description']}_")
    else:
        st.error("Please enter a description first!")
