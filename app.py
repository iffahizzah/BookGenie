import streamlit as st
import numpy as np
import joblib
import pandas as pd
from transformers import BertTokenizer, BertForSequenceClassification
from engine import get_predictions, get_recommendations
from st_supabase_connection import SupabaseConnection
from auth import show_auth_page
from interface import apply_custom_css, show_sidebar, show_profile_page, show_main_genie_page

# 1. SETUP
st.set_page_config(page_title="BookGenie AI", page_icon="🧞‍♂️", layout="wide")
st_supabase = st.connection("supabase", type=SupabaseConnection)

# 2. SECURITY GATE
is_authenticated = show_auth_page(st_supabase, cookie_manager)

if is_authenticated:    
    apply_custom_css()
    menu_choice = show_sidebar()
    
    if menu_choice == "⚙️ Profile":
        show_profile_page()
        
    else:
        # 3. LOAD AI ASSETS
        @st.cache_resource
        def load_assets():
            token = st.secrets["HF_TOKEN"]
            model_id = "iffahizzah23/BERT_BookGenie"
            model = BertForSequenceClassification.from_pretrained(model_id, token=token)
            tokenizer = BertTokenizer.from_pretrained(model_id, token=token)
            return (model.eval(), tokenizer, joblib.load('mlb_model.pkl'), 
                    pd.read_csv('book_details.csv'), np.load('book_embeddings.npy'))
        
        # 4. RUN INTERFACE
        model, tokenizer, mlb, df, library_embeddings = load_assets()
        show_main_genie_page(model, tokenizer, mlb, df, library_embeddings, get_predictions, get_recommendations, np)
