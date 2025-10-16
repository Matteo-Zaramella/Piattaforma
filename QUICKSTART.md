# Quick Start Guide - Piattaforma

## Avvio Rapido (Windows)

### Metodo 1: Script Automatico (CONSIGLIATO)
1. Fai doppio clic su `start.bat`
2. Attendi che l'applicazione si avvii
3. Apri il browser su: http://localhost:5000

### Metodo 2: Manuale
```bash
# 1. Apri il Prompt dei comandi (CMD) o PowerShell

# 2. Vai nella cartella del progetto
cd Desktop\Piattaforma

# 3. Installa le dipendenze
pip install -r requirements.txt

# 4. Avvia l'applicazione
python app.py

# 5. Apri il browser su http://localhost:5000
```

## Primo Accesso

1. **Registrazione**
   - Clicca su "Registrati"
   - Scegli username e password
   - Clicca "Registrati"

2. **Login**
   - Inserisci le credenziali
   - Accedi alla Dashboard

## Utilizzo Moduli

### Matched Betting
- **Aggiungi scommessa**: Menu → Matched Betting → Nuova Scommessa
- **Visualizza statistiche**: Matched Betting → Statistiche
- **Modifica/Elimina**: Click sui pulsanti nella lista

### Task Lavoro
- **Nuovo task**: Menu → Task Lavoro → Nuovo Task
- **Filtra per stato**: Usa i pulsanti in alto (Da fare/In corso/Completato)
- **Completa velocemente**: Click su "Completa"

### Task Privati
- Stesso funzionamento di Task Lavoro
- In più: opzione "Task Ricorrente"

### Fitness
- **Pasti**: Fitness → Pasti → Nuovo Pasto
- **Allenamenti**: Fitness → Allenamenti → Nuovo Allenamento
- **Statistiche**: Fitness → Statistiche

## Dev Tools (Manutenzione)

1. Menu → Dev Tools
2. Password: `dev_access_2024`
3. Seleziona file da modificare
4. Usa "Salva" per applicare modifiche

**ATTENZIONE**: Usa solo se sai cosa stai facendo o su indicazione di Claude!

## Problemi Comuni

### L'applicazione non parte
```bash
# Verifica Python installato
python --version

# Se non hai Python, scaricalo da: python.org
```

### Errore "Port already in use"
- Chiudi altre applicazioni che usano porta 5000
- Oppure modifica `app.py` per usare altra porta

### Database corrotto
```bash
# Elimina il database e ricrealo
del piattaforma.db
python app.py
```

### Password dimenticata
```bash
# Elimina il database (perderai i dati!)
del piattaforma.db
python app.py
# Poi registrati di nuovo
```

## Backup Dati

**IMPORTANTE**: Fai backup regolari!

1. Copia il file `piattaforma.db`
2. Salvalo in un posto sicuro (es. OneDrive, Google Drive)

Per ripristinare:
1. Sostituisci `piattaforma.db` con il backup
2. Riavvia l'applicazione

## Accesso da Altri Dispositivi (Stessa Rete)

1. Trova il tuo IP locale:
   ```bash
   ipconfig
   # Cerca "IPv4 Address" (es. 192.168.1.100)
   ```

2. Su altri dispositivi nella stessa rete:
   - Apri browser
   - Vai su: http://192.168.1.100:5000
   - (Sostituisci con il tuo IP)

3. **NOTA**: Il firewall potrebbe bloccare. Aggiungi eccezione per Python.

## Google Calendar (TODO - In Sviluppo)

Funzionalità in arrivo per:
- Promemoria automatici per scommesse
- Sincronizzazione allenamenti
- Scadenze task

## Supporto

Se hai problemi:
1. Controlla i messaggi di errore nel terminale
2. Leggi README.md per info dettagliate
3. Usa Dev Tools per condividere codice con Claude
4. Verifica che tutte le dipendenze siano installate

## Comandi Utili

```bash
# Installa/Aggiorna dipendenze
pip install -r requirements.txt

# Avvia applicazione
python app.py

# Ferma applicazione
CTRL + C

# Verifica versione Flask
python -c "import flask; print(flask.__version__)"

# Reset database
del piattaforma.db
```

## Tips & Tricks

1. **Bookmark**: Salva http://localhost:5000 nei preferiti
2. **Shortcut Desktop**: Crea collegamento a `start.bat`
3. **Backup Automatico**: Usa script o servizio cloud
4. **Task Ricorrenti**: Usa flag "ricorrente" per task ripetitivi
5. **Filtri**: Sfrutta i filtri per trovare velocemente task/scommesse
6. **Statistiche**: Controlla regolarmente per monitorare progressi

---

**Buon utilizzo della Piattaforma!**

Per domande o problemi, usa Dev Tools per condividere il codice con Claude.
