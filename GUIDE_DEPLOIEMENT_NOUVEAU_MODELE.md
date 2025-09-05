# 🚀 Guide de Déploiement du Nouveau Modèle CLIP

## 📋 Prérequis

### 1. Fichiers nécessaires
- ✅ `new_clip_product_classifier.pth` (1.2 GB) - Votre nouveau modèle
- ✅ `.env_azure_production` - Configuration Azure
- ✅ Compte Azure ML configuré

### 2. Variables d'environnement Azure
```bash
AZURE_SUBSCRIPTION_ID=votre_subscription_id
AZURE_RESOURCE_GROUP=votre_resource_group
AZURE_WORKSPACE_NAME=votre_workspace_name
```

## 🔧 Déploiement

### Option 1: Script automatique (Recommandé)
```bash
./deploy_new_model_simple.sh
```

### Option 2: Déploiement manuel
```bash
# 1. Installer les dépendances
pip install azure-ai-ml azure-identity python-dotenv

# 2. Lancer le déploiement
python deploy_new_model.py
```

## 📊 Optimisations pour économiser les crédits

### 1. Configuration minimale
- **Instance:** `Standard_DS2_v2` (2 vCPU, 7 GB RAM)
- **Scaling:** 0-1 instance (arrêt automatique)
- **Timeout:** 30 secondes

### 2. Monitoring des coûts
```bash
# Vérifier l'état de l'endpoint
az ml online-endpoint show --name clip-classifier-endpoint --resource-group votre_rg

# Arrêter l'endpoint si nécessaire
az ml online-endpoint delete --name clip-classifier-endpoint --resource-group votre_rg
```

### 3. Stratégies d'économie
- **Mode démonstration:** Garder le mode local pour les tests
- **Déploiement à la demande:** Déployer seulement pour les démonstrations
- **Monitoring:** Surveiller les coûts dans le portail Azure

## 🎯 Résultat attendu

### 1. Endpoint créé
- **Nom:** `clip-classifier-endpoint`
- **URL:** `https://clip-classifier-endpoint.region.inference.ml.azure.com/score`
- **État:** `Succeeded`

### 2. Variables mises à jour
Le fichier `.env_azure_production` sera mis à jour avec :
```bash
AZURE_ML_ENDPOINT_URL=https://clip-classifier-endpoint.region.inference.ml.azure.com/score
AZURE_ML_API_KEY=votre_cle_api
```

### 3. Configuration Streamlit
Mettre à jour les secrets Streamlit Cloud avec les nouvelles valeurs.

## 🔍 Vérification

### 1. Test de l'endpoint
```python
import requests
import base64
from PIL import Image
import io

# Charger une image de test
image = Image.open("Images/1120bc768623572513df956172ffefeb.jpg")
buffer = io.BytesIO()
image.save(buffer, format='JPEG')
image_data = base64.b64encode(buffer.getvalue()).decode()

# Tester l'endpoint
response = requests.post(
    "VOTRE_ENDPOINT_URL",
    headers={"Authorization": "Bearer VOTRE_CLE_API"},
    json={
        "image": image_data,
        "text": "Escort E-1700-906_Blk Analog Watch - For Men, Boys"
    }
)

print(response.json())
```

### 2. Vérification des coûts
- Portail Azure > Machine Learning > Endpoints
- Surveiller la consommation en temps réel
- Configurer des alertes de coût

## ⚠️ Gestion des coûts

### 1. Arrêt automatique
- L'endpoint s'arrête automatiquement après 30 minutes d'inactivité
- Redémarrage automatique lors de la première requête

### 2. Monitoring
```bash
# Vérifier l'état
az ml online-endpoint show --name clip-classifier-endpoint

# Voir les métriques
az ml online-endpoint get-logs --name clip-classifier-endpoint
```

### 3. Suppression si nécessaire
```bash
# Supprimer l'endpoint (arrête tous les coûts)
az ml online-endpoint delete --name clip-classifier-endpoint --resource-group votre_rg
```

## 🎯 Prochaines étapes

1. **Déployer le modèle** avec le script
2. **Tester l'endpoint** avec une image de test
3. **Mettre à jour Streamlit** avec les nouvelles clés
4. **Surveiller les coûts** dans Azure
5. **Configurer des alertes** de coût si nécessaire

## 📞 Support

En cas de problème :
1. Vérifier les logs Azure ML
2. Contrôler les variables d'environnement
3. Vérifier les permissions Azure
4. Consulter la documentation Azure ML
