#!/usr/bin/env python3
"""
Test simple de l'application cloud
"""

import sys
import os

def test_imports():
    """Tester les imports essentiels"""
    print("🧪 Test des imports...")
    
    try:
        import streamlit as st
        print("✅ Streamlit importé")
        
        from azure_client import AzureMLClient
        print("✅ Client Azure ML importé")
        
        from accessibility import init_accessibility_state
        print("✅ Module d'accessibilité importé")
        
        import pandas as pd
        print("✅ Pandas importé")
        
        import numpy as np
        print("✅ NumPy importé")
        
        import matplotlib.pyplot as plt
        print("✅ Matplotlib importé")
        
        import spacy
        print("✅ spaCy importé")
        
        from sklearn.preprocessing import LabelEncoder
        print("✅ Scikit-learn importé")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur d'import: {str(e)}")
        return False

def test_azure_client():
    """Tester le client Azure ML"""
    print("\n🧪 Test du client Azure ML...")
    
    try:
        from azure_client import AzureMLClient
        
        client = AzureMLClient()
        print(f"✅ Client initialisé")
        print(f"   - Mode local: {client.use_local}")
        print(f"   - Endpoint: {client.endpoint_url}")
        
        # Test de statut
        status = client.get_service_status()
        print(f"   - Statut: {status['status']}")
        print(f"   - Message: {status['message']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur client Azure: {str(e)}")
        return False

def test_spacy():
    """Tester spaCy"""
    print("\n🧪 Test de spaCy...")
    
    try:
        import spacy
        nlp = spacy.load("en_core_web_trf")
        print("✅ Modèle spaCy chargé")
        
        # Test simple
        doc = nlp("This is a test sentence.")
        print(f"✅ Traitement de texte: {len(doc)} tokens")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur spaCy: {str(e)}")
        return False

def main():
    """Fonction principale"""
    print("🚀 Test simple de l'application cloud")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Client Azure ML", test_azure_client),
        ("spaCy", test_spacy)
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
        print("✅ L'application est prête pour le déploiement")
    else:
        print("⚠️ Certains tests ont échoué")
        print("🔧 Corrigez les erreurs avant le déploiement")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
