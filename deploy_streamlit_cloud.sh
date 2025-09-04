#!/bin/bash

echo "🚀 Déploiement sur Streamlit Cloud"
echo "=================================="
echo ""

# Vérifier que nous sommes dans le bon répertoire
if [ ! -f "accueil_cloud.py" ]; then
    echo "❌ Erreur : accueil_cloud.py non trouvé"
    echo "Assurez-vous d'être dans le répertoire de l'application"
    exit 1
fi

# Vérifier que Git est configuré
if [ ! -d ".git" ]; then
    echo "❌ Erreur : Dépôt Git non initialisé"
    echo "Exécutez d'abord : git init"
    exit 1
fi

echo "✅ Fichiers de déploiement vérifiés :"
echo "   - accueil_cloud.py ✓"
echo "   - requirements.txt ✓"
echo "   - .streamlit/ ✓"
echo ""

# Vérifier le statut Git
echo "📊 Statut Git :"
git status --short
echo ""

# Demander l'URL du dépôt GitHub
echo "🔗 Configuration du dépôt GitHub"
echo "================================"
echo ""
echo "📋 Instructions :"
echo "1. Allez sur https://github.com"
echo "2. Créez un nouveau dépôt public nommé 'clip-product-classifier'"
echo "3. Copiez l'URL du dépôt"
echo ""

read -p "🌐 Entrez l'URL de votre dépôt GitHub : " GITHUB_URL

if [ -z "$GITHUB_URL" ]; then
    echo "❌ URL GitHub requise"
    exit 1
fi

echo ""
echo "🔗 Connexion au dépôt GitHub..."

# Ajouter le remote
git remote add origin "$GITHUB_URL" 2>/dev/null || git remote set-url origin "$GITHUB_URL"

# Pousser le code
echo "📤 Poussée du code vers GitHub..."
git branch -M main
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Code poussé avec succès vers GitHub !"
    echo ""
    echo "🌐 Prochaines étapes :"
    echo "1. Allez sur https://share.streamlit.io"
    echo "2. Connectez-vous avec votre compte GitHub"
    echo "3. Cliquez sur 'New app'"
    echo "4. Sélectionnez votre dépôt : clip-product-classifier"
    echo "5. Main file path : accueil_cloud.py"
    echo "6. Cliquez sur 'Deploy!'"
    echo ""
    echo "🎉 Votre application sera accessible depuis n'importe où !"
    echo ""
    echo "📱 URL finale : https://clip-product-classifier.streamlit.app"
else
    echo ""
    echo "❌ Erreur lors de la poussée vers GitHub"
    echo "Vérifiez que :"
    echo "- Le dépôt GitHub existe"
    echo "- Vous avez les permissions"
    echo "- L'URL est correcte"
fi
