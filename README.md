# Piattaforma - Hub Applicazioni Personali

Applicazione web centralizzata per la gestione di:
- Matched Betting
- Task Lavoro
- Task Privati
- Fitness (Pasti e Allenamenti)

Sviluppato con Flask, Bootstrap 5 e SQLite.

## Caratteristiche

- **Sistema di Login**: Autenticazione sicura con password hash
- **Dashboard Unificata**: Panoramica di tutti i moduli
- **Dev Tools**: Interfaccia per la manutenzione del codice
- **Responsive Design**: Ottimizzato per desktop e mobile
- **API REST**: Comunicazione con altri terminali
- **Google Calendar**: Integrazione per promemoria (in sviluppo)

## Requisiti

- Python 3.8 o superiore
- pip (gestore pacchetti Python)

## Installazione

### 1. Clona o scarica il progetto

Il progetto è già nella cartella `Desktop/Piattaforma`

### 2. Crea un ambiente virtuale (opzionale ma consigliato)

```bash
cd Desktop/Piattaforma
python -m venv venv

# Attiva l'ambiente virtuale
# Su Windows:
venv\Scripts\activate
# Su Mac/Linux:
source venv/bin/activate
```

### 3. Installa le dipendenze

```bash
pip install -r requirements.txt
```

### 4. Avvia l'applicazione

```bash
python app.py
```

L'applicazione sarà disponibile su: **http://localhost:5000**

## Primo Utilizzo

1. Apri il browser su http://localhost:5000
2. Clicca su "Registrati" per creare il tuo account
3. Effettua il login con le credenziali appena create
4. Accedi alla dashboard e inizia a utilizzare i moduli

## Struttura del Progetto

```
Piattaforma/
├── app.py                  # Applicazione principale Flask
├── requirements.txt        # Dipendenze Python
├── piattaforma.db         # Database SQLite (creato automaticamente)
├── modules/               # Moduli dell'applicazione
│   ├── matched_betting.py
│   ├── task_lavoro.py
│   ├── task_privati.py
│   └── fitness.py
├── templates/             # Template HTML
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── matched_betting/
│   ├── task_lavoro/
│   ├── task_privati/
│   └── fitness/
└── static/                # File statici
    ├── css/
    │   └── style.css
    └── js/
        └── main.js
```

## Moduli Disponibili

### 1. Matched Betting
Traccia tutte le scommesse matched betting con:
- Bookmaker (Back e Lay)
- Stake e Quote
- Rating, Mercato, Offerta
- Evento e Data
- Profitto/Perdita
- Statistiche dettagliate

### 2. Task Manager Lavoro
Gestisci i task lavorativi con:
- Titolo e Descrizione
- Priorità (Alta/Media/Bassa)
- Stato (Da fare/In corso/Completato)
- Deadline
- Filtri per stato

### 3. Task Manager Vita Privata
Gestisci i task personali con:
- Tutte le funzionalità del Task Lavoro
- Opzione task ricorrenti
- Separazione chiara tra lavoro e privato

### 4. Fitness Tracker
Monitora alimentazione e allenamenti:
- **Pasti**: Data, Tipo (colazione/pranzo/cena/snack), Descrizione
- **Allenamenti**: Data, Esercizio, Ripetizioni, Peso, Note
- Statistiche settimanali e mensili
- Progressi per esercizio

## Dev Tools

La sezione Dev Tools permette di:
- Visualizzare il codice sorgente di tutti i file
- Modificare i file direttamente dall'interfaccia
- Navigare nella struttura del progetto
- Editor con syntax highlighting

**Accesso Dev Tools:**
1. Clicca su "Dev Tools" nel menu
2. Inserisci la password: `dev_access_2024`
3. Seleziona un file da visualizzare/modificare

**ATTENZIONE**: Le modifiche ai file possono compromettere il funzionamento dell'applicazione. Usa con cautela.

## API REST

L'applicazione espone API REST per comunicare con altri terminali/applicazioni.

### Esempi di endpoint:

- `GET /matched-betting/` - Lista scommesse
- `POST /matched-betting/add` - Aggiungi scommessa
- `GET /task-lavoro/` - Lista task lavoro
- `POST /fitness/allenamenti/add` - Aggiungi allenamento

(Documentazione API completa in arrivo)

## Configurazione

### Modifica Password Dev Tools

Modifica il file `app.py`, linea 25:

```python
DEV_TOOLS_PASSWORD = "tua_password_qui"
```

### Modifica Porta del Server

Modifica l'ultima linea di `app.py`:

```python
app.run(debug=True, host='0.0.0.0', port=5000)  # Cambia 5000 con la porta desiderata
```

### Database

Il database SQLite viene creato automaticamente al primo avvio in `piattaforma.db`.

Per resettare il database:
```bash
rm piattaforma.db
python app.py
```

## Integrazione Google Calendar (TODO)

**Funzionalità in sviluppo**

Per abilitare i promemoria automatici su Google Calendar:

1. Crea un progetto nella Google Cloud Console
2. Abilita Google Calendar API
3. Scarica le credenziali OAuth 2.0
4. Salva il file come `credentials.json` nella root del progetto
5. Riavvia l'applicazione

## Troubleshooting

### Errore: "Address already in use"
La porta 5000 è già occupata. Cambia porta o termina il processo:
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Mac/Linux
lsof -i :5000
kill -9 <PID>
```

### Errore: "ModuleNotFoundError"
Installa le dipendenze:
```bash
pip install -r requirements.txt
```

### Database corrotto
Elimina e ricrea:
```bash
rm piattaforma.db
python app.py
```

## Backup

Per fare backup dei tuoi dati:

1. **Database**: Copia il file `piattaforma.db`
2. **Codice**: Copia l'intera cartella `Piattaforma`

## Sicurezza

- Le password sono hashate con Werkzeug (bcrypt)
- Le sessioni utilizzano chiavi segrete casuali
- Dev Tools protetto da password separata
- Database locale (non esposto online)

**NOTA**: Per uso in produzione (server online), configura:
- HTTPS
- Chiave segreta fissa (non `os.urandom`)
- Firewall e rate limiting
- Backup automatici

## Supporto

Per assistenza o manutenzione, utilizza la sezione Dev Tools per condividere il codice con Claude.

## Licenza

Uso personale - Tutti i diritti riservati

---

**Sviluppato con Claude Code**
**Versione**: 1.1.0
**Data**: Ottobre 2025
