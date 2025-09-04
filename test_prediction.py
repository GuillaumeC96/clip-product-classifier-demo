#!/usr/bin/env python3
"""
Test de prédiction avec l'application cloud
"""

import os
import sys
import json
import base64
from PIL import Image
import io
import requests

def create_test_image():
    """Créer une image de test simple"""
    # Créer une image de test avec du texte
    img = Image.new('RGB', (224, 224), color='lightblue')
    return img

def test_local_prediction():
    """Tester la prédiction en mode local"""
    print("🧪 Test de prédiction en mode local...")
    
    try:
        # Importer le client Azure ML
        from azure_client import AzureMLClient
        
        # Créer le client
        client = AzureMLClient()
        print(f"✅ Client créé (mode local: {client.use_local})")
        
        # Créer une image de test
        test_image = create_test_image()
        test_text = "Une montre élégante pour homme en cuir noir"
        
        print("🔄 Test de prédiction...")
        result = client.predict_category(test_image, test_text)
        
        if result['success']:
            print("✅ Prédiction réussie !")
            print(f"   - Catégorie: {result['predicted_category']}")
            print(f"   - Confiance: {result['confidence']:.3f}")
            print(f"   - Source: {result['source']}")
            
            if 'category_scores' in result:
                print("   - Scores par catégorie:")
                for category, score in result['category_scores'].items():
                    print(f"     * {category}: {score:.3f}")
        else:
            print(f"❌ Erreur de prédiction: {result['error']}")
        
        return result['success']
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        return False

def test_streamlit_app():
    """Tester l'application Streamlit"""
    print("\n🧪 Test de l'application Streamlit...")
    
    try:
        # Tester la connectivité
        response = requests.get("http://localhost:8502", timeout=5)
        if response.status_code == 200:
            print("✅ Application Streamlit accessible")
            print(f"   - Status: {response.status_code}")
            print(f"   - Content-Type: {response.headers.get('Content-Type', 'N/A')}")
            return True
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {str(e)}")
        return False

def main():
    """Fonction principale"""
    print("🚀 Test de déploiement et prédiction")
    print("=" * 50)
    
    tests = [
        ("Application Streamlit", test_streamlit_app),
        ("Prédiction locale", test_local_prediction)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        success = test_func()
        results.append((test_name, success))
    
    print("\n" + "=" * 50)
    print("📊 Résultats")
    print("=" * 50)
    
    all_passed = True
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if not success:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 Tous les tests sont passés!")
        print("✅ L'application est opérationnelle")
        print("\n🌐 Accès à l'application:")
        print("   - URL: http://localhost:8502")
        print("   - Page principale: accueil_cloud.py")
        print("   - Page prédiction: pages/2_prediction_cloud.py")
    else:
        print("⚠️ Certains tests ont échoué")
        print("🔧 Vérifiez les erreurs ci-dessus")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
