#!/usr/bin/env python3
"""
Test complet du déploiement
"""

import os
import sys
import json
import base64
from PIL import Image
import io
import requests

def create_test_image():
    """Créer une image de test"""
    # Créer une image de test avec des couleurs
    img = Image.new('RGB', (224, 224), color='lightblue')
    return img

def test_azure_ml_scoring():
    """Tester le scoring Azure ML directement"""
    print("🧪 Test du scoring Azure ML...")
    
    try:
        # Aller dans le dossier azure_ml_api
        original_dir = os.getcwd()
        os.chdir('azure_ml_api')
        
        # Ajouter le dossier au path pour l'import
        sys.path.insert(0, '.')
        
        # Importer le script de scoring
        from score import init, run
        
        # Initialiser le modèle
        print("🔄 Initialisation du modèle...")
        init()
        print("✅ Modèle initialisé")
        
        # Créer une image de test
        test_image = create_test_image()
        buffer = io.BytesIO()
        test_image.save(buffer, format='JPEG')
        img_bytes = buffer.getvalue()
        image_base64 = base64.b64encode(img_bytes).decode('utf-8')
        
        # Données de test
        test_data = {
            "image": image_base64,
            "text": "Une montre élégante pour homme en cuir noir avec bracelet en métal"
        }
        
        # Test de scoring
        print("🔄 Test de scoring...")
        result = run(json.dumps(test_data))
        
        if result.get('status') == 'success':
            print("✅ Scoring réussi !")
            print(f"   - Catégorie prédite: {result['predicted_category']}")
            print(f"   - Confiance: {result['confidence']:.3f}")
            
            print("   - Scores par catégorie:")
            for category, score in result['category_scores'].items():
                print(f"     * {category}: {score:.3f}")
            
            return True
        else:
            print(f"❌ Erreur de scoring: {result.get('error', 'Erreur inconnue')}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        return False
    finally:
        # Revenir au dossier parent
        os.chdir(original_dir)
        # Nettoyer le path
        if '.' in sys.path:
            sys.path.remove('.')

def test_streamlit_app():
    """Tester l'application Streamlit"""
    print("\n🧪 Test de l'application Streamlit...")
    
    try:
        # Tester la connectivité
        response = requests.get("http://localhost:8502", timeout=5)
        if response.status_code == 200:
            print("✅ Application Streamlit accessible")
            print(f"   - Status: {response.status_code}")
            print(f"   - URL: http://localhost:8502")
            return True
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {str(e)}")
        return False

def test_environment():
    """Tester l'environnement"""
    print("\n🧪 Test de l'environnement...")
    
    try:
        # Vérifier les imports essentiels
        import streamlit as st
        print("✅ Streamlit importé")
        
        from azure_client import AzureMLClient
        print("✅ Client Azure ML importé")
        
        import torch
        print(f"✅ PyTorch importé (version: {torch.__version__})")
        
        from transformers import CLIPModel
        print("✅ Transformers importé")
        
        import spacy
        nlp = spacy.load("en_core_web_trf")
        print("✅ spaCy importé et modèle chargé")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur d'environnement: {str(e)}")
        return False

def main():
    """Fonction principale"""
    print("🚀 Test complet du déploiement")
    print("=" * 60)
    
    tests = [
        ("Environnement", test_environment),
        ("Application Streamlit", test_streamlit_app),
        ("Scoring Azure ML", test_azure_ml_scoring)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        success = test_func()
        results.append((test_name, success))
    
    print("\n" + "=" * 60)
    print("📊 Résultats finaux")
    print("=" * 60)
    
    all_passed = True
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if not success:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 DÉPLOIEMENT RÉUSSI !")
        print("✅ Tous les composants fonctionnent correctement")
        print("\n🌐 Application accessible:")
        print("   - URL: http://localhost:8502")
        print("   - Mode: Local (prêt pour le cloud)")
        print("\n📋 Prochaines étapes pour le déploiement cloud:")
        print("   1. Configurer Azure ML avec vos credentials")
        print("   2. Déployer le modèle avec ./deploy_azure.sh")
        print("   3. Configurer Streamlit Cloud")
        print("   4. Déployer l'application finale")
    else:
        print("⚠️ Certains tests ont échoué")
        print("🔧 Corrigez les erreurs avant le déploiement")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
