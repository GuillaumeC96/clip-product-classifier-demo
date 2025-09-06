#!/usr/bin/env python3
"""
Script de déploiement pour le modèle CLIP fine-tuné avec vraie logique d'attention
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
        print("✅ Variables d'environnement chargées depuis .env_azure_production")
    else:
        print("❌ Fichier .env_azure_production non trouvé")

def create_ml_client():
    """Créer le client ML"""
    subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID')
    resource_group = os.getenv('AZURE_RESOURCE_GROUP')
    workspace_name = os.getenv('AZURE_WORKSPACE_NAME')
    
    if not all([subscription_id, resource_group, workspace_name]):
        raise ValueError("Variables d'environnement Azure manquantes")
    
    credential = DefaultAzureCredential()
    ml_client = MLClient(
        credential=credential,
        subscription_id=subscription_id,
        resource_group_name=resource_group,
        workspace_name=workspace_name
    )
    
    print(f"✅ Client ML créé pour {workspace_name}")
    return ml_client

def create_endpoint(ml_client, endpoint_name):
    """Créer l'endpoint"""
    try:
        # Vérifier si l'endpoint existe déjà
        try:
            existing_endpoint = ml_client.online_endpoints.get(endpoint_name)
            print(f"✅ Endpoint existant trouvé: {endpoint_name}")
            return existing_endpoint
        except:
            pass
        
        # Créer un nouvel endpoint
        endpoint = ManagedOnlineEndpoint(
            name=endpoint_name,
            description="Endpoint pour le modèle CLIP fine-tuné avec attention",
            auth_mode="key"
        )
        
        print(f"🚀 Création de l'endpoint: {endpoint_name}")
        endpoint = ml_client.online_endpoints.begin_create_or_update(endpoint).result()
        print(f"✅ Endpoint créé: {endpoint_name}")
        return endpoint
        
    except Exception as e:
        print(f"❌ Erreur lors de la création de l'endpoint: {str(e)}")
        raise e

def register_model(ml_client, model_name, model_path):
    """Enregistrer le modèle"""
    try:
        # Vérifier si le modèle existe déjà
        try:
            existing_model = ml_client.models.get(model_name)
            print(f"✅ Modèle existant trouvé: {model_name}")
            return existing_model
        except:
            pass
        
        # Enregistrer le modèle
        model = Model(
            name=model_name,
            path=model_path,
            description="Modèle CLIP fine-tuné pour la classification de produits"
        )
        
        print(f"🚀 Enregistrement du modèle: {model_name}")
        model = ml_client.models.create_or_update(model)
        print(f"✅ Modèle enregistré: {model_name}")
        return model
        
    except Exception as e:
        print(f"❌ Erreur lors de l'enregistrement du modèle: {str(e)}")
        raise e

def create_environment(ml_client, env_name):
    """Créer l'environnement"""
    try:
        # Vérifier si l'environnement existe déjà
        try:
            existing_env = ml_client.environments.get(env_name)
            print(f"✅ Environnement existant trouvé: {env_name}")
            return existing_env
        except:
            pass
        
        # Créer l'environnement
        environment = Environment(
            name=env_name,
            description="Environnement pour le modèle CLIP fine-tuné",
            conda_file="azure_ml_api/environment.yml",
            image="mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04:latest"
        )
        
        print(f"🚀 Création de l'environnement: {env_name}")
        environment = ml_client.environments.create_or_update(environment)
        print(f"✅ Environnement créé: {env_name}")
        return environment
        
    except Exception as e:
        print(f"❌ Erreur lors de la création de l'environnement: {str(e)}")
        raise e

def create_deployment(ml_client, endpoint_name, model, environment, deployment_name):
    """Créer le déploiement"""
    try:
        # Vérifier si le déploiement existe déjà
        try:
            existing_deployment = ml_client.online_deployments.get(endpoint_name, deployment_name)
            print(f"✅ Déploiement existant trouvé: {deployment_name}")
            return existing_deployment
        except:
            pass
        
        # Créer le déploiement
        deployment = ManagedOnlineDeployment(
            name=deployment_name,
            endpoint_name=endpoint_name,
            model=model,
            environment=environment,
            code_configuration=CodeConfiguration(
                source="azure_ml_api",
                scoring_script="score_finetuned.py"
            ),
            instance_type="Standard_DS3_v2",  # Instance plus grande pour le modèle fine-tuné
            instance_count=1,
            description="Déploiement du modèle CLIP fine-tuné avec attention"
        )
        
        print(f"🚀 Création du déploiement: {deployment_name}")
        deployment = ml_client.online_deployments.begin_create_or_update(deployment).result()
        print(f"✅ Déploiement créé: {deployment_name}")
        return deployment
        
    except Exception as e:
        print(f"❌ Erreur lors de la création du déploiement: {str(e)}")
        raise e

def set_traffic(ml_client, endpoint_name, deployment_name, traffic_percentage=100):
    """Définir le trafic vers le déploiement"""
    try:
        endpoint = ml_client.online_endpoints.get(endpoint_name)
        endpoint.traffic = {deployment_name: traffic_percentage}
        
        print(f"🚀 Définition du trafic: {traffic_percentage}% vers {deployment_name}")
        endpoint = ml_client.online_endpoints.begin_create_or_update(endpoint).result()
        print(f"✅ Trafic défini: {traffic_percentage}% vers {deployment_name}")
        return endpoint
        
    except Exception as e:
        print(f"❌ Erreur lors de la définition du trafic: {str(e)}")
        raise e

def get_endpoint_info(ml_client, endpoint_name):
    """Obtenir les informations de l'endpoint"""
    try:
        endpoint = ml_client.online_endpoints.get(endpoint_name)
        
        # Obtenir la clé API
        keys = ml_client.online_endpoints.get_keys(endpoint_name)
        api_key = keys.primary_key
        
        print(f"✅ Informations de l'endpoint:")
        print(f"   - Nom: {endpoint_name}")
        print(f"   - URL: {endpoint.scoring_uri}")
        print(f"   - Clé API: {api_key[:8]}...")
        
        return {
            'endpoint_url': endpoint.scoring_uri,
            'api_key': api_key
        }
        
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des informations: {str(e)}")
        raise e

def main():
    """Fonction principale"""
    print("🚀 Déploiement du modèle CLIP fine-tuné avec attention")
    print("=" * 60)
    
    # Charger les variables d'environnement
    load_env_file()
    
    # Vérifier que le modèle existe
    model_path = "new_clip_product_classifier.pth"
    if not os.path.exists(model_path):
        print(f"❌ Modèle non trouvé: {model_path}")
        return
    
    print(f"📁 Modèle trouvé: {model_path}")
    print(f"📊 Taille: {os.path.getsize(model_path) / (1024*1024*1024):.2f} GB")
    
    # Créer le client ML
    ml_client = create_ml_client()
    
    # Noms des ressources
    endpoint_name = "clip-finetuned-endpoint"
    model_name = "clip-finetuned-model"
    env_name = "clip-finetuned-env"
    deployment_name = "clip-finetuned-deployment"
    
    try:
        # Créer l'endpoint
        endpoint = create_endpoint(ml_client, endpoint_name)
        
        # Enregistrer le modèle
        model = register_model(ml_client, model_name, model_path)
        
        # Créer l'environnement
        environment = create_environment(ml_client, env_name)
        
        # Créer le déploiement
        deployment = create_deployment(ml_client, endpoint_name, model, environment, deployment_name)
        
        # Définir le trafic
        endpoint = set_traffic(ml_client, endpoint_name, deployment_name)
        
        # Obtenir les informations de l'endpoint
        endpoint_info = get_endpoint_info(ml_client, endpoint_name)
        
        # Mettre à jour le fichier .env_azure_production
        env_file = '.env_azure_production'
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                lines = f.readlines()
            
            # Mettre à jour les lignes existantes ou ajouter de nouvelles
            updated_lines = []
            endpoint_url_updated = False
            api_key_updated = False
            
            for line in lines:
                if line.startswith('AZURE_ML_ENDPOINT_URL='):
                    updated_lines.append(f'AZURE_ML_ENDPOINT_URL={endpoint_info["endpoint_url"]}\n')
                    endpoint_url_updated = True
                elif line.startswith('AZURE_ML_API_KEY='):
                    updated_lines.append(f'AZURE_ML_API_KEY={endpoint_info["api_key"]}\n')
                    api_key_updated = True
                else:
                    updated_lines.append(line)
            
            # Ajouter les nouvelles lignes si elles n'existent pas
            if not endpoint_url_updated:
                updated_lines.append(f'AZURE_ML_ENDPOINT_URL={endpoint_info["endpoint_url"]}\n')
            if not api_key_updated:
                updated_lines.append(f'AZURE_ML_API_KEY={endpoint_info["api_key"]}\n')
            
            with open(env_file, 'w') as f:
                f.writelines(updated_lines)
            
            print(f"✅ Fichier .env_azure_production mis à jour")
        
        print("\n🎉 Déploiement terminé avec succès!")
        print(f"🔗 URL de l'endpoint: {endpoint_info['endpoint_url']}")
        print(f"🔑 Clé API: {endpoint_info['api_key'][:8]}...")
        
    except Exception as e:
        print(f"❌ Erreur lors du déploiement: {str(e)}")
        raise e

if __name__ == "__main__":
    main()
