"""
Page de prédiction pour la version cloud avec Azure ML
"""

import os
import pandas as pd
import streamlit as st
try:
    import spacy
except ImportError:
    spacy = None
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
try:
    import seaborn as sns
except ImportError:
    sns = None
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

st.title("🔮 Prédiction de Catégorie")

# Configuration d'accessibilité
ACCESSIBLE_COLORS = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
HIGH_CONTRAST_COLORS = ['#FFFFFF', '#FF0000', '#00FF00', '#0000FF', '#FFFF00']

# Obtenir le client Azure ML
azure_client = get_azure_client()

# Afficher les options d'accessibilité dans la sidebar
render_accessibility_sidebar()

# Appliquer les styles d'accessibilité
apply_accessibility_styles()

# spaCy will be handled by Azure ML API, not locally
nlp = None
st.info("🔄 spaCy processing will be handled by Azure ML API")

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

def extract_keywords_fallback(text, top_n=15):
    """Fallback keyword extraction without spaCy."""
    import re
    from collections import Counter
    
    # Simple stopwords list
    stopwords = {
        'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
        'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
        'to', 'was', 'will', 'with', 'this', 'these', 'they', 'them',
        'their', 'there', 'then', 'than', 'or', 'but', 'if', 'when',
        'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few',
        'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
        'only', 'own', 'same', 'so', 'than', 'too', 'very', 'can',
        'could', 'should', 'would', 'may', 'might', 'must', 'shall'
    }
    
    # Clean and tokenize text
    text = re.sub(r'[^\w\s]', ' ', text.lower())
    words = text.split()
    
    # Filter out stopwords and short words
    keywords = [word for word in words if len(word) > 2 and word not in stopwords]
    
    # Count and return top keywords
    word_counts = Counter(keywords)
    return [word for word, count in word_counts.most_common(top_n)]

def extract_keywords(text, nlp, top_n=15):
    """Extract keywords from text using lemmatization and stopword removal."""
    if pd.isna(text) or text == '':
        return []
    # Clean text before processing
    text = clean_text(text)
    
    # If spaCy is not available, use simple text processing
    if nlp is None:
        return extract_keywords_fallback(text, top_n)
    
    try:
        doc = nlp(text)
    except Exception as e:
        st.warning(f"⚠️ Error processing text with spaCy: {str(e)}")
        return extract_keywords_fallback(text, top_n)
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
        
        # Heatmap des scores (simulation)
        st.subheader("Heatmap des Scores de Classification")
        
        # Créer une matrice pour la heatmap
        categories = list(result['category_scores'].keys())
        scores = list(result['category_scores'].values())
        
        # Créer une matrice 1D pour la heatmap
        score_matrix = np.array(scores).reshape(1, -1)
        
        plt.figure(figsize=(12, 4))
        
        # Générer la heatmap
        if sns is not None:
            # Utiliser seaborn si disponible
            sns.heatmap(score_matrix, 
                       xticklabels=categories,
                       yticklabels=['Scores'],
                       annot=True, 
                       fmt='.3f',
                       cmap='RdYlBu_r' if not st.session_state.accessibility.get('color_blind', False) else 'viridis',
                       cbar_kws={'label': 'Score de probabilité'})
        else:
            # Fallback avec matplotlib
            im = plt.imshow(score_matrix, cmap='RdYlBu_r' if not st.session_state.accessibility.get('color_blind', False) else 'viridis', aspect='auto')
            plt.xticks(range(len(categories)), categories, rotation=45, ha='right')
            plt.yticks([0], ['Scores'])
            plt.colorbar(im, label='Score de probabilité')
            
            # Ajouter les annotations
            for i in range(len(categories)):
                plt.text(i, 0, f'{scores[i]:.3f}', ha='center', va='center', 
                        color='white' if scores[i] > 0.5 else 'black', fontweight='bold')
        
        plt.title(f"Heatmap des Scores - {product_name[:50]}...", 
                  fontsize=16 if not st.session_state.accessibility.get('large_text', False) else 20, 
                  pad=20)
        plt.tight_layout()
        st.pyplot(plt, use_container_width=True)
        
        # Heatmap d'attention simulée sur l'image (comme dans votre version locale)
        if uploaded_image:
            st.subheader("Interprétabilité Image (Heatmap d'Attention Simulée)")
            
            # Charger l'image
            image = Image.open(uploaded_image)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convertir en niveaux de gris pour l'affichage
            image_gray = image.convert('L')
            image_array = np.array(image_gray)
            
            # Simuler une carte d'attention basée sur la catégorie prédite
            height, width = image_array.shape
            
            # Créer une attention map simulée
            # Pour les montres, concentrer l'attention sur le centre (cadran)
            if result['predicted_category'] == 'Watches':
                # Créer une attention concentrée sur le centre (cadran de montre)
                y, x = np.ogrid[:height, :width]
                center_y, center_x = height // 2, width // 2
                sigma = min(height, width) // 4
                attention_map = np.exp(-((x - center_x)**2 + (y - center_y)**2) / (2 * sigma**2))
            elif result['predicted_category'] == 'Computers':
                # Pour les ordinateurs, attention sur les bords (écran, clavier)
                y, x = np.ogrid[:height, :width]
                attention_map = np.zeros((height, width))
                # Attention sur les bords
                attention_map[0:height//4, :] = 0.8  # Haut
                attention_map[3*height//4:, :] = 0.8  # Bas
                attention_map[:, 0:width//4] = 0.6  # Gauche
                attention_map[:, 3*width//4:] = 0.6  # Droite
            else:
                # Pour les autres catégories, attention uniforme avec quelques zones d'intérêt
                attention_map = np.random.rand(height, width) * 0.3
                # Ajouter quelques zones d'attention
                for _ in range(3):
                    center_y = np.random.randint(height//4, 3*height//4)
                    center_x = np.random.randint(width//4, 3*width//4)
                    sigma = min(height, width) // 8
                    y, x = np.ogrid[:height, :width]
                    attention_map += 0.4 * np.exp(-((x - center_x)**2 + (y - center_y)**2) / (2 * sigma**2))
                attention_map = np.clip(attention_map, 0, 1)
            
            # Normaliser l'attention map
            attention_map = (attention_map - attention_map.min()) / (attention_map.max() - attention_map.min() + 1e-8)
            
            # Créer la visualisation comme dans votre version locale
            aspect_ratio = width / height
            base_size = 0.8
            if aspect_ratio > 1:
                fig_width = base_size * aspect_ratio
                fig_height = base_size
            else:
                fig_width = base_size
                fig_height = base_size / aspect_ratio
                
            fig, ax = plt.subplots(figsize=(fig_width, fig_height))
            
            # Afficher l'image en niveaux de gris
            ax.imshow(image_array, cmap='gray', aspect='equal')
            
            # Choisir la palette en fonction du mode d'accessibilité
            if st.session_state.accessibility.get('color_blind', False):
                cmap = 'viridis'
            elif st.session_state.accessibility.get('high_contrast', False):
                cmap = 'hot'
            else:
                cmap = 'plasma'
                
            # Superposer la heatmap d'attention
            im = ax.imshow(attention_map, cmap=cmap, alpha=0.5, aspect='equal')
            ax.set_title("Heatmap d'Attention Simulée", fontsize=4)
            ax.axis('off')
            
            # Appliquer les styles d'accessibilité
            text_color = 'white' if st.session_state.accessibility.get('high_contrast', False) else 'black'
            if st.session_state.accessibility.get('high_contrast', False):
                ax.set_facecolor('black')
                fig.set_facecolor('black')
                ax.title.set_color('white')
            
            # Ajouter une barre de couleur
            cbar = plt.colorbar(im, ax=ax, shrink=0.4, aspect=30)
            cbar.set_label('Intensité d\'attention', 
                           fontsize=3,
                           color=text_color)
            cbar.ax.yaxis.set_tick_params(color=text_color, labelsize=2)
            plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color=text_color, fontsize=2)
            
            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)
            
            # Description textuelle pour les non-voyants
            st.write("**Description de l'analyse d'attention :**")
            max_attention = np.max(attention_map)
            min_attention = np.min(attention_map)
            st.write(f"""
            - La heatmap superposée montre les zones de l'image où le modèle se concentre pour faire sa prédiction
            - Intensité d'attention maximale: {max_attention:.3f}
            - Intensité d'attention minimale: {min_attention:.3f}
            - Les zones les plus claires indiquent une attention plus forte
            - **Note:** Cette heatmap est simulée pour le mode démonstration. En mode production avec Azure ML, vous obtiendriez la vraie analyse d'attention CLIP.
            """)
        
    else:
        st.error(f"❌ Erreur lors de la prédiction: {result['error']}")
        st.info("💡 Vérifiez la configuration de l'API Azure ML ou utilisez le mode local.")

st.markdown("</div>", unsafe_allow_html=True)
