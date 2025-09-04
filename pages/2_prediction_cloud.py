"""
Page de prédiction pour la version cloud avec Azure ML
"""

import os
import pandas as pd
import streamlit as st
import spacy
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import re
from scipy.interpolate import griddata
from azure_client import get_azure_client

# Importer le module d'accessibilité
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from accessibility import init_accessibility_state, render_accessibility_sidebar, apply_accessibility_styles

# Initialiser l'état d'accessibilité
init_accessibility_state()

st.title("Prédiction de Catégorie - Version Cloud")

# Configuration d'accessibilité
ACCESSIBLE_COLORS = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
HIGH_CONTRAST_COLORS = ['#FFFFFF', '#FF0000', '#00FF00', '#0000FF', '#FFFF00']

# Obtenir le client Azure ML
azure_client = get_azure_client()

# Afficher les options d'accessibilité dans la sidebar
render_accessibility_sidebar()

# Appliquer les styles d'accessibilité
apply_accessibility_styles()

# Load spaCy model on CPU to avoid device mismatch issues
try:
    nlp = spacy.load("en_core_web_trf")
    st.info("⚠️ spaCy running on CPU to ensure stability")
except Exception as e:
    st.error(f"❌ Failed to load spaCy model: {str(e)}")
    st.info("⏳ Downloading spaCy model...")
    os.system("python -m spacy download en_core_web_trf")
    nlp = spacy.load("en_core_web_trf")
    st.info("⚠️ spaCy running on CPU to ensure stability")

def clean_text(text):
    """Clean text using the same replacement patterns as in training."""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    all_patterns = [
        (r'\(', ' ( '),
        (r'\)', ' ) '),
        (r'\.', ' . '),
        (r'\!', ' ! '),
        (r'\?', ' ? '),
        (r'\:', ' : '),
        (r'\,', ', '),
        # Baby Care
        (r'\b(\d+)\s*[-~to]?\s*(\d+)\s*(m|mth|mths|month|months?)\b', 'month'),
        (r'\bnewborn\s*[-~to]?\s*(\d+)\s*(m|mth|months?)\b', 'month'),
        (r'\b(nb|newborn|baby|bb|bby|babie|babies)\b', 'baby'),
        (r'\b(diaper|diapr|nappy)\b', 'diaper'),
        (r'\b(stroller|pram|buggy)\b', 'stroller'),
        (r'\b(bpa\s*free|non\s*bpa)\b', 'bisphenol A free'),
        (r'\b(\d+)\s*(oz|ounce)\b', 'ounce'),
        # Computer Hardware
        (r'\b(rtx\s*\d+)\b', 'ray tracing graphics'),
        (r'\b(gtx\s*\d+)\b', 'geforce graphics'),
        (r'\bnvidia\b', 'nvidia'),
        (r'\b(amd\s*radeon\s*rx\s*\d+)\b', 'amd radeon graphics'),
        (r'\b(intel\s*(core|xeon)\s*[i\d-]+)\b', 'intel processor'),
        (r'\b(amd\s*ryzen\s*[\d]+)\b', 'amd ryzen processor'),
        (r'\bssd\b', 'solid state drive'),
        (r'\bhdd\b', 'hard disk drive'),
        (r'\bwifi\s*([0-9])\b', 'wi-fi standard'),
        (r'\bbluetooth\s*(\d\.\d)\b', 'bluetooth version'),
        (r'\bethernet\b', 'ethernet'),
        (r'\bfhd\b', 'full high definition'),
        (r'\buhd\b', 'ultra high definition'),
        (r'\bqhd\b', 'quad high definition'),
        (r'\boled\b', 'organic light emitting diode'),
        (r'\bips\b', 'in-plane switching'),
        (r'\bram\b', 'random access memory'),
        (r'\bcpu\b', 'central processing unit'),
        (r'\bgpu\b', 'graphics processing unit'),
        (r'\bhdmi\b', 'high definition multimedia interface'),
        (r'\busb\s*([a-z0-9]*)\b', 'universal serial bus'),
        (r'\brgb\b', 'red green blue'),
        # Home Appliances
        (r'\bfridge\b', 'refrigerator'),
        (r'\bwashing\s*machine\b', 'clothes washer'),
        (r'\bdishwasher\b', 'dish washing machine'),
        (r'\boven\b', 'cooking oven'),
        (r'\bmicrowave\b', 'microwave oven'),
        (r'\bhoover\b', 'vacuum cleaner'),
        (r'\btumble\s*dryer\b', 'clothes dryer'),
        (r'\b(a\+)\b', 'energy efficiency class'),
        (r'\b(\d+)\s*btu\b', 'british thermal unit'),
        # Textiles and Materials
        (r'\bpoly\b', 'polyester'),
        (r'\bacrylic\b', 'acrylic fiber'),
        (r'\bnylon\b', 'nylon fiber'),
        (r'\bspandex\b', 'spandex fiber'),
        (r'\blycra\b', 'lycra fiber'),
        (r'\bpvc\b', 'polyvinyl chloride'),
        (r'\bvinyl\b', 'vinyl material'),
        (r'\bstainless\s*steel\b', 'stainless steel'),
        (r'\baluminum\b', 'aluminum metal'),
        (r'\bplexiglass\b', 'acrylic glass'),
        (r'\bpu\s*leather\b', 'polyurethane leather'),
        (r'\bsynthetic\s*leather\b', 'synthetic leather'),
        (r'\bfaux\s*leather\b', 'faux leather'),
        (r'\bwaterproof\b', 'water resistant'),
        (r'\bbreathable\b', 'air permeable'),
        (r'\bwrinkle-free\b', 'wrinkle resistant'),
        # Beauty and Personal Care
        (r'\bSPF\b', 'Sun Protection Factor'),
        (r'\bUV\b', 'Ultraviolet'),
        (r'\bBB\s*cream\b', 'Blemish Balm cream'),
        (r'\bCC\s*cream\b', 'Color Correcting cream'),
        (r'\bHA\b', 'Hyaluronic Acid'),
        (r'\bAHA\b', 'Alpha Hydroxy Acid'),
        (r'\bBHA\b', 'Beta Hydroxy Acid'),
        (r'\bPHA\b', 'Polyhydroxy Acid'),
        (r'\bNMF\b', 'Natural Moisturizing Factor'),
        (r'\bEGF\b', 'Epidermal Growth Factor'),
        (r'\bVit\s*C\b', 'Vitamin C'),
        (r'\bVit\s*E\b', 'Vitamin E'),
        (r'\bVit\s*B3\b', 'Niacinamide Vitamin B3'),
        (r'\bVit\s*B5\b', 'Panthenol Vitamin B5'),
        (r'\bSOD\b', 'Superoxide Dismutase'),
        (r'\bQ10\b', 'Coenzyme Q10'),
        (r'\bFoam\s*cl\b', 'Foam cleanser'),
        (r'\bMic\s*H2O\b', 'Micellar Water'),
        (r'\bToner\b', 'Skin toner'),
        (r'\bEssence\b', 'Skin essence'),
        (r'\bAmpoule\b', 'Concentrated serum'),
        (r'\bCF\b', 'Cruelty Free'),
        (r'\bPF\b', 'Paraben Free'),
        (r'\bSF\b', 'Sulfate Free'),
        (r'\bGF\b', 'Gluten Free'),
        (r'\bHF\b', 'Hypoallergenic Formula'),
        (r'\bNT\b', 'Non-comedogenic Tested'),
        (r'\bAM\b', 'morning'),
        (r'\bPM\b', 'night'),
        (r'\bBID\b', 'twice daily'),
        (r'\bQD\b', 'once daily'),
        (r'\bAIR\b', 'Airless pump bottle'),
        (r'\bD-C\b', 'Dropper container'),
        (r'\bT-C\b', 'Tube container'),
        (r'\bPDO\b', 'Polydioxanone'),
        (r'\bPCL\b', 'Polycaprolactone'),
        (r'\bPLLA\b', 'Poly-L-lactic Acid'),
        (r'\bHIFU\b', 'High-Intensity Focused Ultrasound'),
        (r'\b(\d+)\s*fl\s*oz\b', 'fluid ounce'),
        (r'\bpH\s*bal\b', 'pH balanced'),
        # General Abbreviations and Units
        (r'\b(\d+)\s*gb\b', 'byte'),
        (r'\b(\d+)\s*tb\b', 'byte'),
        (r'\b(\d+)\s*mb\b', 'byte'),
        (r'\b(\d+)\s*go\b', 'byte'),
        (r'\b(\d+)\s*to\b', 'byte'),
        (r'\b(\d+)\s*mo\b', 'byte'),
        (r'\boctet\b', 'byte'),
        (r'\b(\d+)\s*y\b', 'year'),
        (r'\b(\d+)\s*mth\b', 'month'),
        (r'\b(\d+)\s*d\b', 'day'),
        (r'\b(\d+)\s*h\b', 'hour'),
        (r'\b(\d+)\s*min\b', 'minute'),
        (r'\b(\d+)\s*rpm\b', 'revolution per minute'),
        (r'\b(\d+)\s*mw\b', 'watt'),
        (r'\b(\d+)\s*cw\b', 'watt'),
        (r'\b(\d+)\s*kw\b', 'watt'),
        (r'\b(\d+)\s*ma\b', 'ampere'),
        (r'\b(\d+)\s*ca\b', 'ampere'),
        (r'\b(\d+)\s*ka\b', 'ampere'),
        (r'\b(\d+)\s*mv\b', 'volt'),
        (r'\b(\d+)\s*cv\b', 'volt'),
        (r'\b(\d+)\s*kv\b', 'volt'),
        (r'\b(\d+)\s*mm\b', 'meter'),
        (r'\b(\d+)\s*cm\b', 'meter'),
        (r'\b(\d+)\s*m\b', 'meter'),
        (r'\b(\d+)\s*km\b', 'meter'),
        (r'\binch\b', 'meter'),
        (r'\b(\d+)\s*ml\b', 'liter'),
        (r'\b(\d+)\s*cl\b', 'liter'),
        (r'\b(\d+)\s*dl\b', 'liter'),
        (r'\b(\d+)\s*l\b', 'liter'),
        (r'\b(\d+)\s*oz\b', 'liter'),
        (r'\b(\d+)\s*gal\b', 'liter'),
        (r'\bounce\b', 'liter'),
        (r'\bgallon\b', 'liter'),
        (r'\b(\d+)\s*mg\b', 'gram'),
        (r'\b(\d+)\s*cg\b', 'gram'),
        (r'\b(\d+)\s*dg\b', 'gram'),
        (r'\b(\d+)\s*g\b', 'gram'),
        (r'\b(\d+)\s*kg\b', 'gram'),
        (r'\b(\d+)\s*lb\b', 'gram'),
        (r'\bpound\b', 'gram'),
        (r'\b(\d+)\s*°c\b', 'celsius'),
        (r'\b(\d+)\s*°f\b', 'celcius'),
        (r'\bfahrenheit\b', 'celcius'),
        (r'\bflipkart\.com\b', ''),
        (r'\bapprox\.?\b', 'approximately'),
        (r'\bw/o\b', 'without'),
        (r'\bw/\b', 'with'),
        (r'\bant-\b', 'anti'),
        (r'\byes\b', ''),
        (r'\bno\b', ''),
        (r'\bna\b', ''),
        (r'\brs\.?\b', ''),
    ]
    for pattern, replacement in all_patterns:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text

def extract_keywords(text, nlp, top_n=15):
    """Extract keywords from text using lemmatization and stopword removal."""
    if pd.isna(text) or text == '':
        return []
    # Clean text before processing
    text = clean_text(text)
    try:
        doc = nlp(text)
    except Exception as e:
        st.error(f"❌ Error processing text with spaCy: {str(e)}")
        st.warning("⚠️ Retrying with CPU-based spaCy model...")
        try:
            nlp_cpu = spacy.load("en_core_web_trf")
            doc = nlp_cpu(text)
        except Exception as e2:
            st.error(f"❌ Failed to process text even on CPU: {str(e2)}")
            return []
    keywords = []
    for token in doc:
        lemma = token.lemma_.lower().strip()
        if (len(lemma) < 2 or token.is_punct or not lemma or token.is_stop or
            token.text.isdigit() or
            re.match(r'^[\d.,]+$', token.text) or
            re.match(r'^[\d.,]+\s*[a-zA-Z%]+$', token.text) or
            re.match(r'^-[0-9]+$', token.text) or
            (re.match(r'^[A-Z0-9]+(?:[-_][A-Z0-9]+)*$', token.text, re.IGNORECASE) and
             (re.search(r'\d', token.text) and re.search(r'[a-zA-Z]', token.text)) or
             re.match(r'^[A-Z0-9]+$', token.text))):
            continue
        keywords.append(lemma)
    keyword_counts = Counter(keywords)
    return [word for word, count in keyword_counts.most_common(top_n)]

st.header("Entrée des Données du Produit")
product_name = st.text_input("Nom du Produit", placeholder="Exemple : Montre pour homme", 
                            help="Saisissez le nom complet du produit", key="product_name_input",
                            label_visibility="visible")
description = st.text_area("Description", placeholder="Exemple : Une montre élégante en cuir noir pour homme",
                          help="Décrivez le produit en détail", key="description_input",
                          label_visibility="visible")
specifications = st.text_area("Spécifications Techniques", placeholder="Exemple : Résistant à l'eau, affichage analogique",
                             help="Listez les spécifications techniques importantes", key="specifications_input",
                             label_visibility="visible")
uploaded_image = st.file_uploader("Télécharger une Image du Produit", type=['jpg', 'png', 'jpeg'],
                                 help="Image du produit à analyser", key="image_uploader",
                                 label_visibility="visible")

# Ajouter des labels ARIA pour l'accessibilité
st.markdown("""
<div role="region" aria-label="Formulaire de prédiction de produit">
""", unsafe_allow_html=True)

if st.button("Prédire", key="predict_button", help="Lancer la prédiction de catégorie", type="primary"):
    if not (uploaded_image and product_name and description and specifications):
        st.error("Veuillez fournir un nom de produit, une description, des spécifications techniques et une image.")
        st.stop()
    
    st.image(uploaded_image, caption="Image Téléchargée", width=200)
    st.caption(f"Image analysée: {product_name}")
    
    # Extract keywords
    combined_text = f"{description} {specifications}"
    combined_text = clean_text(combined_text)
    keywords = extract_keywords(combined_text, nlp)
    if not keywords:
        st.error("Aucun mot-clé extrait. Veuillez fournir une description et des spécifications plus détaillées.")
        st.stop()
    
    st.write(f"**Mots-clés extraits :** {', '.join(keywords)}")
    
    # Prédiction via Azure ML
    with st.spinner("🔄 Prédiction en cours via Azure ML..."):
        image = Image.open(uploaded_image)
        text_description = f"{product_name} {description} {specifications}"
        
        result = azure_client.predict_category(image, text_description)
    
    if result['success']:
        st.header("Résultats de la Prédiction")
        st.write(f"**Mots-clés analysés :** {', '.join(keywords)}")
        st.write(f"**Catégorie prédite :** {result['predicted_category']}")
        st.write(f"**Confiance :** {result['confidence']:.3f}")
        st.write(f"**Source :** {result['source']}")
        
        # Afficher les scores de toutes les catégories
        st.subheader("Scores de Toutes les Catégories")
        category_data = []
        for category, score in result['category_scores'].items():
            category_data.append({"Catégorie": category, "Score": f"{score:.4f}"})
        st.table(category_data)
        
        # Graphique des scores
        st.subheader("Visualisation des Scores")
        
        # Configuration des couleurs selon le mode d'accessibilité
        if st.session_state.accessibility.get('color_blind', False):
            palette = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2']
        elif st.session_state.accessibility.get('high_contrast', False):
            palette = HIGH_CONTRAST_COLORS
        else:
            palette = ACCESSIBLE_COLORS
        
        plt.figure(figsize=(12, 8))
        categories = list(result['category_scores'].keys())
        scores = list(result['category_scores'].values())
        
        bars = plt.barh(categories, scores, color=palette[:len(categories)])
        
        # Ajouter des motifs pour le mode daltonien
        if st.session_state.accessibility.get('color_blind', False):
            patterns = ['/', '\\', '|', '-', '+', 'x', 'o', '.', '*']
            for i, bar in enumerate(bars):
                bar.set_hatch(patterns[i % len(patterns)])
        
        plt.title(f"Scores de Classification - {product_name[:50]}...", 
                  fontsize=16 if not st.session_state.accessibility.get('large_text', False) else 20, 
                  pad=20)
        plt.xlabel("Score de probabilité", fontsize=14 if not st.session_state.accessibility.get('large_text', False) else 18)
        plt.ylabel("Catégories", fontsize=14 if not st.session_state.accessibility.get('large_text', False) else 18)
        plt.gca().invert_yaxis()
        
        # Appliquer les styles d'accessibilité aux graphiques
        if st.session_state.accessibility.get('high_contrast', False):
            plt.gca().set_facecolor('black')
            plt.gcf().set_facecolor('black')
            plt.gca().tick_params(colors='white')
            plt.gca().xaxis.label.set_color('white')
            plt.gca().yaxis.label.set_color('white')
            plt.title(plt.gca().get_title(), color='white')
        
        # Ajouter les valeurs sur les barres
        for i, (category, score) in enumerate(zip(categories, scores)):
            plt.text(score + 0.01, i, f'{score:.3f}', va='center', ha='left', 
                    fontsize=12 if not st.session_state.accessibility.get('large_text', False) else 16)
        
        plt.grid(axis='x', alpha=0.3)
        plt.tight_layout()
        st.pyplot(plt, use_container_width=True)
        
    else:
        st.error(f"❌ Erreur lors de la prédiction: {result['error']}")
        st.info("💡 Vérifiez la configuration de l'API Azure ML ou utilisez le mode local.")

st.markdown("</div>", unsafe_allow_html=True)
