#!/usr/bin/env python3
"""
Script de déploiement pour le nouveau modèle CLIP
"""

import os
import json
import torch
from azure.ai.ml import MLClient
from azure.ai.ml.entities import (
    ManagedOnlineEndpoint,
    ManagedOnlineDeployment,
    Model,
    Environment,
    CodeConfiguration,
)
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv('.env_azure_production')

def load_env_file():
    """Charger les variables d'environnement depuis le fichier .env_azure_production"""
    env_file = '.env_azure_production'
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
        print(f"✅ Variables d'environnement chargées depuis {env_file}")
    else:
        print(f"⚠️ Fichier {env_file} non trouvé")

def verify_model():
    """Vérifier le nouveau modèle"""
    model_path = "new_clip_product_classifier.pth"
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Modèle non trouvé: {model_path}")
    
    print(f"📁 Modèle trouvé: {model_path}")
    print(f"📊 Taille: {os.path.getsize(model_path) / (1024**3):.2f} GB")
    
    # Vérifier la structure du modèle
    try:
        checkpoint = torch.load(model_path, map_location='cpu')
        print("🔍 Structure du modèle:")
        for key in checkpoint.keys():
            if isinstance(checkpoint[key], dict):
                print(f"  - {key}: {list(checkpoint[key].keys())}")
            else:
                print(f"  - {key}: {type(checkpoint[key])}")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la vérification du modèle: {e}")
        return False

def create_ml_client():
    """Créer le client ML"""
    subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID')
    resource_group = os.getenv('AZURE_RESOURCE_GROUP')
    workspace_name = os.getenv('AZURE_WORKSPACE_NAME')
    
    if not all([subscription_id, resource_group, workspace_name]):
        raise ValueError("Variables d'environnement Azure manquantes")
    
    credential = DefaultAzureCredential()
    ml_client = MLClient(credential, subscription_id, resource_group, workspace_name)
    
    print(f"✅ Client ML créé pour {workspace_name}")
    return ml_client

def create_endpoint(ml_client, endpoint_name="clip-classifier-endpoint"):
    """Créer ou mettre à jour l'endpoint"""
    try:
        # Vérifier si l'endpoint existe
        try:
            endpoint = ml_client.online_endpoints.get(endpoint_name)
            print(f"✅ Endpoint existant trouvé: {endpoint_name}")
            return endpoint
        except:
            # Créer un nouvel endpoint
            endpoint = ManagedOnlineEndpoint(
                name=endpoint_name,
                description="Endpoint pour le nouveau modèle CLIP",
                auth_mode="key"
            )
            
            endpoint = ml_client.online_endpoints.begin_create_or_update(endpoint).result()
            print(f"✅ Nouvel endpoint créé: {endpoint_name}")
            return endpoint
            
    except Exception as e:
        print(f"❌ Erreur lors de la création de l'endpoint: {e}")
        raise

def register_model(ml_client, model_name="new-clip-classifier"):
    """Enregistrer le nouveau modèle"""
    try:
        # Vérifier si le modèle existe déjà
        try:
            model = ml_client.models.get(model_name, version="1")
            print(f"✅ Modèle existant trouvé: {model_name}")
            return model
        except:
            # Enregistrer le nouveau modèle
            model = Model(
                name=model_name,
                path="new_clip_product_classifier.pth",
                description="Nouveau modèle CLIP fine-tuné",
                version="1"
            )
            
            model = ml_client.models.create_or_update(model)
            print(f"✅ Nouveau modèle enregistré: {model_name}")
            return model
            
    except Exception as e:
        print(f"❌ Erreur lors de l'enregistrement du modèle: {e}")
        raise

def create_environment(ml_client, env_name="clip-env-v2"):
    """Créer l'environnement pour le nouveau modèle"""
    try:
        # Vérifier si l'environnement existe
        try:
            env = ml_client.environments.get(env_name, version="1")
            print(f"✅ Environnement existant trouvé: {env_name}")
            return env
        except:
            # Créer un nouvel environnement
            env = Environment(
                name=env_name,
                description="Environnement pour le nouveau modèle CLIP",
                image="mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04:latest",
                conda_file="azure_ml_api/environment.yml",
                version="1"
            )
            
            env = ml_client.environments.create_or_update(env)
            print(f"✅ Nouvel environnement créé: {env_name}")
            return env
            
    except Exception as e:
        print(f"❌ Erreur lors de la création de l'environnement: {e}")
        raise

def create_deployment(ml_client, endpoint_name, model, environment, deployment_name="new-clip-deployment"):
    """Créer le déploiement"""
    try:
        # Vérifier si le déploiement existe
        try:
            deployment = ml_client.online_deployments.get(endpoint_name, deployment_name)
            print(f"✅ Déploiement existant trouvé: {deployment_name}")
            return deployment
        except:
            # Créer un nouveau déploiement
            deployment = ManagedOnlineDeployment(
                name=deployment_name,
                endpoint_name=endpoint_name,
                model=model,
                environment=environment,
                code_configuration=CodeConfiguration(
                    source="azure_ml_api",
                    scoring_script="score.py"
                ),
                instance_type="Standard_DS2_v2",  # Instance minimale pour économiser
                instance_count=1,
                description="Déploiement du nouveau modèle CLIP"
            )
            
            deployment = ml_client.online_deployments.begin_create_or_update(deployment).result()
            print(f"✅ Nouveau déploiement créé: {deployment_name}")
            return deployment
            
    except Exception as e:
        print(f"❌ Erreur lors de la création du déploiement: {e}")
        raise

def set_traffic(ml_client, endpoint_name, deployment_name):
    """Définir le trafic vers le nouveau déploiement"""
    try:
        endpoint = ml_client.online_endpoints.get(endpoint_name)
        endpoint.traffic = {deployment_name: 100}
        endpoint = ml_client.online_endpoints.begin_create_or_update(endpoint).result()
        print(f"✅ Trafic défini à 100% vers {deployment_name}")
        return endpoint
    except Exception as e:
        print(f"❌ Erreur lors de la définition du trafic: {e}")
        raise

def get_endpoint_info(ml_client, endpoint_name):
    """Récupérer les informations de l'endpoint"""
    try:
        endpoint = ml_client.online_endpoints.get(endpoint_name)
        print(f"\n🎯 Informations de l'endpoint:")
        print(f"   - Nom: {endpoint.name}")
        print(f"   - URL: {endpoint.scoring_uri}")
        print(f"   - État: {endpoint.provisioning_state}")
        print(f"   - Trafic: {endpoint.traffic}")
        
        # Récupérer la clé API
        keys = ml_client.online_endpoints.get_keys(endpoint_name)
        print(f"   - Clé API: {keys.primary_key[:10]}...")
        
        return endpoint.scoring_uri, keys.primary_key
        
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des informations: {e}")
        raise

def main():
    """Fonction principale"""
    print("🚀 Déploiement du nouveau modèle CLIP")
    print("=" * 50)
    
    try:
        # 1. Charger les variables d'environnement
        load_env_file()
        
        # 2. Vérifier le modèle
        if not verify_model():
            return
        
        # 3. Créer le client ML
        ml_client = create_ml_client()
        
        # 4. Créer l'endpoint
        endpoint_name = "clip-classifier-endpoint"
        endpoint = create_endpoint(ml_client, endpoint_name)
        
        # 5. Enregistrer le modèle
        model = register_model(ml_client)
        
        # 6. Créer l'environnement
        environment = create_environment(ml_client)
        
        # 7. Créer le déploiement
        deployment_name = "new-clip-deployment"
        deployment = create_deployment(ml_client, endpoint_name, model, environment, deployment_name)
        
        # 8. Définir le trafic
        set_traffic(ml_client, endpoint_name, deployment_name)
        
        # 9. Récupérer les informations
        endpoint_url, api_key = get_endpoint_info(ml_client, endpoint_name)
        
        print(f"\n✅ Déploiement terminé avec succès!")
        print(f"🔗 URL de l'endpoint: {endpoint_url}")
        print(f"🔑 Clé API: {api_key[:10]}...")
        
        # Mettre à jour le fichier .env_azure_production
        with open('.env_azure_production', 'a') as f:
            f.write(f"\n# Nouveau modèle déployé\n")
            f.write(f"AZURE_ML_ENDPOINT_URL={endpoint_url}\n")
            f.write(f"AZURE_ML_API_KEY={api_key}\n")
        
        print(f"\n📝 Variables d'environnement mises à jour dans .env_azure_production")
        
    except Exception as e:
        print(f"❌ Erreur lors du déploiement: {e}")
        raise

if __name__ == "__main__":
    main()
