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

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CLIPClassifier:
    def __init__(self):
        """Initialiser le classificateur CLIP"""
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Utilisation du device: {self.device}")
        
        # Charger le modèle CLIP
        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.tokenizer = CLIPTokenizer.from_pretrained("openai/clip-vit-base-patch32")
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        
        # Charger le modèle fine-tuné
        model_path = "new_clip_product_classifier.pth"
        if os.path.exists(model_path):
            checkpoint = torch.load(model_path, map_location=self.device)
            self.model.load_state_dict(checkpoint['model_state_dict'])
            logger.info("Modèle fine-tuné chargé avec succès")
        else:
            logger.warning("Modèle fine-tuné non trouvé, utilisation du modèle de base")
        
        self.model.to(self.device)
        self.model.eval()
        
        # Charger l'encodeur de labels
        self.label_encoder = LabelEncoder()
        self.categories = [
            'Baby Care', 'Beauty and Personal Care', 'Computers',
            'Home Decor & Festive Needs', 'Home Furnishing',
            'Kitchen & Dining', 'Watches'
        ]
        self.label_encoder.fit(self.categories)
        
        logger.info("Classificateur CLIP initialisé avec succès")
    
    def preprocess_image(self, image_data):
        """Préprocesser l'image"""
        try:
            if isinstance(image_data, str):
                # Décoder l'image base64
                image_bytes = base64.b64decode(image_data)
                image = Image.open(io.BytesIO(image_bytes))
            else:
                image = image_data
            
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            return image
        except Exception as e:
            logger.error(f"Erreur lors du préprocessing de l'image: {e}")
            raise
    
    def preprocess_text(self, text):
        """Préprocesser le texte"""
        if not isinstance(text, str):
            return ""
        
        # Nettoyer le texte
        text = text.lower().strip()
        return text
    
    def predict(self, image, text_description):
        """Effectuer la prédiction"""
        try:
            # Préprocesser les entrées
            image = self.preprocess_image(image)
            text = self.preprocess_text(text_description)
            
            # Traiter l'image
            image_inputs = self.processor(images=image, return_tensors="pt").pixel_values.to(self.device)
            
            # Traiter le texte
            text_inputs = self.tokenizer(
                text,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=77
            ).to(self.device)
            
            # Prédiction
            with torch.no_grad():
                outputs = self.model(
                    pixel_values=image_inputs,
                    input_ids=text_inputs['input_ids'],
                    attention_mask=text_inputs['attention_mask']
                )
                
                # Calculer les scores de similarité
                image_embeds = outputs.image_embeds
                text_embeds = outputs.text_embeds
                
                # Normaliser les embeddings
                image_embeds = image_embeds / image_embeds.norm(dim=-1, keepdim=True)
                text_embeds = text_embeds / text_embeds.norm(dim=-1, keepdim=True)
                
                # Calculer la similarité
                similarity = torch.matmul(image_embeds, text_embeds.T)
                
                # Convertir en probabilités
                probabilities = torch.softmax(similarity, dim=-1)
                
                # Obtenir la prédiction
                predicted_idx = torch.argmax(probabilities, dim=-1).item()
                predicted_category = self.label_encoder.inverse_transform([predicted_idx])[0]
                confidence = probabilities[0, predicted_idx].item()
                
                # Calculer les scores pour toutes les catégories
                category_scores = {}
                for i, category in enumerate(self.categories):
                    if i < probabilities.shape[1]:
                        category_scores[category] = probabilities[0, i].item()
                    else:
                        category_scores[category] = 0.0
                
                return {
                    'success': True,
                    'predicted_category': predicted_category,
                    'confidence': confidence,
                    'category_scores': category_scores,
                    'source': 'azure_ml'
                }
                
        except Exception as e:
            logger.error(f"Erreur lors de la prédiction: {e}")
            return {
                'success': False,
                'error': str(e),
                'source': 'azure_ml'
            }

# Instance globale du classificateur
classifier = None

def init():
    """Initialiser le modèle"""
    global classifier
    try:
        classifier = CLIPClassifier()
        logger.info("Modèle initialisé avec succès")
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation: {e}")
        raise

def run(raw_data):
    """Fonction principale pour Azure ML"""
    try:
        # Initialiser le modèle si nécessaire
        if classifier is None:
            init()
        
        # Parser les données d'entrée
        data = json.loads(raw_data)
        
        # Extraire l'image et le texte
        image_data = data.get('image')
        text_description = data.get('text', '')
        
        if not image_data:
            return json.dumps({
                'success': False,
                'error': 'Image manquante',
                'source': 'azure_ml'
            })
        
        # Effectuer la prédiction
        result = classifier.predict(image_data, text_description)
        
        # Retourner le résultat
        return json.dumps(result)
        
    except Exception as e:
        logger.error(f"Erreur dans run(): {e}")
        return json.dumps({
            'success': False,
            'error': str(e),
            'source': 'azure_ml'
        })