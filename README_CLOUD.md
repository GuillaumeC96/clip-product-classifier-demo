# Déploiement Cloud - Classification de Produits avec CLIP

Ce guide explique comment déployer l'application de classification de produits sur le cloud avec Azure ML et Streamlit Cloud.

## Architecture Cloud

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit     │    │   Azure ML      │    │   Modèle CLIP   │
│   Cloud         │◄──►│   Endpoint      │◄──►│   Fine-tuné     │
│   (Frontend)    │    │   (Backend)     │    │   (Inference)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Prérequis

1. **Compte Azure** avec accès à Azure ML
2. **Compte GitHub** pour Streamlit Cloud
3. **Modèle CLIP fine-tuné** (`clip_product_classifier.pth`)

## Étapes de déploiement

### 1. Déploiement sur Azure ML

#### 1.1 Configuration Azure

```bash
# Installer Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Se connecter à Azure
az login

# Créer un groupe de ressources
az group create --name ml-resource-group --location westeurope

# Créer un workspace Azure ML
az ml workspace create --name clip-classification-workspace --resource-group ml-resource-group --location westeurope
```

#### 1.2 Déploiement du modèle

```bash
# Aller dans le dossier Azure ML
cd azure_ml_api

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
export AZURE_SUBSCRIPTION_ID="your_subscription_id"
export AZURE_RESOURCE_GROUP="ml-resource-group"
export AZURE_WORKSPACE_NAME="clip-classification-workspace"

# Déployer le modèle
python deploy_model.py
```

#### 1.3 Récupérer les informations de l'endpoint

Après le déploiement, notez :
- **URL de l'endpoint** : `https://your-endpoint.westeurope.inference.ml.azure.com/score`
- **Clé API** : Récupérée depuis le portail Azure ML

### 2. Déploiement sur Streamlit Cloud

#### 2.1 Préparation du repository GitHub

1. **Pousser le code sur GitHub** :
```bash
git init
git add .
git commit -m "Initial commit - Cloud deployment"
git branch -M main
git remote add origin https://github.com/yourusername/your-repo.git
git push -u origin main
```

2. **Fichiers requis** :
   - `accueil_cloud.py` (point d'entrée principal)
   - `pages/2_prediction_cloud.py` (page de prédiction)
   - `azure_client.py` (client Azure ML)
   - `accessibility.py` (module d'accessibilité)
   - `requirements_cloud.txt` (dépendances)
   - `.streamlit/config.toml` (configuration Streamlit)

#### 2.2 Configuration des secrets

1. **Aller sur [Streamlit Cloud](https://share.streamlit.io/)**
2. **Connecter votre repository GitHub**
3. **Configurer les secrets** :
   - `AZURE_ML_ENDPOINT_URL` : URL de votre endpoint Azure ML
   - `AZURE_ML_API_KEY` : Clé API Azure ML
   - `USE_LOCAL_MODEL` : `false` (pour utiliser Azure ML)

#### 2.3 Déploiement

1. **Sélectionner le repository**
2. **Choisir le fichier principal** : `accueil_cloud.py`
3. **Configurer les secrets** (voir section précédente)
4. **Déployer**

## Configuration des variables d'environnement

### Pour Streamlit Cloud (secrets.toml)

```toml
AZURE_ML_ENDPOINT_URL = "https://your-endpoint.westeurope.inference.ml.azure.com/score"
AZURE_ML_API_KEY = "your_api_key_here"
USE_LOCAL_MODEL = false
```

### Pour le développement local

```bash
export AZURE_ML_ENDPOINT_URL="https://your-endpoint.westeurope.inference.ml.azure.com/score"
export AZURE_ML_API_KEY="your_api_key_here"
export USE_LOCAL_MODEL="false"
```

## Structure des fichiers

```
application/
├── accueil_cloud.py              # Point d'entrée principal (cloud)
├── azure_client.py               # Client Azure ML
├── accessibility.py              # Module d'accessibilité
├── pages/
│   ├── 2_prediction_cloud.py     # Page de prédiction (cloud)
│   └── 1_eda.py                  # Page EDA (inchangée)
├── azure_ml_api/
│   ├── score.py                  # Script de scoring Azure ML
│   ├── deploy_model.py           # Script de déploiement
│   └── requirements.txt          # Dépendances Azure ML
├── .streamlit/
│   ├── config.toml               # Configuration Streamlit
│   └── secrets.toml.example      # Exemple de secrets
├── requirements_cloud.txt        # Dépendances Streamlit Cloud
└── README_CLOUD.md              # Ce fichier
```

## Fonctionnalités

### Mode Cloud (recommandé)
- ✅ Inférence sur Azure ML
- ✅ Scalabilité automatique
- ✅ Haute disponibilité
- ✅ Monitoring intégré

### Mode Local (fallback)
- ✅ Fonctionnement hors ligne
- ✅ Développement local
- ⚠️ Limité par les ressources locales

## Monitoring et maintenance

### Azure ML
- **Métriques** : Disponibles dans le portail Azure ML
- **Logs** : Accessibles via Application Insights
- **Coûts** : Facturation basée sur l'utilisation

### Streamlit Cloud
- **Logs** : Disponibles dans l'interface Streamlit Cloud
- **Métriques** : Nombre d'utilisateurs, temps de réponse
- **Coûts** : Gratuit pour les applications publiques

## Dépannage

### Problèmes courants

1. **Erreur de connexion Azure ML** :
   - Vérifier l'URL de l'endpoint
   - Vérifier la clé API
   - Vérifier le statut du service Azure ML

2. **Timeout de l'API** :
   - Augmenter le timeout dans `azure_client.py`
   - Vérifier la charge du service Azure ML

3. **Erreur de déploiement Streamlit** :
   - Vérifier les secrets
   - Vérifier les dépendances dans `requirements_cloud.txt`

### Logs utiles

```python
# Dans azure_client.py
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

## Coûts estimés

### Azure ML
- **ACI (Azure Container Instances)** : ~0.10€/heure
- **Stockage** : ~0.02€/GB/mois
- **Réseau** : ~0.05€/GB

### Streamlit Cloud
- **Gratuit** pour les applications publiques
- **Pro** : 20$/mois pour les applications privées

## Sécurité

- ✅ HTTPS obligatoire
- ✅ Authentification par clé API
- ✅ Secrets gérés par Streamlit Cloud
- ✅ Isolation des conteneurs Azure

## Support

Pour toute question ou problème :
1. Vérifier les logs Azure ML
2. Vérifier les logs Streamlit Cloud
3. Consulter la documentation Azure ML
4. Consulter la documentation Streamlit Cloud
