import os
import json
import torch
import numpy as np
from PIL import Image
import io
import base64
from transformers import CLIPModel, CLIPTokenizer, CLIPProcessor
import pandas as pd
from sklearn.preprocessing import LabelEncoder
import logging
from scipy.interpolate import griddata
import re
from collections import Counter

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CLIPClassifierFinetuned:
    def __init__(self):
        """Initialiser le classificateur CLIP fine-tuné"""
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Utilisation du device: {self.device}")
        
        # Charger le modèle CLIP de base
        self.model_name = "openai/clip-vit-base-patch32"
        self.clip_model = CLIPModel.from_pretrained(self.model_name).to(self.device)
        self.tokenizer = CLIPTokenizer.from_pretrained(self.model_name)
        self.processor = CLIPProcessor.from_pretrained(self.model_name)
        
        # Charger le modèle fine-tuné
        self.load_finetuned_model()
        
        # Catégories disponibles
        self.categories = [
            'Baby Care', 'Beauty and Personal Care', 'Computers',
            'Home Decor & Festive Needs', 'Home Furnishing',
            'Kitchen & Dining', 'Watches'
        ]
        
        # Encoder pour les catégories
        self.label_encoder = LabelEncoder()
        self.label_encoder.fit(self.categories)
        
        logger.info("✅ Modèle CLIP fine-tuné chargé avec succès")
    
    def load_finetuned_model(self):
        """Charger le modèle fine-tuné"""
        try:
            # Chemin vers le modèle fine-tuné
            model_path = "/var/azureml-app/new_clip_product_classifier.pth"
            
            if os.path.exists(model_path):
                # Charger le state_dict du modèle fine-tuné
                state_dict = torch.load(model_path, map_location=self.device)
                
                # Créer le modèle avec la classification head
                from torch import nn
                
                class CLIPForClassification(nn.Module):
                    def __init__(self, config, num_labels):
                        super().__init__()
                        self.clip = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
                        self.classifier = nn.Linear(config.projection_dim * 2, num_labels)
                        self.loss_fn = nn.CrossEntropyLoss()
                    
                    def forward(self, pixel_values, input_ids, attention_mask, labels=None):
                        outputs = self.clip(pixel_values=pixel_values, input_ids=input_ids, attention_mask=attention_mask)
                        pooled_output = torch.cat((outputs.image_embeds, outputs.text_embeds), dim=-1)
                        logits = self.classifier(pooled_output)
                        
                        loss = None
                        if labels is not None:
                            loss = self.loss_fn(logits, labels)
                        
                        return type('Output', (), {
                            'loss': loss,
                            'logits': logits,
                            'image_embeds': outputs.image_embeds,
                            'text_embeds': outputs.text_embeds
                        })()
                
                # Créer le modèle avec classification head
                config = self.clip_model.config
                self.model = CLIPForClassification(config, num_labels=len(self.categories)).to(self.device)
                
                # Charger les poids fine-tunés
                self.model.load_state_dict(state_dict)
                self.model.eval()
                
                logger.info("✅ Modèle fine-tuné chargé avec succès")
            else:
                logger.warning("⚠️ Modèle fine-tuné non trouvé, utilisation du modèle de base")
                self.model = self.clip_model
                
        except Exception as e:
            logger.error(f"❌ Erreur lors du chargement du modèle fine-tuné: {str(e)}")
            self.model = self.clip_model
    
    def clean_text(self, text):
        """Nettoyer le texte comme dans le notebook"""
        if not isinstance(text, str):
            return ""
        text = text.lower()
        all_patterns = [
            # Transformation des motifs comme iphone4s en iphone s
            (r'([a-zA-Z]+)(\d+)([a-zA-Z])', r'\1 \3'),
            # Abréviations d'indice solaire
            (r'\bpa\+{1,3}\b', 'sun protection factor'),
            # Symboles indésirables
            (r'[@*/±&%#]', ' '),  # Supprime @, *, /, ±, &, %, #
            # Codes alphanumériques non pertinents (ex. ms004pktbl, r&m0179)
            (r'\b[A-Z0-9]+[-_][A-Z0-9]+\b', ' '),
            # Nombres seuls
            (r'\b\d+\b', ' '),
            # Ponctuation spécifique
            (r'\(', ' ( '),
            (r'\)', ' ) '),
            (r'\.', ' . '),
            (r'\!', ' ! '),
            (r'\?', ' ? '),
            (r'\:', ' : '),
            (r'\,', ', '),
            # Motifs spécifiques du domaine
            (r'\b(\d+)\s*[-~to]?\s*(\d+)\s*(m|mth|mths|month|months?)\b', 'month'),
            (r'\bnewborn\s*[-~to]?\s*(\d+)\s*(m|mth|months?)\b', 'month'),
            (r'\b(nb|newborn|baby|bb|bby|babie|babies)\b', 'baby'),
            (r'\b(diaper|diapr|nappy)\b', 'diaper'),
            (r'\b(stroller|pram|buggy)\b', 'stroller'),
            (r'\b(bpa\s*free|non\s*bpa)\b', 'bisphenol a free'),
            (r'\b(\d+)\s*(oz|ounce)\b', 'ounce'),
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
            (r'\bfridge\b', 'refrigerator'),
            (r'\bwashing\s*machine\b', 'clothes washer'),
            (r'\bdishwasher\b', 'dish washing machine'),
            (r'\boven\b', 'cooking oven'),
            (r'\bmicrowave\b', 'microwave oven'),
            (r'\bhoover\b', 'vacuum cleaner'),
            (r'\btumble\s*dryer\b', 'clothes dryer'),
            (r'\b(a\+\++)\b', 'energy efficiency class'),
            (r'\b(\d+)\s*btu\b', 'british thermal unit'),
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
            (r'\bSPF\b', 'sun protection factor'),
            (r'\bUV\b', 'ultraviolet'),
            (r'\bBB\s*cream\b', 'blemish balm cream'),
            (r'\bCC\s*cream\b', 'color correcting cream'),
            (r'\bHA\b', 'hyaluronic acid'),
            (r'\bAHA\b', 'alpha hydroxy acid'),
            (r'\bBHA\b', 'beta hydroxy acid'),
            (r'\bPHA\b', 'polyhydroxy acid'),
            (r'\bNMF\b', 'natural moisturizing factor'),
            (r'\bEGF\b', 'epidermal growth factor'),
            (r'\bVit\s*C\b', 'vitamin c'),
            (r'\bVit\s*E\b', 'vitamin e'),
            (r'\bVit\s*B3\b', 'niacinamide vitamin b3'),
            (r'\bVit\s*B5\b', 'panthenol vitamin b5'),
            (r'\bSOD\b', 'superoxide dismutase'),
            (r'\bQ10\b', 'coenzyme q10'),
            (r'\bFoam\s*cl\b', 'foam cleanser'),
            (r'\bMic\s*H2O\b', 'micellar water'),
            (r'\bToner\b', 'skin toner'),
            (r'\bEssence\b', 'skin essence'),
            (r'\bAmpoule\b', 'concentrated serum'),
            (r'\bCF\b', 'cruelty free'),
            (r'\bPF\b', 'paraben free'),
            (r'\bSF\b', 'sulfate free'),
            (r'\bGF\b', 'gluten free'),
            (r'\bHF\b', 'hypoallergenic formula'),
            (r'\bNT\b', 'non-comedogenic tested'),
            (r'\bAM\b', 'morning'),
            (r'\bPM\b', 'night'),
            (r'\bBID\b', 'twice daily'),
            (r'\bQD\b', 'once daily'),
            (r'\bAIR\b', 'airless pump bottle'),
            (r'\bD-C\b', 'dropper container'),
            (r'\bT-C\b', 'tube container'),
            (r'\bPDO\b', 'polydioxanone'),
            (r'\bPCL\b', 'polycaprolactone'),
            (r'\bPLLA\b', 'poly-l-lactic acid'),
            (r'\bHIFU\b', 'high-intensity focused ultrasound'),
            (r'\b(\d+)\s*fl\s*oz\b', 'fluid ounce'),
            (r'\bpH\s*bal\b', 'ph balanced'),
            (r'\b(\d+)\s*(gb|tb|mb|go|to|mo)\b', 'byte'),
            (r'\boctet\b', 'byte'),
            (r'\b(\d+)\s*y\b', 'year'),
            (r'\b(\d+)\s*mth\b', 'month'),
            (r'\b(\d+)\s*d\b', 'day'),
            (r'\b(\d+)\s*h\b', 'hour'),
            (r'\b(\d+)\s*min\b', 'minute'),
            (r'\b(\d+)\s*rpm\b', 'revolution per minute'),
            (r'\b(\d+)\s*(mw|cw|kw)\b', 'watt'),
            (r'\b(\d+)\s*(ma|ca|ka)\b', 'ampere'),
            (r'\b(\d+)\s*(mv|cv|kv)\b', 'volt'),
            (r'\b(\d+)\s*(mm|cm|m|km)\b', 'meter'),
            (r'\binch\b', 'meter'),
            (r'\b(\d+)\s*(ml|cl|dl|l|oz|gal)\b', 'liter'),
            (r'\b(gallon|ounce)\b', 'liter'),
            (r'\b(\d+)\s*(mg|cg|dg|g|kg|lb)\b', 'gram'),
            (r'\bpound\b', 'gram'),
            (r'\b(\d+)\s*(°c|°f)\b', 'celsius'),
            (r'\bfahrenheit\b', 'celsius'),
            (r'\bflipkart\.com\b', ''),
            (r'\bapprox\.?\b', 'approximately'),
            (r'\bw/o\b', 'without'),
            (r'\bw/\b', 'with'),
            (r'\bant-\b', 'anti'),
            (r'\byes\b', ''),
            (r'\bno\b', ''),
            (r'\bna\b', ''),
            (r'\brs\.?\b', ''),
            # Normaliser les espaces
            (r'\s+', ' '),
        ]
        # Apply patterns twice to ensure complete replacement
        for _ in range(2):
            for pattern, replacement in all_patterns:
                text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        return text.strip()
    
    def extract_keywords(self, text, top_n=15):
        """Extraire les mots-clés comme dans le notebook"""
        if not text:
            return []
        
        # Nettoyer le texte
        text = self.clean_text(text)
        
        # Simple keyword extraction without spaCy
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
    
    def predict_category(self, image, text_description):
        """Prédire la catégorie d'un produit"""
        try:
            # Extraire les mots-clés
            keywords = self.extract_keywords(text_description)
            keywords_text = ", ".join(keywords)
            
            # Prétraiter l'image
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Redimensionner l'image si nécessaire
            max_size = 224
            if max(image.size) > max_size:
                ratio = max_size / max(image.size)
                new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
                image = image.resize(new_size, Image.LANCZOS)
            
            # Prétraiter les entrées
            image_inputs = self.processor(images=image, return_tensors="pt").to(self.device)
            text_inputs = self.tokenizer(keywords_text, return_tensors="pt", padding=True, truncation=True, max_length=77).to(self.device)
            
            # Prédiction
            with torch.no_grad():
                if hasattr(self.model, 'classifier'):
                    # Modèle fine-tuné avec classification head
                    outputs = self.model(
                        pixel_values=image_inputs.pixel_values,
                        input_ids=text_inputs.input_ids,
                        attention_mask=text_inputs.attention_mask
                    )
                    logits = outputs.logits
                else:
                    # Modèle de base CLIP
                    outputs = self.model(
                        pixel_values=image_inputs.pixel_values,
                        input_ids=text_inputs.input_ids,
                        attention_mask=text_inputs.attention_mask
                    )
                    # Calculer les similarités avec les catégories
                    image_features = outputs.image_embeds
                    text_features = outputs.text_embeds
                    
                    # Créer des embeddings pour chaque catégorie
                    category_embeddings = []
                    for category in self.categories:
                        cat_inputs = self.tokenizer(category, return_tensors="pt", padding=True, truncation=True, max_length=77).to(self.device)
                        cat_outputs = self.model.get_text_features(**cat_inputs)
                        category_embeddings.append(cat_outputs)
                    
                    category_embeddings = torch.cat(category_embeddings, dim=0)
                    
                    # Calculer les similarités
                    image_features = image_features / image_features.norm(dim=-1, keepdim=True)
                    category_embeddings = category_embeddings / category_embeddings.norm(dim=-1, keepdim=True)
                    
                    logits = (image_features @ category_embeddings.T) / 0.07
                
                # Appliquer softmax pour obtenir les probabilités
                probs = torch.softmax(logits, dim=-1).cpu().numpy()[0]
                
                # Obtenir la prédiction
                predicted_idx = np.argmax(probs)
                predicted_category = self.categories[predicted_idx]
                confidence = probs[predicted_idx]
                
                # Créer les scores de catégories
                category_scores = {category: float(prob) for category, prob in zip(self.categories, probs)}
                
                return {
                    'predicted_category': predicted_category,
                    'confidence': float(confidence),
                    'category_scores': category_scores,
                    'keywords': keywords
                }
                
        except Exception as e:
            logger.error(f"❌ Erreur lors de la prédiction: {str(e)}")
            raise e
    
    def generate_attention_heatmap(self, image, text_description, resolution=50):
        """Générer une heatmap d'attention comme dans le notebook"""
        try:
            # Extraire les mots-clés
            keywords = self.extract_keywords(text_description)
            
            if not keywords:
                return None
            
            # Prétraiter l'image
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            img_width, img_height = image.size
            
            # Créer une grille de positions
            x = np.linspace(0, img_width, resolution, dtype=int)
            y = np.linspace(0, img_height, resolution, dtype=int)
            xx, yy = np.meshgrid(x, y)
            
            # Traiter les patches par batch
            batch_size = 10
            patch_features = []
            positions = []
            patch_size = min(img_width, img_height) // 10
            
            for i in range(0, resolution * resolution, batch_size):
                batch_patches = []
                batch_positions = []
                
                for j in range(i, min(i + batch_size, resolution * resolution)):
                    x_idx = j // resolution
                    y_idx = j % resolution
                    x_pos = xx[x_idx, y_idx]
                    y_pos = yy[x_idx, y_idx]
                    
                    patch = image.crop((
                        max(0, x_pos - patch_size//2), 
                        max(0, y_pos - patch_size//2),
                        min(img_width, x_pos + patch_size//2), 
                        min(img_height, y_pos + patch_size//2)
                    ))
                    
                    if patch.size[0] > 0 and patch.size[1] > 0:
                        patch = patch.convert('RGB')
                        patch = patch.resize((224, 224), Image.LANCZOS)
                        batch_patches.append(patch)
                        batch_positions.append((x_pos, y_pos))
                
                if batch_patches:
                    with torch.no_grad():
                        inputs = self.processor(images=batch_patches, return_tensors="pt").pixel_values.to(self.device)
                        features = self.model.get_image_features(pixel_values=inputs)
                        patch_features.append(features)
                    positions.extend(batch_positions)
            
            if not patch_features:
                return None
            
            patch_features = torch.cat(patch_features)
            patch_features = patch_features / patch_features.norm(dim=-1, keepdim=True)
            
            # Calculer les similarités avec les mots-clés
            with torch.no_grad():
                text_inputs = self.tokenizer(keywords, return_tensors="pt", padding=True, truncation=True, max_length=77).to(self.device)
                text_features = self.model.get_text_features(**text_inputs)
                text_features = text_features / text_features.norm(dim=-1, keepdim=True)
                attention_scores = (patch_features @ text_features.T).cpu().numpy()
            
            # Créer la heatmap lissée
            points = np.array(positions)
            grid_x, grid_y = np.meshgrid(
                np.linspace(0, img_width, img_width), 
                np.linspace(0, img_height, img_height)
            )
            
            smooth_heatmap = griddata(
                points, 
                attention_scores.mean(axis=1), 
                (grid_x, grid_y), 
                method='cubic', 
                fill_value=0
            )
            
            # Normaliser la heatmap
            smooth_heatmap = (smooth_heatmap - smooth_heatmap.min()) / (smooth_heatmap.max() - smooth_heatmap.min() + 1e-8)
            
            return {
                'heatmap': smooth_heatmap,
                'attention_scores': attention_scores,
                'keywords': keywords,
                'positions': positions
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la génération de la heatmap: {str(e)}")
            return None

# Instance globale du classificateur
classifier = None

def init():
    """Initialiser le modèle"""
    global classifier
    classifier = CLIPClassifierFinetuned()

def run(raw_data):
    """Fonction principale pour l'inférence"""
    try:
        # Parser les données d'entrée
        data = json.loads(raw_data)
        
        # Décoder l'image
        image_base64 = data.get('image', '')
        if not image_base64:
            return json.dumps({
                'status': 'error',
                'error': 'Image manquante'
            })
        
        image_bytes = base64.b64decode(image_base64)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Obtenir la description textuelle
        text_description = data.get('text', '')
        if not text_description:
            return json.dumps({
                'status': 'error',
                'error': 'Description textuelle manquante'
            })
        
        # Prédiction
        result = classifier.predict_category(image, text_description)
        
        # Générer la heatmap d'attention
        heatmap_result = classifier.generate_attention_heatmap(image, text_description)
        
        # Préparer la réponse
        response = {
            'status': 'success',
            'predicted_category': result['predicted_category'],
            'confidence': result['confidence'],
            'category_scores': result['category_scores'],
            'keywords': result['keywords']
        }
        
        # Ajouter la heatmap si disponible
        if heatmap_result:
            response['attention_heatmap'] = {
                'heatmap': heatmap_result['heatmap'].tolist(),
                'keywords': heatmap_result['keywords'],
                'attention_scores': heatmap_result['attention_scores'].tolist()
            }
        
        return json.dumps(response)
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'inférence: {str(e)}")
        return json.dumps({
            'status': 'error',
            'error': str(e)
        })
