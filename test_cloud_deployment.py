#!/usr/bin/env python3
"""
Script de test pour vérifier le déploiement cloud
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
    # Créer une image de test simple
    img = Image.new('RGB', (224, 224), color='red')
    return img

def test_azure_client():
    """Tester le client Azure ML"""
    print("🧪 Test du client Azure ML...")
    
    try:
        from azure_client import AzureMLClient
        
        client = AzureMLClient()
        print(f"✅ Client Azure ML initialisé")
        print(f"   - Mode local: {client.use_local}")
        print(f"   - Endpoint: {client.endpoint_url}")
        
        # Test de statut
        status = client.get_service_status()
        print(f"   - Statut: {status['status']}")
        print(f"   - Message: {status['message']}")
        
        # Test de prédiction
        test_image = create_test_image()
        test_text = "Une montre élégante pour homme"
        
        print("🔄 Test de prédiction...")
        result = client.predict_category(test_image, test_text)
        
        if result['success']:
            print(f"✅ Prédiction réussie:")
            print(f"   - Catégorie: {result['predicted_category']}")
            print(f"   - Confiance: {result['confidence']:.3f}")
            print(f"   - Source: {result['source']}")
        else:
            print(f"❌ Erreur de prédiction: {result['error']}")
            
        return result['success']
        
    except Exception as e:
        print(f"❌ Erreur lors du test du client: {str(e)}")
        return False

def test_streamlit_imports():
    """Tester les imports Streamlit"""
    print("🧪 Test des imports Streamlit...")
    
    try:
        import streamlit as st
        print("✅ Streamlit importé")
        
        from accessibility import init_accessibility_state
        print("✅ Module d'accessibilité importé")
        
        # Test des pages
        sys.path.append('pages')
        import importlib.util
        
        # Test de la page de prédiction cloud
        spec = importlib.util.spec_from_file_location("prediction_cloud", "pages/2_prediction_cloud.py")
        if spec and spec.loader:
            print("✅ Page de prédiction cloud trouvée")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors des imports: {str(e)}")
        return False

def test_requirements():
    """Tester les dépendances"""
    print("🧪 Test des dépendances...")
    
    required_packages = [
        'streamlit',
        'pillow',
        'pandas',
        'numpy',
        'plotly',
        'matplotlib',
        'scipy',
        'spacy',
        'scikit-learn',
        'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} manquant")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️ Packages manquants: {', '.join(missing_packages)}")
        print("Installez-les avec: pip install -r requirements_cloud.txt")
        return False
    
    return True

def test_configuration():
    """Tester la configuration"""
    print("🧪 Test de la configuration...")
    
    # Vérifier les fichiers de configuration
    config_files = [
        '.streamlit/config.toml',
        'requirements_cloud.txt',
        'azure_client.py',
        'accueil_cloud.py'
    ]
    
    missing_files = []
    
    for file_path in config_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} manquant")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️ Fichiers manquants: {', '.join(missing_files)}")
        return False
    
    return True

def main():
    """Fonction principale de test"""
    print("🚀 Test du déploiement cloud")
    print("=" * 50)
    
    tests = [
        ("Configuration", test_configuration),
        ("Dépendances", test_requirements),
        ("Imports Streamlit", test_streamlit_imports),
        ("Client Azure ML", test_azure_client)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        success = test_func()
        results.append((test_name, success))
    
    print("\n" + "=" * 50)
    print("📊 Résultats des tests")
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
        print("✅ L'application est prête pour le déploiement cloud")
    else:
        print("⚠️ Certains tests ont échoué")
        print("🔧 Corrigez les erreurs avant le déploiement")
    
    print("\n📋 Prochaines étapes:")
    print("1. Déployer le modèle sur Azure ML")
    print("2. Configurer les secrets Streamlit Cloud")
    print("3. Déployer l'application Streamlit")
    print("4. Tester l'application déployée")

if __name__ == "__main__":
    main()
