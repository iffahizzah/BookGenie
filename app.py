import streamlit as st
import numpy as np
import joblib
import pandas as pd
from huggingface_hub import hf_hub_download
from transformers import BertTokenizer, BertForSequenceClassification
import extra_streamlit_components as stx

from engine import get_predictions, get_recommendations
from st_supabase_connection import SupabaseConnection
from auth import show_auth_page
from interface import apply_custom_css, show_sidebar, show_profile_page
import library

# --- 1. SETUP & CONFIG ---
st.set_page_config(page_title="BookGenie", page_icon="🧞‍♂️", layout="wide")
st_supabase = st.connection("supabase", type=SupabaseConnection)
cookie_manager = stx.CookieManager()

# --- 2. ASSET LOADING (Global) ---
@st.cache_resource
def load_assets():
    token = st.secrets["HF_TOKEN"]
    model_id = "iffahizzah23/BERT_BookGenie"
    
    # Download and load MLB
    mlb_path = hf_hub_download(repo_id=model_id, filename="mlb_model.pkl", token=token)
    mlb = joblib.load(mlb_path)
    
    # Load Model and Tokenizer
    model = BertForSequenceClassification.from_pretrained(model_id, token=token)
    tokenizer = BertTokenizer.from_pretrained(model_id, token=token)
    
    # Load Data
    df = pd.read_csv('book_details.csv')
    library_embeddings = np.load('book_embeddings.npy')
    
    return model.eval(), tokenizer, mlb, df, library_embeddings

# Pre-load everything
model, tokenizer, mlb, df, library_embeddings = load_assets()

# --- 3. SECURITY GATE ---
is_authenticated = show_auth_page(st_supabase, cookie_manager)

# --- 4. MAIN APP LOGIC ---
if is_authenticated:    
    apply_custom_css()
    menu_choice = show_sidebar()
    
    if menu_choice == "Profile":
        show_profile_page(st_supabase)

    elif menu_choice == "My Library":
        library.show_library_page(st_supabase, df)
        
    else:
        from interface import show_main_genie_page # Import here or at top
        show_main_genie_page(
            model, tokenizer, mlb, df, 
            library_embeddings, get_predictions, 
            get_recommendations, np, st_supabase
        )
