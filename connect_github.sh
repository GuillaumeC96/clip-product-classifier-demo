#!/bin/bash

# Script pour connecter le repository local à GitHub
echo "🔗 Connexion du repository local à GitHub"
echo "========================================"

# Vérifier que nous sommes dans un repository Git
if [ ! -d ".git" ]; then
    echo "❌ Ce n'est pas un repository Git"
    exit 1
fi

# Vérifier si un remote existe déjà
if git remote get-url origin >/dev/null 2>&1; then
    echo "⚠️ Un remote 'origin' existe déjà :"
    git remote get-url origin
    echo "Voulez-vous le remplacer ? (y/n)"
    read -r response
    if [ "$response" = "y" ] || [ "$response" = "Y" ]; then
        git remote remove origin
    else
        echo "❌ Connexion annulée"
        exit 1
    fi
fi

# Ajouter le remote GitHub
echo "🔗 Ajout du remote GitHub..."
git remote add origin https://github.com/guillaumec96/clip-product-classifier.git

# Vérifier la connexion
echo "🔍 Vérification de la connexion..."
if git remote get-url origin >/dev/null 2>&1; then
    echo "✅ Remote ajouté avec succès :"
    git remote get-url origin
else
    echo "❌ Erreur lors de l'ajout du remote"
    exit 1
fi

# Pousser le code
echo "📤 Poussée du code vers GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Succès ! Votre code est maintenant sur GitHub"
    echo ""
    echo "📋 Prochaines étapes :"
    echo "1. Aller sur https://share.streamlit.io/"
    echo "2. Se connecter avec GitHub"
    echo "3. Cliquer sur 'New app'"
    echo "4. Repository : guillaumec96/clip-product-classifier"
    echo "5. Branch : main"
    echo "6. Main file path : accueil_cloud.py"
    echo "7. Déployer !"
    echo ""
    echo "🌐 Votre application sera accessible sur :"
    echo "https://clip-product-classifier.streamlit.app"
else
    echo "❌ Erreur lors de la poussée vers GitHub"
    echo "Vérifiez que le repository GitHub existe et que vous avez les permissions"
fi
