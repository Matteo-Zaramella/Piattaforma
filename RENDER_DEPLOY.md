# Guida Deploy su Render con PostgreSQL

## 1. Preparazione Database PostgreSQL su Render

1. Vai su https://dashboard.render.com
2. Click **New +** → **PostgreSQL**
3. Configura:
   - Name: `piattaforma-db`
   - Database: `piattaforma`
   - User: (generato automaticamente)
   - Region: Frankfurt (o più vicino a te)
   - Instance Type: **Free**
4. Click **Create Database**
5. **Importante**: Copia l'**Internal Database URL** (inizia con `postgres://`)

## 2. Deploy Web Service

1. Click **New +** → **Web Service**
2. Connetti il tuo repository GitHub
3. Configura:
   - Name: `piattaforma`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Instance Type: **Free**

## 3. Configurare Variabili d'Ambiente

Nel pannello del Web Service, vai su **Environment** e aggiungi:

```
DATABASE_URL = [Incolla Internal Database URL copiato prima]
SECRET_KEY = [genera chiave casuale, es: python -c "import os; print(os.urandom(24).hex())"]
DEBUG = False
```

## 4. Deploy

1. Click **Create Web Service**
2. Render farà automaticamente il deploy
3. Attendi che il build completi
4. Le tabelle PostgreSQL verranno create automaticamente al primo avvio!

## 5. Verifica

1. Apri l'URL del tuo servizio (es: `https://piattaforma.onrender.com`)
2. Prova a registrarti con un nuovo account
3. I dati ora persistono anche dopo il riavvio!

## Note Importanti

- Il database PostgreSQL Free ha 90 giorni di retention
- Il Web Service va in sleep dopo 15min di inattività  
- I dati nel database **persistono** anche quando il servizio dorme
- Primo avvio può richiedere 1-2 minuti

## Risoluzione Problemi

### Errore connessione database
- Verifica che `DATABASE_URL` sia l'**Internal** URL, non l'External
- Deve iniziare con `postgres://` o `postgresql://`

### Tabelle non create
- Controlla i logs: `Logs` → cerca "Tabelle PostgreSQL verificate/create"
- Se errore, verifica sintassi SQL in `app.py`

### Credenziali non persistono
- Verifica che stai usando PostgreSQL e non SQLite
- Nei logs deve apparire "PostgreSQL rilevato"

