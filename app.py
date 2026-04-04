import streamlit as st
import numpy as np
from huggingface_hub import hf_hub_download
import joblib
import pandas as pd
from transformers import BertTokenizer, BertForSequenceClassification
from engine import get_predictions, get_recommendations
from st_supabase_connection import SupabaseConnection
from auth import show_auth_page
from interface import apply_custom_css, show_sidebar, show_profile_page, show_main_genie_page
import extra_streamlit_components as stx

#SETUP
st.set_page_config(page_title="BookGenie", page_icon="🧞‍♂️", layout="wide")
st_supabase = st.connection("supabase", type=SupabaseConnection)
cookie_manager = stx.CookieManager()

#SECURITY GATE
is_authenticated = show_auth_page(st_supabase, cookie_manager)

if is_authenticated:    
    apply_custom_css()
    menu_choice = show_sidebar()
    
    if menu_choice == "⚙️ Profile":
        show_profile_page(st_supabase)
        
    else:
        @st.cache_resource
        def load_assets():
            token = st.secrets["HF_TOKEN"]
            model_id = "iffahizzah23/BERT_BookGenie"
            
            mlb_path = hf_hub_download(repo_id=model_id, filename="mlb_model.pkl", token=token)
            mlb = joblib.load(mlb_path)
            
            model = BertForSequenceClassification.from_pretrained(model_id, token=token)
            tokenizer = BertTokenizer.from_pretrained(model_id, token=token)
            
            df = pd.read_csv('book_details.csv')
            library_embeddings = np.load('book_embeddings.npy')
            
            return model.eval(), tokenizer, mlb, df, library_embeddings
        
        model, tokenizer, mlb, df, library_embeddings = load_assets()
        show_main_genie_page(model, tokenizer, mlb, df, library_embeddings, get_predictions, get_recommendations, np)
