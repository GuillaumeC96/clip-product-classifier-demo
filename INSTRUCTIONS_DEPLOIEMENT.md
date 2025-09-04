# 🚀 Instructions de Déploiement - Application CLIP

## 🎯 Créer votre propre application Streamlit Cloud

Vous devez créer votre propre application car vous n'avez pas accès à l'application existante.

## 📋 Étapes détaillées

### 1️⃣ **Créer un repository GitHub**

1. **Aller sur [GitHub](https://github.com)**
2. **Cliquer sur "New repository" (bouton vert)**
3. **Configurer le repository** :
   - **Repository name** : `clip-product-classifier`
   - **Description** : `Application de classification de produits avec CLIP`
   - **Visibilité** : ✅ **Public** (obligatoire pour Streamlit Cloud gratuit)
   - **Ne pas** cocher "Add a README file" (nous en avons déjà un)
4. **Cliquer sur "Create repository"**

### 2️⃣ **Connecter votre repository local à GitHub**

```bash
# Dans le terminal, dans le dossier de votre application
git remote add origin https://github.com/guillaumec96/clip-product-classifier.git
git branch -M main
git push -u origin main
```

### 3️⃣ **Déployer sur Streamlit Cloud**

1. **Aller sur [Streamlit Cloud](https://share.streamlit.io/)**
2. **Se connecter avec votre compte GitHub** (`guillaumec96`)
3. **Cliquer sur "New app"**
4. **Configurer le déploiement** :
   - **Repository** : `guillaumec96/clip-product-classifier`
   - **Branch** : `main`
   - **Main file path** : `accueil_cloud.py`
   - **App URL** : `clip-product-classifier` (optionnel)
5. **Cliquer sur "Deploy!"**

### 4️⃣ **Attendre le déploiement**

- Le déploiement prend 2-5 minutes
- Vous verrez les logs en temps réel
- Une fois terminé, vous aurez une URL comme : `https://clip-product-classifier.streamlit.app`

## 🔧 Configuration automatique

Votre application est déjà configurée pour fonctionner automatiquement :

- ✅ **Mode local activé** : Pas besoin d'Azure ML
- ✅ **Dépendances installées** : Toutes dans `requirements.txt`
- ✅ **Modèle spaCy** : Téléchargé automatiquement
- ✅ **Interface accessible** : Options d'accessibilité incluses

## 🌐 Accès à votre application

Une fois déployée, votre application sera accessible publiquement sur :
`https://clip-product-classifier.streamlit.app`

## 📱 Partage

Vous pourrez partager cette URL avec n'importe qui dans le monde !

## 🆘 En cas de problème

### Erreur de déploiement
- Vérifier que le repository est **public**
- Vérifier que `accueil_cloud.py` existe
- Consulter les logs de déploiement

### Erreur d'accès
- Vérifier que vous êtes connecté avec le bon compte GitHub
- Vérifier que le repository appartient à votre compte

## 🎉 Résultat attendu

Votre application sera :
- ✅ **Publiquement accessible** sur le web
- ✅ **Gratuite** à héberger
- ✅ **Automatiquement mise à jour** lors des modifications
- ✅ **Partageable** avec d'autres personnes

---

**🚀 Suivez ces étapes pour créer votre propre application CLIP !**
