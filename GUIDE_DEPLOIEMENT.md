# 🚀 Guide de Déploiement Cloud - Classification de Produits CLIP

## 📋 Résumé

Votre application Streamlit a été préparée pour le déploiement cloud avec :
- **Frontend** : Streamlit Cloud
- **Backend** : Azure ML pour l'inférence
- **Modèle** : CLIP fine-tuné pour la classification de produits

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit     │    │   Azure ML      │    │   Modèle CLIP   │
│   Cloud         │◄──►│   Endpoint      │◄──►│   Fine-tuné     │
│   (Frontend)    │    │   (Backend)     │    │   (Inference)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 Fichiers créés

### 🔧 Configuration Azure ML
- `azure_ml_api/score.py` - Script de scoring pour Azure ML
- `azure_ml_api/deploy_model.py` - Script de déploiement
- `azure_ml_api/requirements.txt` - Dépendances Azure ML
- `azure_ml_api/env_example.txt` - Exemple de configuration

### 🌐 Application Streamlit Cloud
- `accueil_cloud.py` - Point d'entrée principal (version cloud)
- `pages/2_prediction_cloud.py` - Page de prédiction (version cloud)
- `azure_client.py` - Client pour l'API Azure ML
- `requirements_cloud.txt` - Dépendances Streamlit Cloud

### ⚙️ Configuration
- `.streamlit/config.toml` - Configuration Streamlit
- `.streamlit/secrets.toml.example` - Exemple de secrets
- `.gitignore` - Fichiers à ignorer

### 📚 Documentation et scripts
- `README_CLOUD.md` - Documentation complète
- `deploy_azure.sh` - Script de déploiement Azure
- `test_cloud_deployment.py` - Script de test
- `GUIDE_DEPLOIEMENT.md` - Ce guide

## 🚀 Étapes de déploiement

### 1️⃣ Préparation

```bash
# Installer les dépendances locales (optionnel)
pip install -r requirements_cloud.txt

# Tester la configuration
python3 test_cloud_deployment.py
```

### 2️⃣ Déploiement Azure ML

```bash
# Configurer les variables d'environnement
export AZURE_SUBSCRIPTION_ID="your_subscription_id"
export AZURE_RESOURCE_GROUP="ml-resource-group"
export AZURE_WORKSPACE_NAME="clip-classification-workspace"

# Déployer le modèle
./deploy_azure.sh
```

### 3️⃣ Configuration des secrets

Récupérer depuis le portail Azure ML :
- **URL de l'endpoint** : `https://your-endpoint.westeurope.inference.ml.azure.com/score`
- **Clé API** : Clé d'authentification

### 4️⃣ Déploiement Streamlit Cloud

1. **Pousser le code sur GitHub** :
```bash
git init
git add .
git commit -m "Cloud deployment ready"
git remote add origin https://github.com/yourusername/your-repo.git
git push -u origin main
```

2. **Déployer sur Streamlit Cloud** :
   - Aller sur [share.streamlit.io](https://share.streamlit.io/)
   - Connecter le repository GitHub
   - Choisir `accueil_cloud.py` comme fichier principal
   - Configurer les secrets :
     ```toml
     AZURE_ML_ENDPOINT_URL = "https://your-endpoint.westeurope.inference.ml.azure.com/score"
     AZURE_ML_API_KEY = "your_api_key_here"
     USE_LOCAL_MODEL = false
     ```

## 🔄 Modes de fonctionnement

### Mode Cloud (recommandé)
- ✅ Inférence sur Azure ML
- ✅ Scalabilité automatique
- ✅ Haute disponibilité
- ✅ Monitoring intégré

### Mode Local (fallback)
- ✅ Fonctionnement hors ligne
- ✅ Développement local
- ⚠️ Limité par les ressources locales

## 🧪 Test de l'application

### Test local
```bash
# Lancer l'application locale
streamlit run accueil_cloud.py
```

### Test de l'API Azure ML
```bash
# Tester le client Azure ML
python3 test_cloud_deployment.py
```

## 📊 Monitoring

### Azure ML
- **Métriques** : Portail Azure ML
- **Logs** : Application Insights
- **Coûts** : Facturation basée sur l'utilisation

### Streamlit Cloud
- **Logs** : Interface Streamlit Cloud
- **Métriques** : Utilisateurs, temps de réponse
- **Coûts** : Gratuit pour les applications publiques

## 🔧 Dépannage

### Problèmes courants

1. **Erreur de connexion Azure ML** :
   - Vérifier l'URL de l'endpoint
   - Vérifier la clé API
   - Vérifier le statut du service

2. **Timeout de l'API** :
   - Augmenter le timeout dans `azure_client.py`
   - Vérifier la charge du service

3. **Erreur de déploiement Streamlit** :
   - Vérifier les secrets
   - Vérifier les dépendances

### Logs utiles

```python
# Dans azure_client.py
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

## 💰 Coûts estimés

### Azure ML
- **ACI** : ~0.10€/heure
- **Stockage** : ~0.02€/GB/mois
- **Réseau** : ~0.05€/GB

### Streamlit Cloud
- **Gratuit** pour les applications publiques
- **Pro** : 20$/mois pour les applications privées

## 🔒 Sécurité

- ✅ HTTPS obligatoire
- ✅ Authentification par clé API
- ✅ Secrets gérés par Streamlit Cloud
- ✅ Isolation des conteneurs Azure

## 📞 Support

Pour toute question :
1. Vérifier les logs Azure ML
2. Vérifier les logs Streamlit Cloud
3. Consulter la documentation Azure ML
4. Consulter la documentation Streamlit Cloud

## 🎯 Prochaines étapes

1. **Déployer le modèle sur Azure ML** avec `./deploy_azure.sh`
2. **Configurer les secrets** dans Streamlit Cloud
3. **Déployer l'application** Streamlit
4. **Tester l'application** déployée
5. **Monitorer** les performances et les coûts

---

**🎉 Félicitations !** Votre application est prête pour le déploiement cloud. Suivez les étapes ci-dessus pour la déployer sur Azure ML et Streamlit Cloud.
