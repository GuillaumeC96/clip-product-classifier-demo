#!/bin/bash

echo "🔗 Connexion finale à GitHub pour Streamlit Cloud"
echo "================================================="
echo ""

# Vérifier que nous sommes dans le bon répertoire
if [ ! -f "accueil_cloud.py" ]; then
    echo "❌ Erreur : accueil_cloud.py non trouvé"
    exit 1
fi

echo "✅ Fichiers de déploiement vérifiés"
echo ""

# Demander l'URL du dépôt GitHub
echo "🌐 Configuration du dépôt GitHub"
echo "================================"
echo ""
echo "📋 Si vous n'avez pas encore créé le dépôt :"
echo "1. Allez sur https://github.com"
echo "2. Créez un nouveau dépôt PUBLIC nommé 'clip-product-classifier'"
echo "3. Copiez l'URL du dépôt"
echo ""

read -p "🔗 Entrez l'URL de votre dépôt GitHub : " GITHUB_URL

if [ -z "$GITHUB_URL" ]; then
    echo "❌ URL GitHub requise"
    exit 1
fi

echo ""
echo "🔗 Connexion au dépôt GitHub..."

# Supprimer l'ancien remote s'il existe
git remote remove origin 2>/dev/null

# Ajouter le nouveau remote
git remote add origin "$GITHUB_URL"

# Pousser le code
echo "📤 Poussée du code vers GitHub..."
git branch -M main
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Code poussé avec succès vers GitHub !"
    echo ""
    echo "🌐 PROCHAINES ÉTAPES POUR STREAMLIT CLOUD :"
    echo "==========================================="
    echo ""
    echo "1️⃣ Allez sur : https://share.streamlit.io"
    echo "2️⃣ Connectez-vous avec votre compte GitHub"
    echo "3️⃣ Cliquez sur 'New app'"
    echo "4️⃣ Sélectionnez votre dépôt : clip-product-classifier"
    echo "5️⃣ Main file path : accueil_cloud.py"
    echo "6️⃣ App URL : clip-product-classifier (ou votre choix)"
    echo "7️⃣ Cliquez sur 'Deploy!'"
    echo ""
    echo "⏳ Temps de déploiement : 5-10 minutes"
    echo ""
    echo "🎉 Votre application sera accessible à :"
    echo "   https://clip-product-classifier.streamlit.app"
    echo ""
    echo "🌍 Accessible depuis n'importe où dans le monde !"
else
    echo ""
    echo "❌ Erreur lors de la poussée vers GitHub"
    echo "Vérifiez que :"
    echo "- Le dépôt GitHub existe et est public"
    echo "- Vous avez les permissions"
    echo "- L'URL est correcte"
fi
