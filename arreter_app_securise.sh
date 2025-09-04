#!/bin/bash

# Script pour arrêter l'application CLIP de manière sécurisée
echo "🛑 Arrêt sécurisé de l'application CLIP"
echo "======================================"

# Arrêter l'application Streamlit
echo "🔄 Arrêt de l'application Streamlit..."
if pgrep -f "streamlit run accueil_cloud.py" > /dev/null; then
    pkill -f "streamlit run accueil_cloud.py"
    echo "✅ Application arrêtée"
else
    echo "ℹ️ Aucune application en cours d'exécution"
fi

# Bloquer le port 8502
echo "🔒 Blocage du port 8502..."
sudo ufw deny 8502

# Vérifier qu'aucun processus n'écoute sur le port
echo "🔍 Vérification des processus..."
if sudo netstat -tulpn | grep :8502 > /dev/null; then
    echo "⚠️ Attention : Un processus écoute encore sur le port 8502"
    sudo netstat -tulpn | grep :8502
else
    echo "✅ Aucun processus n'écoute sur le port 8502"
fi

# Afficher le statut du pare-feu
echo ""
echo "🛡️ Statut du pare-feu :"
sudo ufw status numbered | grep 8502

echo ""
echo "✅ Application arrêtée de manière sécurisée"
echo "🔒 Port 8502 bloqué"
echo "🛡️ Sécurité restaurée"
