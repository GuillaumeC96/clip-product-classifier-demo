
import os
import pandas as pd
try:
    import torch
except ImportError:
    torch = None
import streamlit as st
import spacy
from transformers import CLIPModel, CLIPTokenizer, CLIPProcessor
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import re
from scipy.interpolate import griddata

# Importer le module d'accessibilité
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from accessibility import init_accessibility_state, render_accessibility_sidebar, apply_accessibility_styles

# Initialiser l'état d'accessibilité
init_accessibility_state()

# Configuration de page supprimée - gérée par accessibility.py

st.title("Prédiction de Catégorie")

# Configuration d'accessibilité
ACCESSIBLE_COLORS = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
HIGH_CONTRAST_COLORS = ['#FFFFFF', '#FF0000', '#00FF00', '#0000FF', '#FFFF00']

# Load classifier from session state
classifier = st.session_state['classifier']

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

def clip_attention_analysis(classifier, image, keywords):
    """Perform attention analysis and prediction, adapted from notebook."""
    classifier.model.eval()
    try:
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Sauvegarder les proportions originales pour l'affichage
        original_size = image.size  # (width, height)
        
        # Pour le modèle CLIP, on doit redimensionner à 224x224
        image_inputs = classifier.processor(images=image, return_tensors="pt").pixel_values.to(classifier.device)
        
        # Pour l'affichage, garder les proportions originales
        image_pil = image  # Garder l'image originale pour l'affichage
        image_gray = image_pil.convert('L')
        image_array = np.array(image_gray)
    except Exception as e:
        st.error(f"❌ Erreur lors du traitement de l'image: {str(e)}")
        return None
    
    text = ", ".join(keywords)
    text_inputs = classifier.tokenizer(
        text,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=77
    ).to(classifier.device)
    
    with torch.no_grad():
        outputs = classifier.model.clip(
            pixel_values=image_inputs,
            input_ids=text_inputs['input_ids'],
            attention_mask=text_inputs['attention_mask'],
            output_attentions=True,
            return_dict=True
        )
    
    # Predict category
    logits = classifier.model.classifier(torch.cat((outputs.image_embeds, outputs.text_embeds), dim=-1))
    predicted_label = torch.argmax(logits, dim=1).item()
    predicted_category = classifier.label_encoder.inverse_transform([predicted_label])[0]
    
    # Extract image attention for heatmap
    vision_attentions = outputs.vision_model_output.attentions[-1]
    vision_attentions = vision_attentions.mean(dim=1).squeeze(0)
    vision_attentions = vision_attentions[1:, 1:]  # Exclude [CLS]
    patch_attentions = vision_attentions.mean(dim=0)
    grid_size = 7
    attention_map = patch_attentions.reshape(grid_size, grid_size).cpu().numpy()
    
    # Smooth attention map to match original image size
    x, y = np.meshgrid(np.linspace(0, grid_size-1, grid_size), np.linspace(0, grid_size-1, grid_size))
    
    # Utiliser la taille originale de l'image pour le lissage
    target_height, target_width = image_array.shape
    
    # Créer la grille fine avec le bon ordre pour correspondre à l'image
    x_fine, y_fine = np.meshgrid(np.linspace(0, grid_size-1, target_width), np.linspace(0, grid_size-1, target_height))
    
    # Interpoler la carte d'attention
    attention_map_smooth = griddata(
        (x.flatten(), y.flatten()),
        attention_map.flatten(),
        (x_fine, y_fine),
        method='cubic'
    )
    attention_map_smooth = np.clip(attention_map_smooth, 0, None)
    attention_map_smooth = (attention_map_smooth - attention_map_smooth.min()) / (attention_map_smooth.max() - attention_map_smooth.min() + 1e-8)
    
    # Ensure correct orientation by transposing if necessary
    if attention_map_smooth.shape != (target_height, target_width):
        st.error(f"Unexpected attention map shape: {attention_map_smooth.shape}, expected: {(target_height, target_width)}")
        return None
    
    # Extract keyword similarities, mapping tokens to full keywords
    keyword_similarities = {kw: 0.0 for kw in keywords}  # Initialize with input keywords
    tokens = classifier.tokenizer.convert_ids_to_tokens(text_inputs['input_ids'][0])
    cross_attentions = outputs.vision_model_output.attentions[-1]
    cross_attentions = cross_attentions.mean(dim=1).squeeze(0)
    cross_attentions = cross_attentions[1:, :]  # Exclude [CLS]
    attention_mask = text_inputs['attention_mask'][0].cpu().numpy()
    valid_indices = np.where(attention_mask == 1)[0]
    cross_attentions_sum = cross_attentions.sum(dim=0).cpu().numpy()
    
    # Tokenize input keywords to map to their token IDs
    tokenized_keywords = [classifier.tokenizer(kw, add_special_tokens=False)['input_ids'] for kw in keywords]
    keyword_token_map = {kw: tokens for kw, tokens in zip(keywords, tokenized_keywords)}
    
    current_word = ""
    current_keyword = None
    token_buffer = []
    token_indices = []
    
    for i, token in enumerate(tokens):
        if i not in valid_indices:
            continue
        if token in ['[CLS]', '[SEP]', '<pad>', '<|startoftext|>', '<|endoftext|>']:
            continue
        if token == ',' or token == ',</w>':
            continue  # Skip commas
        if token.endswith('</w>'):
            token = token[:-4]  # Remove </w>
        if token.startswith('##'):
            token = token[2:]  # Remove ## prefix
            current_word += token
            token_buffer.append(token)
            token_indices.append(i)
        else:
            if current_word and current_keyword and token_indices:
                # Assign accumulated attention to the matched keyword
                total_attention = sum(cross_attentions_sum[idx] for idx in token_indices if idx < len(cross_attentions_sum))
                keyword_similarities[current_keyword] += total_attention / cross_attentions_sum.sum()
            current_word = token
            token_buffer = [token]
            token_indices = [i]
            current_keyword = None
            # Find matching keyword
            for kw, kw_tokens in keyword_token_map.items():
                kw_token_strings = [classifier.tokenizer.decode([t]).replace('</w>', '').replace('##', '') for t in kw_tokens]
                if current_word in kw_token_strings or current_word == kw.lower():
                    current_keyword = kw
                    break
    
    # Handle the last word
    if current_word and current_keyword and token_indices:
        total_attention = sum(cross_attentions_sum[idx] for idx in token_indices if idx < len(cross_attentions_sum))
        keyword_similarities[current_keyword] += total_attention / cross_attentions_sum.sum()
    
    # Normalize similarities to sum to 1
    total_sim = sum(keyword_similarities.values())
    if total_sim > 0:
        keyword_similarities = {k: v / total_sim for k, v in keyword_similarities.items()}
    
    return {
        'keywords': keywords,
        'predicted_category': predicted_category,
        'attention_map': attention_map_smooth,
        'keyword_similarities': keyword_similarities,
        'image_gray': image_array
    }

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
    
    # Predict and analyze attention
    image = Image.open(uploaded_image)
    results = clip_attention_analysis(classifier, image, keywords)
    
    if results:
        st.header("Résultats de la Prédiction")
        st.write(f"**Mots-clés analysés :** {', '.join(results['keywords'])}")
        st.write(f"**Catégorie prédite :** {results['predicted_category']}")
        
        # Tableau alternatif pour les lecteurs d'écran
        st.write("**Détails des scores de similarité :**")
        similarity_data = []
        for keyword, score in results['keyword_similarities'].items():
            similarity_data.append({"Mot-clé": keyword, "Score": f"{score:.4f}"})
        st.table(similarity_data)
        
        st.subheader("Interprétabilité Texte (Barchart)")
        
        # Configuration des couleurs selon le mode d'accessibilité
        if st.session_state.accessibility.get('color_blind', False):
            # Utiliser des couleurs accessibles pour les daltoniens
            palette = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22']
        elif st.session_state.accessibility.get('high_contrast', False):
            palette = HIGH_CONTRAST_COLORS
        else:
            palette = ACCESSIBLE_COLORS
        
        plt.figure(figsize=(12, 8))
        keywords_list = list(results['keyword_similarities'].keys())
        scores_list = list(results['keyword_similarities'].values())
        
        # Créer un graphique accessible
        bars = plt.barh(keywords_list, scores_list, 
                       color=palette[:len(keywords_list)])
        
        # Ajouter des motifs pour le mode daltonien
        if st.session_state.accessibility.get('color_blind', False):
            patterns = ['/', '\\', '|', '-', '+', 'x', 'o', '.', '*']
            for i, bar in enumerate(bars):
                bar.set_hatch(patterns[i % len(patterns)])
        
        plt.title(f"Scores de Similarité des Mots-Clés - {product_name[:50]}...", 
                  fontsize=16 if not st.session_state.accessibility.get('large_text', False) else 20, 
                  pad=20)
        plt.xlabel("Score de similarité", fontsize=14 if not st.session_state.accessibility.get('large_text', False) else 18)
        plt.ylabel("Mots-clés", fontsize=14 if not st.session_state.accessibility.get('large_text', False) else 18)
        plt.gca().invert_yaxis()  # Inverser pour avoir le plus haut en haut
        
        # Appliquer les styles d'accessibilité aux graphiques
        bg_color = 'black' if st.session_state.accessibility.get('high_contrast', False) else 'white'
        text_color = 'white' if st.session_state.accessibility.get('high_contrast', False) else 'black'
        
        if st.session_state.accessibility.get('high_contrast', False):
            plt.gca().set_facecolor('black')
            plt.gcf().set_facecolor('black')
            plt.gca().tick_params(colors='white')
            plt.gca().xaxis.label.set_color('white')
            plt.gca().yaxis.label.set_color('white')
            plt.title(plt.gca().get_title(), color='white')
        
        # Ajouter les valeurs sur les barres
        for i, (keyword, score) in enumerate(zip(keywords_list, scores_list)):
            plt.text(score + 0.002, i, f'{score:.4f}', va='center', ha='left', 
                    fontsize=12 if not st.session_state.accessibility.get('large_text', False) else 16, 
                    color=text_color)
        
        plt.grid(axis='x', alpha=0.3)
        plt.tight_layout()
        st.pyplot(plt, use_container_width=True)
        
        st.subheader("Interprétabilité Image (Heatmap)")
        
        # Debug shapes to ensure alignment
        st.write(f"Debug: Image shape: {results['image_gray'].shape}, Attention map shape: {results['attention_map'].shape}")
        
        # Créer une heatmap superposée avec les proportions correctes
        # Calculer les proportions basées sur la taille de l'image
        image_height, image_width = results['image_gray'].shape
        aspect_ratio = image_width / image_height
        
        # Définir une taille de base compacte
        base_size = 0.8  # Taille compacte pour une vue optimale
        if aspect_ratio > 1:  # Image plus large que haute
            fig_width = base_size * aspect_ratio
            fig_height = base_size
        else:  # Image plus haute que large
            fig_width = base_size
            fig_height = base_size / aspect_ratio
            
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        
        # Heatmap superposée sur l'image en niveaux de gris
        ax.imshow(results['image_gray'], cmap='gray', aspect='equal')
        
        # Choisir la palette en fonction du mode d'accessibilité
        if st.session_state.accessibility.get('color_blind', False):
            cmap = 'viridis'
        elif st.session_state.accessibility.get('high_contrast', False):
            cmap = 'hot'
        else:
            cmap = 'plasma'
            
        # Utiliser la carte d'attention directement sans transposition
        im = ax.imshow(results['attention_map'], cmap=cmap, alpha=0.5, aspect='equal')  # Superposition avec transparence
        ax.set_title("Heatmap Superposée", fontsize=4)
        ax.axis('off')
        
        # Appliquer les styles d'accessibilité
        if st.session_state.accessibility.get('high_contrast', False):
            ax.set_facecolor('black')
            fig.set_facecolor('black')
            ax.title.set_color('white')
        
        # Ajouter une barre de couleur très compacte
        cbar = plt.colorbar(im, ax=ax, shrink=0.4, aspect=30)
        cbar.set_label('Intensité d\'attention', 
                       fontsize=3,
                       color=text_color)
        cbar.ax.yaxis.set_tick_params(color=text_color, labelsize=2)
        plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color=text_color, fontsize=2)
        
        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)
        
        # Description textuelle pour les non-voyants
        st.write("**Description de l'analyse :**")
        max_attention = np.max(results['attention_map'])
        min_attention = np.min(results['attention_map'])
        st.write(f"""
        - La heatmap superposée montre les zones de l'image où le modèle se concentre pour faire sa prédiction
        - Intensité d'attention maximale: {max_attention:.3f}
        - Intensité d'attention minimale: {min_attention:.3f}
        - Les zones les plus claires indiquent une attention plus forte
        """)

st.markdown("</div>", unsafe_allow_html=True)
