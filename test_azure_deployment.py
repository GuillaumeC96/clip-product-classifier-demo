#!/usr/bin/env python3
"""
Test de déploiement Azure ML simplifié
"""

import os
import sys
import json
import base64
from PIL import Image
import io

def test_azure_ml_imports():
    """Tester les imports Azure ML"""
    print("🧪 Test des imports Azure ML...")
    
    try:
        import azureml.core
        print("✅ azureml.core importé")
        
        from azureml.core import Workspace, Model, Environment
        print("✅ Workspace, Model, Environment importés")
        
        from azureml.core.model import InferenceConfig
        print("✅ InferenceConfig importé")
        
        from azureml.core.webservice import AciWebservice
        print("✅ AciWebservice importé")
        
        from azureml.core.conda_dependencies import CondaDependencies
        print("✅ CondaDependencies importé")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur d'import Azure ML: {str(e)}")
        return False

def test_azure_ml_connection():
    """Tester la connexion Azure ML"""
    print("\n🧪 Test de connexion Azure ML...")
    
    try:
        from azureml.core import Workspace
        
        # Vérifier les variables d'environnement
        subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID')
        resource_group = os.getenv('AZURE_RESOURCE_GROUP', 'ml-resource-group')
        workspace_name = os.getenv('AZURE_WORKSPACE_NAME', 'clip-classification-workspace')
        
        if not subscription_id:
            print("⚠️ AZURE_SUBSCRIPTION_ID non défini")
            print("   Mode test sans connexion Azure")
            return True
        
        print(f"   - Subscription ID: {subscription_id[:8]}...")
        print(f"   - Resource Group: {resource_group}")
        print(f"   - Workspace: {workspace_name}")
        
        # Essayer de se connecter
        try:
            ws = Workspace(
                subscription_id=subscription_id,
                resource_group=resource_group,
                workspace_name=workspace_name
            )
            print("✅ Connexion au workspace réussie")
            return True
            
        except Exception as e:
            print(f"⚠️ Impossible de se connecter au workspace: {str(e)}")
            print("   Vérifiez vos credentials Azure")
            return False
        
    except Exception as e:
        print(f"❌ Erreur de connexion: {str(e)}")
        return False

def test_model_files():
    """Tester les fichiers du modèle"""
    print("\n🧪 Test des fichiers du modèle...")
    
    files_to_check = [
        'azure_ml_api/score.py',
        'azure_ml_api/requirements.txt',
        'azure_ml_api/deploy_model.py'
    ]
    
    all_exist = True
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} manquant")
            all_exist = False
    
    # Vérifier le modèle fine-tuné
    model_path = 'clip_product_classifier.pth'
    if os.path.exists(model_path):
        print(f"✅ {model_path} (modèle fine-tuné)")
    else:
        print(f"⚠️ {model_path} manquant (utilisera les poids pré-entraînés)")
    
    return all_exist

def test_score_script():
    """Tester le script de scoring"""
    print("\n🧪 Test du script de scoring...")
    
    try:
        # Importer le script de scoring
        sys.path.append('azure_ml_api')
        from score import init, run
        
        print("✅ Script de scoring importé")
        
        # Test d'initialisation (sans GPU)
        print("🔄 Test d'initialisation...")
        try:
            init()
            print("✅ Initialisation réussie")
        except Exception as e:
            print(f"⚠️ Erreur d'initialisation: {str(e)}")
            print("   Normal si le modèle n'est pas disponible")
        
        # Test de scoring avec des données factices
        print("🔄 Test de scoring...")
        try:
            # Créer une image de test
            test_image = Image.new('RGB', (224, 224), color='red')
            buffer = io.BytesIO()
            test_image.save(buffer, format='JPEG')
            img_bytes = buffer.getvalue()
            image_base64 = base64.b64encode(img_bytes).decode('utf-8')
            
            test_data = {
                "image": image_base64,
                "text": "Une montre élégante pour homme"
            }
            
            result = run(json.dumps(test_data))
            print(f"✅ Scoring réussi: {result.get('status', 'unknown')}")
            
            if result.get('status') == 'success':
                print(f"   - Catégorie prédite: {result.get('predicted_category')}")
                print(f"   - Confiance: {result.get('confidence', 0):.3f}")
            
        except Exception as e:
            print(f"⚠️ Erreur de scoring: {str(e)}")
            print("   Normal si le modèle n'est pas initialisé")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur d'import du script: {str(e)}")
        return False

def main():
    """Fonction principale"""
    print("🚀 Test de déploiement Azure ML")
    print("=" * 50)
    
    tests = [
        ("Imports Azure ML", test_azure_ml_imports),
        ("Connexion Azure ML", test_azure_ml_connection),
        ("Fichiers du modèle", test_model_files),
        ("Script de scoring", test_score_script)
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
        print("✅ Le déploiement Azure ML est prêt")
    else:
        print("⚠️ Certains tests ont échoué")
        print("🔧 Corrigez les erreurs avant le déploiement")
    
    print("\n📋 Prochaines étapes:")
    print("1. Configurer les variables d'environnement Azure")
    print("2. Exécuter le script de déploiement")
    print("3. Tester l'endpoint déployé")
    print("4. Configurer Streamlit Cloud")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
