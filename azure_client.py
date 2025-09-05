"""
Client Azure ML pour l'inférence du modèle CLIP
"""

import os
import json
import base64
import requests
import streamlit as st
from PIL import Image
import io
from typing import Dict, Any, Optional

class AzureMLClient:
    """Client pour interagir avec l'API Azure ML"""
    
    def __init__(self):
        self.endpoint_url = os.getenv('AZURE_ML_ENDPOINT_URL')
        self.api_key = os.getenv('AZURE_ML_API_KEY')
        self.use_local = os.getenv('USE_LOCAL_MODEL', 'false').lower() == 'true'
        
        if not self.use_local and not self.endpoint_url:
            st.warning("⚠️ AZURE_ML_ENDPOINT_URL non configuré. Utilisation du mode démonstration.")
            self.use_local = True
    
    def encode_image_to_base64(self, image: Image.Image) -> str:
        """Convertir une image PIL en base64"""
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG', quality=85)
        img_bytes = buffer.getvalue()
        return base64.b64encode(img_bytes).decode('utf-8')
    
    def predict_category(self, image: Image.Image, text_description: str) -> Dict[str, Any]:
        """
        Prédire la catégorie d'un produit
        
        Args:
            image: Image PIL du produit
            text_description: Description textuelle du produit
            
        Returns:
            Dict contenant les résultats de prédiction
        """
        if self.use_local:
            return self._predict_local(image, text_description)
        else:
            return self._predict_azure(image, text_description)
    
    def _predict_azure(self, image: Image.Image, text_description: str) -> Dict[str, Any]:
        """Prédiction via l'API Azure ML"""
        try:
            # Encoder l'image
            image_base64 = self.encode_image_to_base64(image)
            
            # Préparer les données
            data = {
                "image": image_base64,
                "text": text_description
            }
            
            # Headers pour l'authentification
            headers = {
                'Content-Type': 'application/json'
            }
            
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
            
            # Appel à l'API
            response = requests.post(
                self.endpoint_url,
                data=json.dumps(data),
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    return {
                        'success': True,
                        'predicted_category': result['predicted_category'],
                        'confidence': result['confidence'],
                        'category_scores': result['category_scores'],
                        'source': 'azure_ml'
                    }
                else:
                    return {
                        'success': False,
                        'error': result.get('error', 'Erreur inconnue de l\'API'),
                        'source': 'azure_ml'
                    }
            else:
                return {
                    'success': False,
                    'error': f'Erreur HTTP {response.status_code}: {response.text}',
                    'source': 'azure_ml'
                }
                
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'Timeout lors de l\'appel à l\'API Azure ML',
                'source': 'azure_ml'
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Erreur de connexion: {str(e)}',
                'source': 'azure_ml'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Erreur inattendue: {str(e)}',
                'source': 'azure_ml'
            }
    
    def _predict_local(self, image: Image.Image, text_description: str) -> Dict[str, Any]:
        """Prédiction de démonstration (fallback)"""
        try:
            # Simulation d'une prédiction basée sur des règles simples
            combined_text = text_description.lower()
            
            # Catégories disponibles
            categories = [
                'Baby Care', 'Beauty and Personal Care', 'Computers',
                'Home Decor & Festive Needs', 'Home Furnishing',
                'Kitchen & Dining', 'Watches'
            ]
            
            # Règles simples basées sur les mots-clés
            category_keywords = {
                'Baby Care': ['baby', 'enfant', 'bébé', 'nourrisson', 'couche', 'jouet', 'poussette', 'biberon', 'tétine'],
                'Beauty and Personal Care': ['beauté', 'cosmétique', 'soin', 'shampooing', 'crème', 'maquillage', 'parfum', 'lotion', 'gel'],
                'Computers': ['ordinateur', 'laptop', 'pc', 'computer', 'écran', 'clavier', 'souris', 'processeur', 'mémoire'],
                'Home Decor & Festive Needs': ['déco', 'décoration', 'fête', 'festif', 'ornement', 'bougie', 'cadre', 'tableau'],
                'Home Furnishing': ['meuble', 'furniture', 'canapé', 'table', 'chaise', 'lit', 'armoire', 'étagère', 'bureau'],
                'Kitchen & Dining': ['cuisine', 'kitchen', 'vaisselle', 'casserole', 'four', 'réfrigérateur', 'assiette', 'verre', 'couteau'],
                'Watches': ['montre', 'watch', 'horloge', 'chronomètre', 'bracelet', 'sapphero', 'digital', 'analogique', 'sport']
            }
            
            # Calculer les scores avec une logique améliorée
            scores = {}
            for category, keywords in category_keywords.items():
                matches = sum(1 for keyword in keywords if keyword in combined_text)
                if matches > 0:
                    # Score basé sur le nombre de correspondances et la longueur du texte
                    base_score = matches / len(keywords)
                    # Bonus pour les correspondances multiples
                    bonus = min(0.3, matches * 0.1)
                    scores[category] = min(1.0, base_score + bonus)
                else:
                    scores[category] = 0.0
            
            # Prédiction
            if max(scores.values()) > 0:
                predicted_category = max(scores, key=scores.get)
                confidence = max(scores.values())
            else:
                # Si aucun mot-clé ne correspond, donner des scores aléatoires mais réalistes
                import random
                predicted_category = 'Home Furnishing'  # Catégorie par défaut
                confidence = 0.15
                
                # Ajouter des scores aléatoires pour simuler une prédiction
                for category in categories:
                    if category not in scores or scores[category] == 0:
                        scores[category] = random.uniform(0.01, 0.08)
                
                # S'assurer que la catégorie prédite a le score le plus élevé
                scores[predicted_category] = confidence
            
            return {
                'success': True,
                'predicted_category': predicted_category,
                'confidence': confidence,
                'category_scores': scores,
                'source': 'demo'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Erreur lors de la prédiction de démonstration: {str(e)}',
                'source': 'demo'
            }
    
    def get_service_status(self) -> Dict[str, Any]:
        """Vérifier le statut du service Azure ML"""
        if self.use_local:
            return {
                'status': 'local',
                'message': 'Utilisation du modèle local'
            }
        
        try:
            # Test simple de connectivité
            response = requests.get(
                self.endpoint_url.replace('/score', '/health'),
                timeout=5
            )
            return {
                'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                'message': f'Service Azure ML - Status: {response.status_code}'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Impossible de contacter le service: {str(e)}'
            }

# Instance globale du client
@st.cache_resource
def get_azure_client():
    """Obtenir l'instance du client Azure ML"""
    return AzureMLClient()
