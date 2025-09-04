"""
Script de scoring pour Azure ML - API d'inférence pour le modèle CLIP
"""

import os
import json
import torch
import numpy as np
from PIL import Image
import io
import base64
from transformers import CLIPModel, CLIPProcessor, CLIPTokenizer
from sklearn.preprocessing import LabelEncoder
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
MODEL_NAME = 'openai/clip-vit-base-patch32'
CATEGORIES = [
    'Baby Care',
    'Beauty and Personal Care', 
    'Computers',
    'Home Decor & Festive Needs',
    'Home Furnishing',
    'Kitchen & Dining',
    'Watches'
]

class CLIPForClassification(torch.nn.Module):
    """Modèle CLIP pour classification"""
    def __init__(self, num_labels):
        super().__init__()
        self.clip = CLIPModel.from_pretrained(MODEL_NAME)
        self.classifier = torch.nn.Linear(self.clip.config.projection_dim * 2, num_labels)
        
    def forward(self, pixel_values, input_ids, attention_mask, labels=None):
        outputs = self.clip(pixel_values=pixel_values, input_ids=input_ids, attention_mask=attention_mask)
        pooled_output = torch.cat((outputs.image_embeds, outputs.text_embeds), dim=-1)
        logits = self.classifier(pooled_output)
        return logits

def init():
    """Initialisation du modèle et des composants"""
    global model, processor, tokenizer, label_encoder, device
    
    try:
        # Configuration du device
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Utilisation du device: {device}")
        
        # Créer le label encoder
        label_encoder = LabelEncoder()
        label_encoder.fit(CATEGORIES)
        
        # Charger le modèle
        model = CLIPForClassification(num_labels=len(CATEGORIES)).to(device)
        
        # Charger les poids fine-tunés si disponibles
        model_path = os.path.join(os.getenv('AZUREML_MODEL_DIR', '.'), 'clip_product_classifier.pth')
        if os.path.exists(model_path):
            state_dict = torch.load(model_path, map_location=device)
            model.load_state_dict(state_dict, strict=False)
            logger.info(f"Modèle fine-tuné chargé depuis {model_path}")
        else:
            logger.warning(f"Fichier de modèle non trouvé: {model_path}. Utilisation du modèle pré-entraîné.")
        
        # Charger le processeur et tokenizer
        processor = CLIPProcessor.from_pretrained(MODEL_NAME)
        tokenizer = CLIPTokenizer.from_pretrained(MODEL_NAME)
        
        model.eval()
        logger.info("Modèle initialisé avec succès")
        
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation: {str(e)}")
        raise

def run(raw_data):
    """Fonction principale de scoring"""
    try:
        # Parser les données d'entrée
        data = json.loads(raw_data)
        
        # Extraire les données
        image_base64 = data.get('image')
        text_description = data.get('text', '')
        
        if not image_base64:
            return {"error": "Aucune image fournie"}
        
        # Décoder l'image
        try:
            image_data = base64.b64decode(image_base64)
            image = Image.open(io.BytesIO(image_data))
            if image.mode != 'RGB':
                image = image.convert('RGB')
        except Exception as e:
            return {"error": f"Erreur lors du décodage de l'image: {str(e)}"}
        
        # Traiter l'image et le texte
        image_inputs = processor(images=image, return_tensors="pt").pixel_values.to(device)
        text_inputs = tokenizer(
            text_description,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=77
        ).to(device)
        
        # Prédiction
        with torch.no_grad():
            logits = model(
                pixel_values=image_inputs,
                input_ids=text_inputs['input_ids'],
                attention_mask=text_inputs['attention_mask']
            )
            
            # Obtenir les probabilités
            probabilities = torch.softmax(logits, dim=-1)
            predicted_label = torch.argmax(logits, dim=1).item()
            predicted_category = label_encoder.inverse_transform([predicted_label])[0]
            
            # Calculer les scores pour toutes les catégories
            category_scores = {}
            for i, category in enumerate(CATEGORIES):
                category_scores[category] = float(probabilities[0][i])
        
        # Retourner les résultats
        result = {
            "predicted_category": predicted_category,
            "confidence": float(probabilities[0][predicted_label]),
            "category_scores": category_scores,
            "status": "success"
        }
        
        logger.info(f"Prédiction réussie: {predicted_category} (confiance: {result['confidence']:.3f})")
        return result
        
    except Exception as e:
        logger.error(f"Erreur lors du scoring: {str(e)}")
        return {"error": str(e), "status": "error"}

if __name__ == "__main__":
    # Test local
    init()
    
    # Test avec une image d'exemple
    test_data = {
        "image": "",  # Base64 encoded image
        "text": "Une montre élégante pour homme"
    }
    
    result = run(json.dumps(test_data))
    print(json.dumps(result, indent=2))
