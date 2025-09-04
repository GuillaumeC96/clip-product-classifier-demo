#!/usr/bin/env python3
"""
Interface principale avec switch entre mode clair et mode contraste élevé
"""

import os
import torch
import streamlit as st
from PIL import Image, ImageFile
import numpy as np
import pandas as pd
import json
import ast
try:
    from transformers import CLIPModel, CLIPTokenizer, CLIPProcessor
except ImportError as e:
    st.error(f"❌ Erreur lors de l'importation des modules CLIP depuis transformers: {str(e)}")
    st.error("Veuillez installer ou mettre à jour la bibliothèque transformers avec 'pip install --upgrade transformers'")
    raise
from sklearn.preprocessing import LabelEncoder
import random
import torch.nn as nn

# Configuration
SEED = 42
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
MODEL_NAME = 'openai/clip-vit-base-patch32'
CHECKPOINT_PATH = 'clip_product_classifier.pth'
CSV_PATH = 'produits_original.csv'
IMAGE_FOLDER = 'images_original'

ImageFile.LOAD_TRUNCATED_IMAGES = True
Image.MAX_IMAGE_PIXELS = None

os.environ['PYTHONHASHSEED'] = str(SEED)
os.environ['CUBLAS_WORKSPACE_CONFIG'] = ':4096:8'
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
torch.cuda.manual_seed(SEED)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False

class CLIPClassifier:
    """Wrapper pour le classificateur CLIP avec tous ses composants"""
    
    def __init__(self, model, processor, tokenizer, label_encoder, device):
        self.model = model
        self.processor = processor
        self.tokenizer = tokenizer
        self.label_encoder = label_encoder
        self.device = device

@st.cache_resource
def load_clip_classifier():
    """Charge le classificateur CLIP fine-tuné"""
    try:
        from transformers import CLIPModel, CLIPProcessor, CLIPTokenizer
        from sklearn.preprocessing import LabelEncoder
        
        # Définir les catégories (basées sur les données)
        categories = [
            'Baby Care',
            'Beauty and Personal Care', 
            'Computers',
            'Home Decor & Festive Needs',
            'Home Furnishing',
            'Kitchen & Dining',
            'Watches'
        ]
        
        # Créer le label encoder
        label_encoder = LabelEncoder()
        label_encoder.fit(categories)
        
        # Créer le modèle CLIP pour classification
        class CLIPForClassification(torch.nn.Module):
            def __init__(self, num_labels):
                super().__init__()
                self.clip = CLIPModel.from_pretrained(MODEL_NAME)
                self.classifier = torch.nn.Linear(self.clip.config.projection_dim * 2, num_labels)
                
            def forward(self, pixel_values, input_ids, attention_mask, labels=None):
                outputs = self.clip(pixel_values=pixel_values, input_ids=input_ids, attention_mask=attention_mask)
                pooled_output = torch.cat((outputs.image_embeds, outputs.text_embeds), dim=-1)
                logits = self.classifier(pooled_output)
                return logits
        
        # Charger le modèle
        model = CLIPForClassification(num_labels=len(categories)).to(device)
        
        # Charger les poids fine-tunés si disponibles
        if os.path.exists(CHECKPOINT_PATH):
            state_dict = torch.load(CHECKPOINT_PATH, map_location=device)
            model.load_state_dict(state_dict, strict=False)
            st.success(f"✅ Modèle fine-tuné chargé depuis {CHECKPOINT_PATH}")
        else:
            st.warning(f"⚠️ Fichier de modèle non trouvé: {CHECKPOINT_PATH}. Utilisation du modèle pré-entraîné.")
        
        # Charger le processeur et tokenizer
        processor = CLIPProcessor.from_pretrained(MODEL_NAME)
        tokenizer = CLIPTokenizer.from_pretrained(MODEL_NAME)
        
        # Créer le wrapper
        classifier = CLIPClassifier(model, processor, tokenizer, label_encoder, device)
        
        return classifier
        
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement du classificateur: {str(e)}")
        return None

@st.cache_data
def load_and_process_data():
    """Charge et traite les données pour l'EDA"""
    try:
        # Charger le CSV original
        df = pd.read_csv(CSV_PATH)
        
        # Traiter la colonne product_category_tree pour extraire main_category et sub_categories
        def extract_categories(category_tree):
            if pd.isna(category_tree):
                return None, None
            try:
                # Parser la chaîne JSON
                categories = ast.literal_eval(category_tree)
                if isinstance(categories, list) and len(categories) > 0:
                    full_path = categories[0]
                    parts = full_path.split(' >> ')
                    main_category = parts[0] if len(parts) > 0 else None
                    sub_categories = ' >> '.join(parts[1:]) if len(parts) > 1 else None
                    return main_category, sub_categories
            except:
                pass
            return None, None
        
        # Appliquer l'extraction des catégories
        category_data = df['product_category_tree'].apply(extract_categories)
        df['main_category'] = [x[0] for x in category_data]
        df['sub_categories'] = [x[1] for x in category_data]
        
        # Créer le chemin des images
        df['image_path'] = df['image'].apply(lambda x: os.path.join(IMAGE_FOLDER, x) if pd.notna(x) else None)
        
        # Vérifier l'existence des images et calculer leurs propriétés
        def check_image_properties(image_path):
            if pd.isna(image_path) or not os.path.exists(image_path):
                return False, 0, 0.0
            try:
                with Image.open(image_path) as img:
                    width, height = img.size
                    num_pixels = width * height
                    aspect_ratio = height / width if width > 0 else 0.0
                    return True, num_pixels, aspect_ratio
            except:
                return False, 0, 0.0
        
        # Appliquer la vérification des images
        image_data = df['image_path'].apply(check_image_properties)
        df['image_exists'] = [x[0] for x in image_data]
        df['num_pixels'] = [x[1] for x in image_data]
        df['aspect_ratio'] = [x[2] for x in image_data]
        
        # Filtrer les lignes avec des catégories principales valides
        df = df[df['main_category'].notna()]
        
        return df
        
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement des données: {str(e)}")
        return pd.DataFrame()

# Importer le module d'accessibilité
from accessibility import init_accessibility_state, render_accessibility_sidebar, apply_accessibility_styles

# Initialiser l'état d'accessibilité
init_accessibility_state()

# Charger les données pour l'EDA
if 'df' not in st.session_state:
    with st.spinner("🔄 Chargement des données..."):
        st.session_state.df = load_and_process_data()

# Charger le classificateur CLIP
if 'classifier' not in st.session_state:
    with st.spinner("🤖 Chargement du classificateur CLIP..."):
        st.session_state.classifier = load_clip_classifier()

# Configuration de la page (définie une seule fois)
st.set_page_config(
    page_title="Dashboard de Classification de Produits avec CLIP",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Titre principal
st.title("🏠 Accueil")
st.markdown("---")

# Texte de présentation
st.markdown("""
## 🎯 Bienvenue sur le Dashboard de Classification de Produits avec CLIP

Cette application utilise un modèle **CLIP (Contrastive Language-Image Pre-training)** fine-tuné pour classifier automatiquement des produits e-commerce en analysant à la fois leurs images et leurs descriptions textuelles.

### 🚀 Fonctionnalités principales

- **📊 Analyse Exploratoire des Données (EDA)** : Explorez les données de produits avec des visualisations interactives
- **🔮 Prédiction de Catégorie** : Classifiez de nouveaux produits en uploadant une image et en fournissant une description
- **👁️ Accessibilité** : Interface adaptée avec options de contraste élevé, texte agrandi et mode daltonien

### 🎨 Options d'accessibilité disponibles

- **🌙 Mode contraste élevé** : Interface sombre avec contraste maximal
- **🔍 Texte agrandi** : Augmentation de la taille des polices
- **🎨 Mode daltonien** : Couleurs optimisées pour les personnes daltoniennes

### 📈 Données analysées

L'application traite un dataset de **plus de 1000 produits** répartis en **7 catégories principales** :
- 👶 Baby Care
- 💄 Beauty and Personal Care  
- 💻 Computers
- 🏠 Home Decor & Festive Needs
- 🛋️ Home Furnishing
- 🍽️ Kitchen & Dining
- ⌚ Watches

### 🔬 Technologie utilisée

- **Modèle CLIP** : Modèle de vision par ordinateur et traitement du langage naturel
- **Fine-tuning** : Entraînement spécialisé sur les données de produits e-commerce
- **Streamlit** : Interface web interactive et responsive
- **Plotly** : Visualisations interactives et accessibles

---

**💡 Conseil** : Utilisez les options d'accessibilité dans la barre latérale pour personnaliser votre expérience selon vos besoins.
""")

st.markdown("---")

# Section d'information sur l'état de l'application
col1, col2, col3 = st.columns(3)

with col1:
    if 'df' in st.session_state and not st.session_state.df.empty:
        st.success("✅ **Données chargées**")
        st.caption(f"{len(st.session_state.df)} produits disponibles")
    else:
        st.error("❌ **Données non chargées**")

with col2:
    if 'classifier' in st.session_state and st.session_state.classifier is not None:
        st.success("✅ **Modèle CLIP chargé**")
        st.caption("Prêt pour les prédictions")
    else:
        st.error("❌ **Modèle non chargé**")

with col3:
    device_info = "🖥️ CPU" if device.type == 'cpu' else "🚀 GPU"
    st.info(f"**{device_info}**")
    st.caption(f"Calcul sur {device}")

st.markdown("---")

# Afficher les options d'accessibilité dans la sidebar
render_accessibility_sidebar()

# Appliquer les styles d'accessibilité
apply_accessibility_styles()
