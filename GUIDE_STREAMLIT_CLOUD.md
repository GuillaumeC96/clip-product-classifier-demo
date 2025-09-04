# 🌐 Guide de Déploiement Streamlit Cloud - Application CLIP

## 🎯 Objectif

Déployer votre application de classification de produits CLIP sur Streamlit Cloud pour qu'elle soit accessible publiquement sur le web.

## ✅ Prérequis

- ✅ Repository Git initialisé
- ✅ Code commité
- ✅ Application testée localement
- ✅ Configuration Streamlit Cloud prête

## 🚀 Étapes de déploiement

### 1️⃣ **Créer un repository GitHub**

```bash
# Créer un nouveau repository sur GitHub
# Nom suggéré : clip-product-classifier
# Description : Application de classification de produits avec CLIP
# Visibilité : Public (pour Streamlit Cloud gratuit)
```

### 2️⃣ **Pousser le code sur GitHub**

```bash
# Ajouter le remote GitHub
git remote add origin https://github.com/VOTRE_USERNAME/clip-product-classifier.git

# Pousser le code
git push -u origin main
```

### 3️⃣ **Déployer sur Streamlit Cloud**

1. **Aller sur [Streamlit Cloud](https://share.streamlit.io/)**
2. **Se connecter avec GitHub**
3. **Cliquer sur "New app"**
4. **Configurer le déploiement** :
   - **Repository** : `VOTRE_USERNAME/clip-product-classifier`
   - **Branch** : `main`
   - **Main file path** : `accueil_cloud.py`
   - **App URL** : `clip-product-classifier` (optionnel)

### 4️⃣ **Configuration des secrets (optionnel)**

Si vous voulez utiliser Azure ML plus tard :
```toml
AZURE_ML_ENDPOINT_URL = "https://your-endpoint.westeurope.inference.ml.azure.com/score"
AZURE_ML_API_KEY = "your_api_key_here"
USE_LOCAL_MODEL = false
```

## 🌐 Accès à l'application

Une fois déployée, l'application sera accessible via :
`https://clip-product-classifier.streamlit.app`

## 🔧 Configuration automatique

L'application est configurée pour fonctionner automatiquement :

### ✅ **Mode local activé**
- `USE_LOCAL_MODEL = true` dans `.streamlit/secrets.toml`
- Modèle CLIP pré-entraîné utilisé
- Pas besoin d'Azure ML

### ✅ **Dépendances installées**
- Toutes les dépendances dans `requirements.txt`
- Modèle spaCy téléchargé automatiquement
- PyTorch et Transformers inclus

### ✅ **Interface accessible**
- Options d'accessibilité activées
- Mode contraste élevé
- Mode daltonien
- Texte agrandi

## 📊 Fonctionnalités disponibles

- **🏠 Page d'accueil** : Présentation de l'application
- **📊 EDA** : Analyse exploratoire des données
- **🔮 Prédiction** : Classification de produits
- **👁️ Accessibilité** : Options d'accessibilité

## 🧪 Test de l'application déployée

1. **Accéder à l'URL** de votre application
2. **Tester la page d'accueil**
3. **Naviguer vers la prédiction**
4. **Uploader une image de test**
5. **Vérifier la prédiction**

## 🔄 Mise à jour de l'application

Pour mettre à jour l'application :

```bash
# Modifier le code
# Commiter les changements
git add .
git commit -m "Mise à jour de l'application"
git push origin main

# Streamlit Cloud redéploiera automatiquement
```

## 📱 Partage de l'application

Une fois déployée, vous pouvez partager l'URL avec d'autres personnes :
- **URL publique** : `https://clip-product-classifier.streamlit.app`
- **Accès gratuit** : Aucune authentification requise
- **Compatible mobile** : Interface responsive

## 🆘 Dépannage

### Problèmes courants

1. **Erreur de déploiement** :
   - Vérifier que `accueil_cloud.py` existe
   - Vérifier que `requirements.txt` est présent
   - Consulter les logs de déploiement

2. **Erreur d'import** :
   - Vérifier que toutes les dépendances sont dans `requirements.txt`
   - Vérifier que le modèle spaCy est téléchargé

3. **Application lente** :
   - Normal au premier lancement (téléchargement des modèles)
   - Les lancements suivants seront plus rapides

### Logs de déploiement

- Aller sur Streamlit Cloud
- Cliquer sur votre application
- Onglet "Logs" pour voir les erreurs

## 💰 Coûts

- **Streamlit Cloud** : Gratuit pour les applications publiques
- **Limitations** : 
  - 1 CPU par application
  - 1 GB de RAM
  - 1 GB de stockage
  - Applications publiques uniquement

## 🎉 Résultat attendu

Une fois déployée, votre application sera :
- ✅ **Accessible publiquement** sur le web
- ✅ **Fonctionnelle** avec toutes les features
- ✅ **Gratuite** à héberger
- ✅ **Automatiquement mise à jour** lors des push Git

---

**🚀 Votre application CLIP sera bientôt accessible à tous sur le web !**
