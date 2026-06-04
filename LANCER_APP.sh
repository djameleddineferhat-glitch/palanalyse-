#!/bin/bash
echo "=========================================="
echo "  PALSTREAM - Lancement de l'application"
echo "=========================================="
echo ""

# Vérifier si streamlit est installé
if ! command -v streamlit &> /dev/null; then
    echo "Installation des dépendances..."
    pip install -r app/requirements.txt
fi

echo "Lancement de Palstream..."
echo "L'application va s'ouvrir sur http://localhost:8501"
echo ""
streamlit run app/app.py
