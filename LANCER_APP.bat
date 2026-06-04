@echo off
title Palstream - Demarrage
echo.
echo  ============================================
echo    PALSTREAM - Analyse des Pals de Palworld
echo  ============================================
echo.

REM Verifier Python
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERREUR] Python n'est pas installe ou pas dans le PATH.
    echo Telecharger Python sur https://python.org
    pause
    exit
)

REM Installer les dependances si manquantes
echo [1/2] Verification des dependances...
pip install -r app\requirements.txt -q

echo.
echo [2/2] Lancement de Palstream...
echo  L'application va s'ouvrir sur http://localhost:8501
echo  Pour arreter : CTRL+C dans cette fenetre
echo.

streamlit run app\app.py

pause
