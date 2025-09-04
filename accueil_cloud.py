#!/usr/bin/env python3
"""
Interface principale pour le déploiement cloud avec Azure ML
"""

import os
import streamlit as st
from PIL import Image, ImageFile
import numpy as np
import pandas as pd
import json
import ast
from azure_client import get_azure_client

# Configuration
SEED = 42
CSV_PATH = 'produits_original.csv'
IMAGE_FOLDER = 'images_original'

ImageFile.LOAD_TRUNCATED_IMAGES = True
Image.MAX_IMAGE_PIXELS = None

# Importer le module d'accessibilité
from accessibility import init_accessibility_state, render_accessibility_sidebar, apply_accessibility_styles

# Initialiser l'état d'accessibilité
init_accessibility_state()

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

# Charger les données pour l'EDA
if 'df' not in st.session_state:
    with st.spinner("🔄 Chargement des données..."):
        st.session_state.df = load_and_process_data()

# Initialiser le client Azure ML
if 'azure_client' not in st.session_state:
    st.session_state.azure_client = get_azure_client()

# Configuration de la page (définie une seule fois)
st.set_page_config(
    page_title="Dashboard de Classification de Produits avec CLIP - Cloud",
    page_icon="☁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Titre principal
st.title("☁️ Accueil - Version Cloud")
st.markdown("---")

# Vérifier le statut du service Azure ML
service_status = st.session_state.azure_client.get_service_status()
if service_status['status'] == 'healthy':
    st.success(f"✅ {service_status['message']}")
elif service_status['status'] == 'local':
    st.info(f"ℹ️ {service_status['message']}")
else:
    st.warning(f"⚠️ {service_status['message']}")

# Texte de présentation
st.markdown("""
## 🎯 Bienvenue sur le Dashboard de Classification de Produits avec CLIP - Version Cloud

Cette application utilise un modèle **CLIP (Contrastive Language-Image Pre-training)** fine-tuné déployé sur **Azure ML** pour classifier automatiquement des produits e-commerce en analysant à la fois leurs images et leurs descriptions textuelles.

### 🚀 Fonctionnalités principales

- **📊 Analyse Exploratoire des Données (EDA)** : Explorez les données de produits avec des visualisations interactives
- **🔮 Prédiction de Catégorie** : Classifiez de nouveaux produits en uploadant une image et en fournissant une description
- **☁️ Inférence Cloud** : Les calculs sont effectués sur Azure ML pour des performances optimales
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

### 🔬 Architecture Cloud

- **Frontend** : Streamlit Cloud pour l'interface utilisateur
- **Backend** : Azure ML pour l'inférence du modèle CLIP
- **Modèle** : CLIP fine-tuné sur les données de produits e-commerce
- **API** : REST API sécurisée pour les prédictions

### 🔧 Configuration

L'application peut fonctionner en deux modes :
- **Mode Cloud** : Utilise l'API Azure ML (recommandé)
- **Mode Local** : Fallback vers le modèle local si l'API n'est pas disponible

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
    if service_status['status'] == 'healthy':
        st.success("✅ **Service Azure ML actif**")
        st.caption("Prêt pour les prédictions cloud")
    elif service_status['status'] == 'local':
        st.info("ℹ️ **Mode local**")
        st.caption("Utilisation du modèle local")
    else:
        st.error("❌ **Service non disponible**")

with col3:
    st.info("☁️ **Cloud**")
    st.caption("Déployé sur Streamlit Cloud")

st.markdown("---")

# Afficher les options d'accessibilité dans la sidebar
render_accessibility_sidebar()

# Appliquer les styles d'accessibilité
apply_accessibility_styles()
