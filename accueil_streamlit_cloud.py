#!/usr/bin/env python3
"""
Interface principale pour le déploiement sur Streamlit Cloud
Version simplifiée sans modèle local
"""

import os
import streamlit as st
from PIL import Image, ImageFile
import numpy as np
import pandas as pd
import json
import ast
import requests
import base64
from io import BytesIO

# Configuration
SEED = 42
CSV_PATH = 'produits_demo.csv'
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
        
        # Appliquer l'extraction
        df[['main_category', 'sub_categories']] = df['product_category_tree'].apply(
            lambda x: pd.Series(extract_categories(x))
        )
        
        # Nettoyer les données
        df = df.dropna(subset=['main_category'])
        df = df[df['main_category'] != '']
        
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {str(e)}")
        return pd.DataFrame()

def predict_with_demo_model(image, product_name, description, specifications):
    """Prédiction avec un modèle de démonstration"""
    # Simulation d'une prédiction basée sur des règles simples
    combined_text = f"{product_name} {description} {specifications}".lower()
    
    # Catégories disponibles
    categories = [
        'Baby Care', 'Beauty and Personal Care', 'Computers',
        'Home Decor & Festive Needs', 'Home Furnishing',
        'Kitchen & Dining', 'Watches'
    ]
    
    # Règles simples basées sur les mots-clés
    category_keywords = {
        'Baby Care': ['baby', 'enfant', 'bébé', 'nourrisson', 'couche', 'jouet'],
        'Beauty and Personal Care': ['beauté', 'cosmétique', 'soin', 'shampooing', 'crème', 'maquillage'],
        'Computers': ['ordinateur', 'laptop', 'pc', 'computer', 'écran', 'clavier'],
        'Home Decor & Festive Needs': ['déco', 'décoration', 'fête', 'festif', 'ornement'],
        'Home Furnishing': ['meuble', 'furniture', 'canapé', 'table', 'chaise', 'lit'],
        'Kitchen & Dining': ['cuisine', 'kitchen', 'vaisselle', 'casserole', 'four', 'réfrigérateur'],
        'Watches': ['montre', 'watch', 'horloge', 'chronomètre', 'bracelet']
    }
    
    # Calculer les scores
    scores = {}
    for category, keywords in category_keywords.items():
        score = sum(1 for keyword in keywords if keyword in combined_text)
        scores[category] = score / len(keywords)
    
    # Prédiction
    if max(scores.values()) > 0:
        predicted_category = max(scores, key=scores.get)
        confidence = max(scores.values())
    else:
        predicted_category = 'Home Furnishing'  # Catégorie par défaut
        confidence = 0.1
    
    return {
        'predicted_category': predicted_category,
        'confidence': confidence,
        'category_scores': scores
    }

def main():
    """Fonction principale de l'application"""
    
    # Appliquer les styles d'accessibilité
    apply_accessibility_styles()
    
    # Configuration de la page
    st.set_page_config(
        page_title="Application CLIP - Classification de Produits",
        page_icon="🛍️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Sidebar d'accessibilité
    render_accessibility_sidebar()
    
    # Titre principal
    st.title("🛍️ Application CLIP - Classification de Produits")
    st.markdown("---")
    
    # Navigation
    st.sidebar.title("📋 Navigation")
    page = st.sidebar.selectbox(
        "Choisissez une page :",
        ["🏠 Accueil", "📊 Analyse des Données", "🔮 Prédiction de Catégorie"]
    )
    
    if page == "🏠 Accueil":
        st.header("🏠 Page d'Accueil")
        st.markdown("""
        ### Bienvenue dans l'Application CLIP !
        
        Cette application utilise un modèle CLIP pour classifier des produits en fonction de leur image et description.
        
        #### 🎯 Fonctionnalités disponibles :
        - **📊 Analyse des Données** : Exploration des données de produits
        - **🔮 Prédiction de Catégorie** : Classification d'images de produits
        
        #### 🚀 Comment utiliser l'application :
        1. Naviguez vers la page "Prédiction de Catégorie"
        2. Uploadez une image de produit
        3. Ajoutez une description (optionnel)
        4. Obtenez la prédiction de catégorie
        
        #### 📱 Accessibilité :
        - Mode contraste élevé
        - Texte agrandi
        - Mode daltonien
        - Navigation au clavier
        """)
        
    elif page == "📊 Analyse des Données":
        st.header("📊 Analyse des Données")
        
        # Charger les données
        df = load_and_process_data()
        
        if not df.empty:
            st.subheader("📈 Statistiques générales")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total des produits", len(df))
            
            with col2:
                st.metric("Catégories uniques", df['main_category'].nunique())
            
            with col3:
                st.metric("Prix moyen", f"₹{df['retail_price'].mean():.2f}")
            
            with col4:
                st.metric("Prix médian", f"₹{df['retail_price'].median():.2f}")
            
            # Distribution des catégories
            st.subheader("📊 Distribution des catégories")
            category_counts = df['main_category'].value_counts()
            st.bar_chart(category_counts)
            
            # Top 10 des catégories
            st.subheader("🏆 Top 10 des catégories")
            st.dataframe(category_counts.head(10))
            
        else:
            st.warning("⚠️ Aucune donnée disponible pour l'analyse")
    
    elif page == "🔮 Prédiction de Catégorie":
        st.header("🔮 Prédiction de Catégorie")
        
        st.markdown("""
        ### 🎯 Classification de produits avec CLIP
        
        Uploadez une image de produit et obtenez sa catégorie prédite.
        """)
        
        # Interface de prédiction
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📤 Upload de l'image")
            uploaded_file = st.file_uploader(
                "Choisissez une image de produit",
                type=['png', 'jpg', 'jpeg'],
                help="Formats supportés : PNG, JPG, JPEG"
            )
            
            if uploaded_file is not None:
                # Afficher l'image
                image = Image.open(uploaded_file)
                st.image(image, caption="Image uploadée", use_column_width=True)
                
                # Informations sur l'image
                st.info(f"📏 Dimensions : {image.size[0]} x {image.size[1]} pixels")
        
        with col2:
            st.subheader("📝 Informations du produit")
            
            product_name = st.text_input(
                "Nom du produit",
                placeholder="Ex: iPhone 14 Pro"
            )
            
            description = st.text_area(
                "Description du produit",
                placeholder="Ex: Smartphone haut de gamme avec caméra professionnelle"
            )
            
            specifications = st.text_area(
                "Spécifications techniques",
                placeholder="Ex: 6.1 pouces, 128GB, iOS 16"
            )
            
            # Bouton de prédiction
            if st.button("🔮 Prédire la catégorie", type="primary"):
                if uploaded_file is not None:
                    with st.spinner("🔄 Analyse en cours..."):
                        # Prédiction
                        result = predict_with_demo_model(
                            image, product_name, description, specifications
                        )
                        
                        # Affichage des résultats
                        st.success("✅ Prédiction terminée !")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric(
                                "Catégorie prédite",
                                result['predicted_category']
                            )
                        
                        with col2:
                            st.metric(
                                "Confiance",
                                f"{result['confidence']:.2%}"
                            )
                        
                        # Scores détaillés
                        st.subheader("📊 Scores par catégorie")
                        scores_df = pd.DataFrame(
                            list(result['category_scores'].items()),
                            columns=['Catégorie', 'Score']
                        ).sort_values('Score', ascending=False)
                        
                        st.bar_chart(scores_df.set_index('Catégorie'))
                        st.dataframe(scores_df)
                        
                else:
                    st.error("❌ Veuillez uploader une image avant de faire une prédiction")
        
        # Informations sur le modèle
        st.markdown("---")
        st.info("""
        ℹ️ **Note** : Cette version de démonstration utilise des règles simples pour la prédiction.
        Pour une prédiction plus précise, utilisez la version complète avec le modèle CLIP fine-tuné.
        """)

if __name__ == "__main__":
    main()
