import torch
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def get_predictions(text, model, tokenizer, mlb):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        logits = model(**inputs).logits
        probs = torch.sigmoid(logits).cpu().numpy()[0]
    predictions = (probs > 0.26).astype(int)
    return mlb.inverse_transform(predictions.reshape(1, -1))[0]

def get_recommendations(text, model, tokenizer, library_embeddings, df):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model.bert(**inputs)
        user_emb = outputs.last_hidden_state[:, 0, :].cpu().numpy()
    sims = cosine_similarity(user_emb, library_embeddings).flatten()
    top_indices = sims.argsort()[-5:][::-1]
    return df.iloc[top_indices], sims[top_indices]
