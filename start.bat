@echo off
echo ========================================
echo   Piattaforma - Avvio Applicazione
echo ========================================
echo.

REM Controlla se l'ambiente virtuale esiste
if not exist "venv" (
    echo Creazione ambiente virtuale...
    python -m venv venv
    echo.
)

REM Attiva ambiente virtuale
echo Attivazione ambiente virtuale...
call venv\Scripts\activate
echo.

REM Installa dipendenze
echo Verifica dipendenze...
pip install -r requirements.txt --quiet
echo.

REM Avvia applicazione
echo Avvio applicazione...
echo L'applicazione sara disponibile su: http://localhost:5000
echo Premi CTRL+C per terminare
echo.
python app.py

pause
