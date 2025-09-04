#!/bin/bash

# Script pour lancer l'application CLIP de manière sécurisée
echo "🔒 Lancement sécurisé de l'application CLIP"
echo "==========================================="

# Vérifier si l'utilisateur est root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Ne pas exécuter ce script en tant que root"
    exit 1
fi

# Activer le pare-feu avec restrictions
echo "🛡️ Configuration du pare-feu..."
sudo ufw enable
sudo ufw allow from 192.168.1.0/24 to any port 8502
sudo ufw deny from any to any port 8502

echo "✅ Pare-feu configuré :"
echo "   - ✅ Accès autorisé : réseau local (192.168.1.x)"
echo "   - 🚫 Accès refusé : internet"

# Arrêter l'application existante si elle tourne
if pgrep -f "streamlit run accueil_cloud.py" > /dev/null; then
    echo "🛑 Arrêt de l'application existante..."
    pkill -f "streamlit run accueil_cloud.py"
    sleep 2
fi

# Activer l'environnement virtuel
echo "🔧 Activation de l'environnement virtuel..."
source clip_cloud_env/bin/activate

# Lancer l'application
echo "🔄 Lancement de l'application Streamlit..."
streamlit run accueil_cloud.py --server.port 8502 --server.address 0.0.0.0 --server.headless true &

# Attendre que l'application démarre
sleep 3

echo ""
echo "✅ Application lancée de manière sécurisée"
echo ""
echo "🌐 URLs d'accès :"
echo "   - Local : http://localhost:8502"
echo "   - Réseau local : http://192.168.1.75:8502"
echo ""
echo "🔒 Sécurité :"
echo "   - ✅ Accès autorisé : réseau local uniquement (192.168.1.x)"
echo "   - 🚫 Accès internet : bloqué"
echo "   - 🛡️ Pare-feu : activé avec restrictions"
echo ""
echo "📱 Depuis un autre PC du réseau local :"
echo "   http://192.168.1.75:8502"
echo ""
echo "🔍 Surveillance :"
echo "   - Voir les connexions : sudo netstat -tulpn | grep :8502"
echo "   - Logs pare-feu : sudo tail -f /var/log/ufw.log"
echo ""
echo "🛑 Pour arrêter l'application :"
echo "   pkill -f streamlit"
echo "   sudo ufw deny 8502"
