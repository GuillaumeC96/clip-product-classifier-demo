#!/bin/bash

# Script pour lancer l'application CLIP avec accès externe
echo "🚀 Lancement de l'application CLIP (accès externe)"
echo "================================================="

# Activer l'environnement virtuel
echo "🔧 Activation de l'environnement virtuel..."
source clip_cloud_env/bin/activate

# Arrêter l'application existante si elle tourne
if pgrep -f "streamlit run accueil_cloud.py" > /dev/null; then
    echo "🛑 Arrêt de l'application existante..."
    pkill -f "streamlit run accueil_cloud.py"
    sleep 2
fi

# Lancer Streamlit sur toutes les interfaces
echo "🔄 Lancement de l'application Streamlit..."
streamlit run accueil_cloud.py --server.port 8502 --server.address 0.0.0.0 --server.headless true &

# Attendre que l'application démarre
sleep 3

echo "✅ Application lancée avec accès externe"
echo ""
echo "🌐 URLs d'accès :"
echo "   - Local : http://localhost:8502"
echo "   - Réseau : http://192.168.1.75:8502"
echo "   - Externe : http://81.250.56.141:8502"
echo ""
echo "📱 Depuis un autre PC, utilisez :"
echo "   http://192.168.1.75:8502"
echo ""
echo "🔧 Configuration du pare-feu (si nécessaire) :"
echo "   sudo ufw allow 8502"
echo ""
echo "🛑 Pour arrêter l'application : Ctrl+C ou pkill -f streamlit"
