import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np
import json
import os
import pandas as pd
import re

alay_dict = {}
alay_path = "utils/new_kamusalay.csv"
if os.path.exists(alay_path):
    df_alay = pd.read_csv(alay_path, header=None, names=["alay", "normal"], encoding="latin-1")
    alay_dict = dict(zip(df_alay["alay"], df_alay["normal"]))

# Preprocessing function
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r"http\S+|www\S+|pic.twitter\S+", " ", text)
    text = re.sub(r"@\w+|#\w+", " ", text)
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    # Normalisasi alay
    words = text.split()
    normalized = [alay_dict.get(word, word) for word in words]
    return " ".join(normalized)

# Load model dan tokenizer
def load_model_and_tokenizer(model_dir="saved-model", threshold_file="optimal_thresholds.json"):
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    model = AutoModelForSequenceClassification.from_pretrained(model_dir)
    model.eval()

    with open(threshold_file, "r") as f:
        thresholds = json.load(f)

    label_names = list(thresholds.keys())
    return model, tokenizer, thresholds, label_names

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

# Fungsi prediksi untuk teks
def predict_texts(texts, model, tokenizer, thresholds, label_names):
    # Preprocess dulu
    texts_clean = [preprocess_text(t) for t in texts]

    encoded = tokenizer(texts_clean, padding=True, truncation=True, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**encoded)
        logits = outputs.logits.cpu().numpy()

    probs = sigmoid(logits)
    results = []

    for i, text_probs in enumerate(probs):
        result = {"text": texts[i]}  # Teks asli
        for j, label in enumerate(label_names):
            score = float(text_probs[j])
            is_active = int(score >= thresholds[label])
            result[label] = is_active
            result[f"{label}_score"] = round(score, 3)
        results.append(result)

    return results
