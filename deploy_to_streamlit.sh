#!/bin/bash

# Script de déploiement pour Streamlit Cloud
echo "🚀 Déploiement de l'application CLIP sur Streamlit Cloud"
echo "=================================================="

# Vérifier que nous sommes dans un repository Git
if [ ! -d ".git" ]; then
    echo "❌ Ce n'est pas un repository Git"
    echo "Exécutez d'abord: git init"
    exit 1
fi

# Vérifier que le code est commité
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️ Des fichiers non commités détectés"
    echo "Voulez-vous les commiter maintenant ? (y/n)"
    read -r response
    if [ "$response" = "y" ] || [ "$response" = "Y" ]; then
        git add .
        git commit -m "Mise à jour avant déploiement Streamlit Cloud"
    else
        echo "❌ Veuillez commiter vos changements avant le déploiement"
        exit 1
    fi
fi

echo "✅ Code prêt pour le déploiement"

# Vérifier la configuration
echo "🔍 Vérification de la configuration..."

if [ ! -f "accueil_cloud.py" ]; then
    echo "❌ Fichier accueil_cloud.py manquant"
    exit 1
fi

if [ ! -f "requirements.txt" ]; then
    echo "❌ Fichier requirements.txt manquant"
    exit 1
fi

if [ ! -f ".streamlit/secrets.toml" ]; then
    echo "❌ Fichier .streamlit/secrets.toml manquant"
    exit 1
fi

echo "✅ Configuration validée"

# Instructions pour GitHub
echo ""
echo "📋 Prochaines étapes :"
echo "1. Créer un repository sur GitHub :"
echo "   - Nom : clip-product-classifier"
echo "   - Visibilité : Public"
echo "   - Description : Application de classification de produits avec CLIP"
echo ""
echo "2. Pousser le code :"
echo "   git remote add origin https://github.com/VOTRE_USERNAME/clip-product-classifier.git"
echo "   git push -u origin main"
echo ""
echo "3. Déployer sur Streamlit Cloud :"
echo "   - Aller sur https://share.streamlit.io/"
echo "   - Se connecter avec GitHub"
echo "   - Cliquer sur 'New app'"
echo "   - Repository : VOTRE_USERNAME/clip-product-classifier"
echo "   - Branch : main"
echo "   - Main file path : accueil_cloud.py"
echo ""
echo "4. Votre application sera accessible sur :"
echo "   https://clip-product-classifier.streamlit.app"
echo ""
echo "🎉 Déploiement prêt !"
