#!/usr/bin/env python3
"""
Script pour analyser les différences entre le notebook d'entraînement et l'application cloud
"""

import pandas as pd
import numpy as np
import re
from collections import Counter
import os

def analyze_notebook_vs_cloud():
    """Analyser les différences entre le notebook et l'application cloud"""
    
    print("🔍 ANALYSE DES DIFFÉRENCES NOTEBOOK vs CLOUD")
    print("=" * 50)
    
    # 1. Différences dans l'extraction des mots-clés
    print("\n📝 1. EXTRACTION DES MOTS-CLÉS")
    print("-" * 30)
    
    # Logique du notebook (simplifiée)
    def notebook_extract_keywords(text, nlp, top_n=15):
        """Logique d'extraction du notebook"""
        if not text:
            return []
        doc = nlp(text)
        keywords = []
        for token in doc:
            lemma = token.lemma_.lower().strip()
            if (len(lemma) < 2 or
                token.is_punct or
                not lemma or
                token.is_stop or
                re.match(r'.*[@*/±&%#].*', lemma)):
                continue
            keywords.append(lemma)
        keyword_counts = Counter(keywords)
        return [word for word, count in keyword_counts.most_common(top_n)]
    
    # Logique de l'application cloud (simplifiée)
    def cloud_extract_keywords(text, nlp, top_n=15):
        """Logique d'extraction de l'application cloud"""
        if pd.isna(text) or text == '':
            return []
        
        # Nettoyage du texte (identique)
        text = clean_text(text)
        
        # Si spaCy n'est pas disponible, utiliser le fallback
        if nlp is None:
            return extract_keywords_fallback(text, top_n)
        
        try:
            doc = nlp(text)
        except Exception as e:
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
    
    def extract_keywords_fallback(text, top_n=15):
        """Fallback sans spaCy"""
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
        
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        words = text.split()
        keywords = [word for word in words if len(word) > 2 and word not in stopwords]
        word_counts = Counter(keywords)
        return [word for word, count in word_counts.most_common(top_n)]
    
    def clean_text(text):
        """Nettoyage du texte (identique dans les deux versions)"""
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
    
    # Test avec un exemple de texte
    test_text = "Escort E-1700-906_Blk Analog Watch - For Men, Boys. Stainless steel case, water resistant, quartz movement, luminous hands"
    
    print(f"Texte de test: {test_text}")
    print(f"Texte nettoyé: {clean_text(test_text)}")
    
    # Simuler l'extraction sans spaCy (mode cloud)
    cloud_keywords = extract_keywords_fallback(clean_text(test_text))
    print(f"Mots-clés cloud (fallback): {cloud_keywords}")
    
    # 2. Différences dans la génération des heatmaps
    print("\n🔥 2. GÉNÉRATION DES HEATMAPS")
    print("-" * 30)
    
    print("NOTEBOOK:")
    print("- Utilise le modèle CLIP fine-tuné réel")
    print("- Calcule les vraies similarités entre patches d'image et mots-clés")
    print("- Génère des heatmaps d'attention basées sur les caractéristiques CLIP")
    print("- Utilise griddata pour lisser les heatmaps")
    print("- Superpose la heatmap sur l'image originale")
    
    print("\nAPPLICATION CLOUD:")
    print("- Utilise des heatmaps simulées (mode démonstration)")
    print("- Génère des patterns d'attention basés sur des règles simples")
    print("- Pour les montres: attention concentrée sur le centre")
    print("- Pour les ordinateurs: attention sur les bords")
    print("- Pour les autres: attention aléatoire avec quelques zones d'intérêt")
    
    # 3. Différences dans la prédiction
    print("\n🎯 3. LOGIQUE DE PRÉDICTION")
    print("-" * 30)
    
    print("NOTEBOOK:")
    print("- Utilise le modèle CLIP fine-tuné avec classification head")
    print("- Prédiction basée sur les caractéristiques multimodales (image + texte)")
    print("- Scores de confiance basés sur les logits du modèle")
    
    print("\nAPPLICATION CLOUD (mode démo):")
    print("- Utilise des règles basées sur les mots-clés")
    print("- Score basé sur le nombre de mots-clés correspondants")
    print("- Bonus pour les mots-clés spécifiques")
    print("- Confiance améliorée si plusieurs mots-clés correspondent")
    
    # 4. Recommandations pour aligner les résultats
    print("\n💡 4. RECOMMANDATIONS POUR ALIGNER LES RÉSULTATS")
    print("-" * 50)
    
    print("1. EXTRACTION DES MOTS-CLÉS:")
    print("   - Utiliser la même logique de nettoyage du texte")
    print("   - Implémenter le même fallback sans spaCy")
    print("   - Appliquer les mêmes filtres de mots-clés")
    
    print("\n2. GÉNÉRATION DES HEATMAPS:")
    print("   - Déployer le modèle CLIP fine-tuné sur Azure ML")
    print("   - Implémenter la vraie logique d'attention CLIP")
    print("   - Utiliser les mêmes paramètres de griddata")
    
    print("\n3. PRÉDICTION:")
    print("   - Utiliser le modèle fine-tuné au lieu des règles")
    print("   - Implémenter la même logique de classification")
    print("   - Calculer les vrais scores de confiance")
    
    print("\n4. DÉPLOIEMENT:")
    print("   - Créer un endpoint Azure ML avec le modèle fine-tuné")
    print("   - Implémenter la logique d'attention dans le script de score")
    print("   - Tester avec les mêmes données d'entraînement")
    
    return {
        'keyword_differences': {
            'notebook': 'Utilise spaCy avec lemmatisation',
            'cloud': 'Utilise fallback simple sans spaCy'
        },
        'heatmap_differences': {
            'notebook': 'Vraies heatmaps CLIP avec attention',
            'cloud': 'Heatmaps simulées basées sur des règles'
        },
        'prediction_differences': {
            'notebook': 'Modèle CLIP fine-tuné avec classification',
            'cloud': 'Règles basées sur les mots-clés'
        }
    }

if __name__ == "__main__":
    results = analyze_notebook_vs_cloud()
    print("\n✅ Analyse terminée!")
