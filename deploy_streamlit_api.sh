#!/bin/bash

echo "🚀 Déploiement automatique sur Streamlit Cloud"
echo "=============================================="
echo ""

# Vérifier que nous sommes dans le bon répertoire
if [ ! -f "accueil_cloud.py" ]; then
    echo "❌ Erreur : accueil_cloud.py non trouvé"
    exit 1
fi

echo "✅ Fichiers de déploiement vérifiés"
echo ""

# Demander les informations
echo "🔐 Configuration pour Streamlit Cloud"
echo "===================================="
echo ""

read -p "👤 Votre nom d'utilisateur GitHub : " GITHUB_USERNAME

if [ -z "$GITHUB_USERNAME" ]; then
    echo "❌ Nom d'utilisateur GitHub requis"
    exit 1
fi

echo ""
echo "🔑 Token d'accès personnel GitHub"
echo "Pour créer un token :"
echo "1. Allez sur https://github.com/settings/tokens"
echo "2. Cliquez 'Generate new token' > 'Generate new token (classic)'"
echo "3. Nom : 'Streamlit Cloud Deployment'"
echo "4. Cochez 'repo' (accès complet aux dépôts)"
echo "5. Cliquez 'Generate token'"
echo "6. Copiez le token"
echo ""

read -p "🔑 Votre token GitHub : " GITHUB_TOKEN

if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ Token GitHub requis"
    exit 1
fi

echo ""
echo "🔗 Création du dépôt GitHub..."

# Créer le dépôt via l'API GitHub
REPO_NAME="clip-product-classifier"
REPO_URL="https://api.github.com/user/repos"

# Créer le dépôt
echo "📦 Création du dépôt '$REPO_NAME'..."
curl -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  "$REPO_URL" \
  -d "{
    \"name\": \"$REPO_NAME\",
    \"description\": \"Application CLIP pour classification de produits\",
    \"private\": false,
    \"auto_init\": false
  }" > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Dépôt GitHub créé avec succès !"
else
    echo "⚠️ Le dépôt existe peut-être déjà, continuons..."
fi

echo ""
echo "🔗 Connexion au dépôt GitHub..."

# Supprimer l'ancien remote s'il existe
git remote remove origin 2>/dev/null

# Ajouter le nouveau remote
git remote add origin "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"

# Pousser le code
echo "📤 Poussée du code vers GitHub..."
git branch -M main
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Code poussé avec succès vers GitHub !"
    echo ""
    echo "🌐 DÉPLOIEMENT SUR STREAMLIT CLOUD"
    echo "=================================="
    echo ""
    echo "🔗 Votre dépôt GitHub :"
    echo "   https://github.com/$GITHUB_USERNAME/$REPO_NAME"
    echo ""
    echo "📋 Étapes pour Streamlit Cloud :"
    echo "1. Allez sur : https://share.streamlit.io"
    echo "2. Connectez-vous avec votre compte GitHub"
    echo "3. Cliquez sur 'New app'"
    echo "4. Sélectionnez votre dépôt : $REPO_NAME"
    echo "5. Main file path : accueil_cloud.py"
    echo "6. App URL : $REPO_NAME (ou votre choix)"
    echo "7. Cliquez sur 'Deploy!'"
    echo ""
    echo "⏳ Temps de déploiement : 5-10 minutes"
    echo ""
    echo "🎉 Votre application sera accessible à :"
    echo "   https://$REPO_NAME.streamlit.app"
    echo ""
    echo "🌍 Accessible depuis n'importe où dans le monde !"
    echo ""
    echo "🔗 Ouverture automatique du navigateur..."
    
    # Ouvrir le navigateur sur Streamlit Cloud
    if command -v xdg-open > /dev/null; then
        xdg-open "https://share.streamlit.io"
    elif command -v open > /dev/null; then
        open "https://share.streamlit.io"
    else
        echo "🌐 Ouvrez manuellement : https://share.streamlit.io"
    fi
else
    echo ""
    echo "❌ Erreur lors de la poussée vers GitHub"
    echo "Vérifiez que :"
    echo "- Le token GitHub est valide"
    echo "- Vous avez les permissions"
    echo "- L'URL est correcte"
fi
