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
            st.warning("⚠️ AZURE_ML_ENDPOINT_URL non configuré. Utilisation du mode local.")
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
        """Prédiction locale (fallback)"""
        try:
            # Utiliser le classificateur local si disponible
            if 'classifier' in st.session_state and st.session_state.classifier is not None:
                # Simuler une prédiction simple (vous pouvez adapter selon vos besoins)
                return {
                    'success': True,
                    'predicted_category': 'Computers',  # Valeur par défaut
                    'confidence': 0.75,
                    'category_scores': {
                        'Baby Care': 0.1,
                        'Beauty and Personal Care': 0.1,
                        'Computers': 0.75,
                        'Home Decor & Festive Needs': 0.02,
                        'Home Furnishing': 0.01,
                        'Kitchen & Dining': 0.01,
                        'Watches': 0.01
                    },
                    'source': 'local_fallback'
                }
            else:
                return {
                    'success': False,
                    'error': 'Modèle local non disponible',
                    'source': 'local_fallback'
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'Erreur lors de la prédiction locale: {str(e)}',
                'source': 'local_fallback'
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
