#!/bin/bash

echo "🚀 Déploiement du nouveau modèle CLIP"
echo "====================================="

# Vérifier que le modèle existe
if [ ! -f "new_clip_product_classifier.pth" ]; then
    echo "❌ Modèle non trouvé: new_clip_product_classifier.pth"
    exit 1
fi

echo "✅ Modèle trouvé: new_clip_product_classifier.pth"
echo "📊 Taille: $(du -h new_clip_product_classifier.pth | cut -f1)"

# Vérifier les variables d'environnement
if [ ! -f ".env_azure_production" ]; then
    echo "❌ Fichier .env_azure_production non trouvé"
    echo "💡 Créez d'abord le fichier avec vos informations Azure"
    exit 1
fi

echo "✅ Fichier .env_azure_production trouvé"

# Installer les dépendances si nécessaire
echo "📦 Vérification des dépendances..."
pip install azure-ai-ml azure-identity python-dotenv

# Lancer le déploiement
echo "🚀 Lancement du déploiement..."
python deploy_new_model.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Déploiement terminé avec succès!"
    echo "🔗 Vérifiez l'URL de l'endpoint dans .env_azure_production"
    echo "📝 Mettez à jour les secrets Streamlit Cloud avec les nouvelles clés"
else
    echo "❌ Erreur lors du déploiement"
    exit 1
fi
