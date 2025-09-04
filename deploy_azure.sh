#!/bin/bash

# Script de déploiement Azure ML
echo "🚀 Déploiement du modèle CLIP sur Azure ML..."

# Vérifier les variables d'environnement
if [ -z "$AZURE_SUBSCRIPTION_ID" ]; then
    echo "❌ AZURE_SUBSCRIPTION_ID n'est pas défini"
    echo "Définissez-le avec: export AZURE_SUBSCRIPTION_ID='your_subscription_id'"
    exit 1
fi

if [ -z "$AZURE_RESOURCE_GROUP" ]; then
    echo "⚠️ AZURE_RESOURCE_GROUP non défini, utilisation de la valeur par défaut"
    export AZURE_RESOURCE_GROUP="ml-resource-group"
fi

if [ -z "$AZURE_WORKSPACE_NAME" ]; then
    echo "⚠️ AZURE_WORKSPACE_NAME non défini, utilisation de la valeur par défaut"
    export AZURE_WORKSPACE_NAME="clip-classification-workspace"
fi

# Aller dans le dossier Azure ML
cd azure_ml_api

# Installer les dépendances
echo "📦 Installation des dépendances..."
pip install -r requirements.txt

# Vérifier que le modèle existe
if [ ! -f "../clip_product_classifier.pth" ]; then
    echo "⚠️ Le fichier clip_product_classifier.pth n'existe pas"
    echo "Le modèle utilisera les poids pré-entraînés"
fi

# Déployer le modèle
echo "🔧 Déploiement du modèle..."
python deploy_model.py

if [ $? -eq 0 ]; then
    echo "✅ Déploiement réussi!"
    echo ""
    echo "📋 Prochaines étapes:"
    echo "1. Récupérer l'URL de l'endpoint depuis le portail Azure ML"
    echo "2. Récupérer la clé API depuis le portail Azure ML"
    echo "3. Configurer les secrets dans Streamlit Cloud"
    echo "4. Déployer l'application Streamlit"
else
    echo "❌ Erreur lors du déploiement"
    exit 1
fi
