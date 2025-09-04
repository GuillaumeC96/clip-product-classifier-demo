"""
Script pour déployer le modèle CLIP sur Azure ML
"""

import os
import azureml.core
from azureml.core import Workspace, Model, Environment
from azureml.core.model import InferenceConfig
from azureml.core.webservice import AciWebservice, LocalWebservice
from azureml.core.conda_dependencies import CondaDependencies

def deploy_model():
    """Déployer le modèle CLIP sur Azure ML"""
    
    # Configuration
    subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID')
    resource_group = os.getenv('AZURE_RESOURCE_GROUP', 'ml-resource-group')
    workspace_name = os.getenv('AZURE_WORKSPACE_NAME', 'clip-classification-workspace')
    
    if not subscription_id:
        raise ValueError("AZURE_SUBSCRIPTION_ID doit être défini dans les variables d'environnement")
    
    # Se connecter au workspace Azure ML
    try:
        ws = Workspace(
            subscription_id=subscription_id,
            resource_group=resource_group,
            workspace_name=workspace_name
        )
        print(f"Connecté au workspace: {ws.name}")
    except Exception as e:
        print(f"Erreur lors de la connexion au workspace: {e}")
        print("Création d'un nouveau workspace...")
        ws = Workspace.create(
            name=workspace_name,
            subscription_id=subscription_id,
            resource_group=resource_group,
            create_resource_group=True,
            location='westeurope'
        )
    
    # Créer l'environnement
    env = Environment('clip-classification-env')
    
    # Définir les dépendances conda
    conda_dep = CondaDependencies()
    conda_dep.add_pip_package("torch>=2.0.0")
    conda_dep.add_pip_package("torchvision>=0.15.0")
    conda_dep.add_pip_package("transformers>=4.30.0")
    conda_dep.add_pip_package("pillow>=9.0.0")
    conda_dep.add_pip_package("numpy>=1.24.0")
    conda_dep.add_pip_package("scikit-learn>=1.3.0")
    conda_dep.add_pip_package("azureml-core>=1.50.0")
    conda_dep.add_pip_package("azureml-inference-server-http>=0.7.0")
    
    env.python.conda_dependencies = conda_dep
    
    # Enregistrer l'environnement
    env.register(workspace=ws)
    
    # Enregistrer le modèle
    model_path = "clip_product_classifier.pth"
    if os.path.exists(model_path):
        model = Model.register(
            workspace=ws,
            model_path=model_path,
            model_name="clip-product-classifier",
            description="Modèle CLIP fine-tuné pour la classification de produits"
        )
        print(f"Modèle enregistré: {model.name}")
    else:
        print(f"Attention: Le fichier {model_path} n'existe pas. Le modèle utilisera les poids pré-entraînés.")
        # Créer un modèle factice pour la structure
        model = Model.register(
            workspace=ws,
            model_path=".",
            model_name="clip-product-classifier",
            description="Modèle CLIP pour la classification de produits (poids pré-entraînés)"
        )
    
    # Configuration d'inférence
    inference_config = InferenceConfig(
        source_directory="./",
        entry_script="score.py",
        environment=env
    )
    
    # Configuration du déploiement
    deployment_config = AciWebservice.deploy_configuration(
        cpu_cores=2,
        memory_gb=4,
        tags={"data": "products", "method": "clip"},
        description="API de classification de produits avec CLIP"
    )
    
    # Déployer le service
    service_name = "clip-classification-service"
    service = Model.deploy(
        workspace=ws,
        name=service_name,
        models=[model],
        inference_config=inference_config,
        deployment_config=deployment_config,
        overwrite=True
    )
    
    service.wait_for_deployment(show_output=True)
    
    print(f"Service déployé: {service.name}")
    print(f"URL du service: {service.scoring_uri}")
    
    return service

if __name__ == "__main__":
    service = deploy_model()
    
    # Test du service
    import requests
    import json
    import base64
    
    # Exemple de test (remplacer par une vraie image en base64)
    test_data = {
        "image": "",  # Image en base64
        "text": "Une montre élégante pour homme"
    }
    
    try:
        response = requests.post(
            service.scoring_uri,
            data=json.dumps(test_data),
            headers={'Content-Type': 'application/json'}
        )
        print(f"Réponse du service: {response.json()}")
    except Exception as e:
        print(f"Erreur lors du test: {e}")
