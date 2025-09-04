#!/bin/bash

# Script pour lancer l'application CLIP dans le navigateur
echo "🚀 Lancement de l'application CLIP"
echo "=================================="

# Activer l'environnement virtuel
echo "🔧 Activation de l'environnement virtuel..."
source clip_cloud_env/bin/activate

# Vérifier si Streamlit est déjà en cours d'exécution
if pgrep -f "streamlit run accueil_cloud.py" > /dev/null; then
    echo "✅ Application déjà en cours d'exécution"
    echo "🌐 URL : http://localhost:8502"
else
    echo "🔄 Lancement de l'application Streamlit..."
    streamlit run accueil_cloud.py --server.port 8502 --server.headless true &
    sleep 3
    echo "✅ Application lancée"
fi

# Ouvrir dans le navigateur
echo "🌐 Ouverture dans le navigateur..."
xdg-open http://localhost:8502 2>/dev/null || firefox http://localhost:8502 2>/dev/null || echo "Ouvrez manuellement : http://localhost:8502"

echo ""
echo "🎉 Application accessible sur :"
echo "   - Local : http://localhost:8502"
echo "   - Réseau : http://192.168.1.75:8502"
echo "   - Externe : http://81.250.56.141:8502"
echo ""
echo "📱 Fonctionnalités disponibles :"
echo "   - 🏠 Page d'accueil"
echo "   - 📊 Analyse des données (EDA)"
echo "   - 🔮 Prédiction de catégorie"
echo "   - 👁️ Options d'accessibilité"
echo ""
echo "🛑 Pour arrêter l'application : Ctrl+C"
