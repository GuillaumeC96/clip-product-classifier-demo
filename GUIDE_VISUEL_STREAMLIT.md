# 🚀 Guide Visuel - Déploiement Streamlit Cloud

## 📋 **Étapes détaillées avec captures d'écran**

### **Étape 1 : Créer le dépôt GitHub**

1. **Allez sur GitHub.com**
   - 🌐 Ouvrez https://github.com
   - 🔐 Connectez-vous avec votre compte

2. **Créer un nouveau dépôt**
   - ➕ Cliquez sur le bouton vert **"New"** ou **"New repository"**
   - 📝 **Repository name** : `clip-product-classifier`
   - 📝 **Description** : `Application CLIP pour classification de produits`
   - 🌍 **Public** (obligatoire pour Streamlit Cloud gratuit)
   - ✅ **Cochez** "Add a README file"
   - 🚀 Cliquez **"Create repository"**

3. **Copier l'URL**
   - 📋 Copiez l'URL qui ressemble à : `https://github.com/votre-username/clip-product-classifier.git`

### **Étape 2 : Connecter le code local**

1. **Exécuter le script**
   ```bash
   ./connect_github_final.sh
   ```

2. **Entrer l'URL du dépôt**
   - 📝 Collez l'URL que vous avez copiée
   - ⏳ Attendez que le code soit poussé

### **Étape 3 : Déployer sur Streamlit Cloud**

1. **Aller sur Streamlit Cloud**
   - 🌐 Ouvrez https://share.streamlit.io
   - 🔐 Connectez-vous avec votre compte GitHub

2. **Créer une nouvelle app**
   - ➕ Cliquez sur **"New app"**
   - 📁 **Repository** : Sélectionnez `clip-product-classifier`
   - 📄 **Branch** : `main`
   - 📄 **Main file path** : `accueil_cloud.py`
   - 🌐 **App URL** : `clip-product-classifier` (ou votre choix)

3. **Configuration avancée (optionnel)**
   - 🔧 Cliquez sur **"Advanced settings"**
   - 🐍 **Python version** : `3.9`
   - 📦 **Requirements file** : `requirements.txt`

4. **Déployer**
   - 🚀 Cliquez sur **"Deploy!"**
   - ⏳ Attendez 5-10 minutes

### **Étape 4 : Accéder à votre application**

1. **URL finale**
   - 🌐 Votre app sera accessible à : `https://clip-product-classifier.streamlit.app`
   - 🔒 **HTTPS automatique**
   - 🌍 **Accessible depuis n'importe où**

2. **Tester l'application**
   - 📱 Ouvrez l'URL dans votre navigateur
   - ✅ Testez toutes les fonctionnalités
   - 🔍 Vérifiez les logs en cas d'erreur

## 🎯 **Résultat final**

- ✅ **Application accessible depuis n'importe où**
- ✅ **HTTPS sécurisé**
- ✅ **URL permanente**
- ✅ **Gratuit**
- ✅ **Hébergé par Streamlit**

## 🔧 **Gestion des mises à jour**

Pour mettre à jour votre application :
```bash
git add .
git commit -m "Mise à jour"
git push origin main
```

Streamlit Cloud redéploiera automatiquement !

## 🆘 **Dépannage**

### Problème : "App not found"
- ✅ Vérifiez que le dépôt est **public**
- ✅ Vérifiez que le fichier principal est `accueil_cloud.py`

### Problème : "Requirements not found"
- ✅ Vérifiez que `requirements.txt` existe
- ✅ Vérifiez le contenu du fichier

### Problème : "Import error"
- ✅ Vérifiez que tous les modules sont dans `requirements.txt`
- ✅ Vérifiez les imports dans le code

---

**🎉 Félicitations ! Votre application CLIP est maintenant accessible depuis n'importe où dans le monde !**
