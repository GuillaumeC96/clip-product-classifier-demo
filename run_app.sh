#!/bin/bash

# Script de lancement de l'application
echo "🚀 Lancement de l'application de classification de produits..."

# Vérifier si l'environnement virtuel existe
if [ ! -d "venv" ]; then
    echo "📦 Création de l'environnement virtuel..."
    python -m venv venv
fi

# Activer l'environnement virtuel
echo "🔧 Activation de l'environnement virtuel..."
source venv/bin/activate

# Installer les dépendances
echo "📚 Installation des dépendances..."
pip install -r requirements.txt

# Lancer l'application
echo "🌟 Lancement de Streamlit..."
streamlit run accueil.py --server.port 8501
