# Documentazione Tecnica - Piattaforma

## Architettura

### Stack Tecnologico
- **Backend**: Flask 3.0 (Python)
- **Frontend**: Bootstrap 5 + Vanilla JavaScript
- **Database**: SQLite
- **Autenticazione**: Werkzeug (bcrypt)
- **Template Engine**: Jinja2

### Pattern Architetturale
- **Blueprint Pattern**: Moduli separati per ogni funzionalità
- **MVC**: Model-View-Controller
- **REST API**: Endpoint per comunicazione esterna

## Struttura File

```
Piattaforma/
├── app.py                      # Applicazione Flask principale
├── requirements.txt            # Dipendenze Python
├── start.bat                   # Script avvio Windows
├── README.md                   # Documentazione utente
├── QUICKSTART.md              # Guida rapida
├── TECHNICAL_DOCS.md          # Questo file
│
├── modules/                    # Moduli applicazione (Blueprints)
│   ├── __init__.py
│   ├── matched_betting.py     # Modulo matched betting
│   ├── task_lavoro.py         # Modulo task lavoro
│   ├── task_privati.py        # Modulo task privati
│   └── fitness.py             # Modulo fitness
│
├── templates/                  # Template HTML (Jinja2)
│   ├── base.html              # Template base
│   ├── login.html             # Pagina login
│   ├── register.html          # Pagina registrazione
│   ├── dashboard.html         # Dashboard principale
│   ├── dev_login.html         # Login Dev Tools
│   ├── dev_tools.html         # Interfaccia Dev Tools
│   │
│   ├── matched_betting/       # Template matched betting
│   │   ├── index.html
│   │   ├── add.html
│   │   ├── edit.html
│   │   └── stats.html
│   │
│   ├── task_lavoro/           # Template task lavoro
│   │   ├── index.html
│   │   ├── add.html
│   │   └── edit.html
│   │
│   ├── task_privati/          # Template task privati
│   │   ├── index.html
│   │   ├── add.html
│   │   └── edit.html
│   │
│   └── fitness/               # Template fitness
│       ├── index.html
│       ├── pasti.html
│       ├── add_pasto.html
│       ├── edit_pasto.html
│       ├── allenamenti.html
│       ├── add_allenamento.html
│       ├── edit_allenamento.html
│       └── stats.html
│
├── static/                    # File statici
│   ├── css/
│   │   └── style.css         # Stili personalizzati
│   └── js/
│       └── main.js           # JavaScript principale
│
└── piattaforma.db            # Database SQLite (generato automaticamente)
```

## Database Schema

### Tabella: users
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,           -- Hash bcrypt
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Tabella: matched_betting
```sql
CREATE TABLE matched_betting (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    bookmaker_back TEXT NOT NULL,
    bookmaker_lay TEXT,
    stake_back REAL,
    stake_lay REAL,
    quota_back REAL,
    quota_lay REAL,
    rating TEXT,
    mercato TEXT,
    offerta TEXT,
    evento TEXT NOT NULL,
    data_evento TIMESTAMP,
    profitto REAL,
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
```

### Tabella: task_lavoro
```sql
CREATE TABLE task_lavoro (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    titolo TEXT NOT NULL,
    descrizione TEXT,
    priorita TEXT DEFAULT 'media',    -- alta, media, bassa
    stato TEXT DEFAULT 'da_fare',     -- da_fare, in_corso, completato
    deadline TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
```

### Tabella: task_privati
```sql
CREATE TABLE task_privati (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    titolo TEXT NOT NULL,
    descrizione TEXT,
    priorita TEXT DEFAULT 'media',
    stato TEXT DEFAULT 'da_fare',
    deadline TIMESTAMP,
    ricorrente BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
```

### Tabella: pasti
```sql
CREATE TABLE pasti (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    data DATE NOT NULL,
    tipo_pasto TEXT NOT NULL,         -- colazione, pranzo, cena, snack
    descrizione TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
```

### Tabella: allenamenti
```sql
CREATE TABLE allenamenti (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    data DATE NOT NULL,
    esercizio TEXT NOT NULL,
    ripetizioni INTEGER,
    peso REAL,
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
```

## Route Mapping

### Route Principali (app.py)
```
GET  /                          → Redirect a /dashboard o /login
GET  /login                     → Pagina login
POST /login                     → Processo login
GET  /register                  → Pagina registrazione
POST /register                  → Processo registrazione
GET  /logout                    → Logout
GET  /dashboard                 → Dashboard principale (protetto)
GET  /dev-login                 → Login Dev Tools
POST /dev-login                 → Processo login Dev Tools
GET  /dev-tools                 → Interfaccia Dev Tools (protetto)
GET  /dev-tools/view-file       → API: visualizza file
POST /dev-tools/save-file       → API: salva file
```

### Blueprint: matched_betting
```
Prefix: /matched-betting

GET  /                          → Lista scommesse
GET  /add                       → Form nuova scommessa
POST /add                       → Crea scommessa
GET  /edit/<id>                 → Form modifica scommessa
POST /edit/<id>                 → Aggiorna scommessa
POST /delete/<id>               → Elimina scommessa
GET  /stats                     → Statistiche
```

### Blueprint: task_lavoro
```
Prefix: /task-lavoro

GET  /                          → Lista task
GET  /add                       → Form nuovo task
POST /add                       → Crea task
GET  /edit/<id>                 → Form modifica task
POST /edit/<id>                 → Aggiorna task
POST /delete/<id>               → Elimina task
POST /toggle-status/<id>        → Cambia stato task
```

### Blueprint: task_privati
```
Prefix: /task-privati

(Stesso schema di task_lavoro)
```

### Blueprint: fitness
```
Prefix: /fitness

GET  /                          → Dashboard fitness
GET  /pasti                     → Lista pasti
GET  /pasti/add                 → Form nuovo pasto
POST /pasti/add                 → Crea pasto
GET  /pasti/edit/<id>           → Form modifica pasto
POST /pasti/edit/<id>           → Aggiorna pasto
POST /pasti/delete/<id>         → Elimina pasto
GET  /allenamenti               → Lista allenamenti
GET  /allenamenti/add           → Form nuovo allenamento
POST /allenamenti/add           → Crea allenamento
GET  /allenamenti/edit/<id>     → Form modifica allenamento
POST /allenamenti/edit/<id>     → Aggiorna allenamento
POST /allenamenti/delete/<id>   → Elimina allenamento
GET  /stats                     → Statistiche fitness
```

## Sicurezza

### Autenticazione
- Password hashate con `werkzeug.security.generate_password_hash()`
- Algoritmo: bcrypt
- Session-based authentication
- Decorator `@login_required` per proteggere route

### Session Management
- Chiave segreta generata con `os.urandom(24)`
- Session cookie httponly
- **NOTA**: In produzione usare chiave segreta fissa

### Dev Tools Protection
- Password separata: `DEV_TOOLS_PASSWORD`
- Decorator `@dev_tools_required`
- Read-only per utente, write per admin

### SQL Injection Prevention
- Uso di parametrized queries con `?` placeholders
- Nessun concatenamento di stringhe in query SQL

### XSS Prevention
- Auto-escaping di Jinja2
- Sanitizzazione input non necessaria (gestita da framework)

## API REST (Futuro)

### Autenticazione API
TODO: Implementare token-based auth (JWT)

### Endpoint API
```
GET  /api/matched-betting       → Lista scommesse (JSON)
POST /api/matched-betting       → Crea scommessa (JSON)
GET  /api/task-lavoro          → Lista task lavoro (JSON)
POST /api/task-lavoro          → Crea task lavoro (JSON)
...
```

## Estensioni Future

### Google Calendar Integration
File: `modules/calendar_integration.py`

Funzionalità:
- Creazione eventi automatici per scommesse
- Reminder per deadline task
- Sincronizzazione allenamenti

Dipendenze aggiuntive:
```
google-auth
google-auth-oauthlib
google-api-python-client
```

Setup:
1. Google Cloud Console → Crea progetto
2. Abilita Google Calendar API
3. Scarica credentials.json
4. Implementa OAuth flow in modulo

### Notifiche Push
Opzioni:
- WebSocket per notifiche real-time
- Email notifications (SMTP)
- Telegram Bot API

### Export/Import Dati
Formati:
- CSV
- JSON
- Excel (pandas)
- PDF (reportlab)

### Multi-tenant
Per supportare più utenti con separazione dati:
- Aggiungere `tenant_id` a tutte le tabelle
- Modificare query per filtrare per tenant
- Implementare sistema di inviti

### Mobile App
Opzioni:
- Progressive Web App (PWA)
- React Native
- Flutter

## Performance

### Ottimizzazioni Database
```sql
-- Indici consigliati
CREATE INDEX idx_betting_user ON matched_betting(user_id);
CREATE INDEX idx_betting_date ON matched_betting(data_evento);
CREATE INDEX idx_task_lavoro_user ON task_lavoro(user_id);
CREATE INDEX idx_task_lavoro_stato ON task_lavoro(stato);
-- ... altri indici per query frequenti
```

### Caching
Opzioni:
- Flask-Caching
- Redis per session storage
- Memoization per query pesanti

### Database Migration
Per passare a PostgreSQL/MySQL:
1. Export dati da SQLite
2. Installare driver database
3. Modificare `app.config['DATABASE']`
4. Creare schema su nuovo DB
5. Import dati

## Testing

### Unit Tests
```python
# tests/test_auth.py
def test_login():
    # Test login functionality
    pass

# tests/test_matched_betting.py
def test_add_bet():
    # Test adding bet
    pass
```

### Integration Tests
```python
# tests/test_integration.py
def test_full_user_flow():
    # Register → Login → Add task → Logout
    pass
```

### Run Tests
```bash
pytest tests/
```

## Deployment

### Produzione (Linux Server)
```bash
# Installa Gunicorn
pip install gunicorn

# Avvia con Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Nginx reverse proxy
# /etc/nginx/sites-available/piattaforma
server {
    listen 80;
    server_name piattaforma.example.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

### Systemd Service
```ini
# /etc/systemd/system/piattaforma.service
[Unit]
Description=Piattaforma Web App
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/piattaforma
ExecStart=/usr/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

## Troubleshooting

### Debug Mode
In `app.py`:
```python
app.run(debug=True)  # SOLO in sviluppo!
```

### Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
app.logger.debug("Debug message")
```

### Common Issues
1. **Database locked**: Chiudi altre connessioni
2. **Port in use**: Cambia porta o uccidi processo
3. **Import errors**: Verifica PYTHONPATH e dipendenze
4. **Template not found**: Controlla struttura cartelle

## Maintenance

### Backup Automatico
```bash
# Script backup.sh
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
cp piattaforma.db backups/piattaforma_$DATE.db
```

### Database Vacuum
```bash
sqlite3 piattaforma.db "VACUUM;"
```

### Update Dependencies
```bash
pip install --upgrade -r requirements.txt
```

---

**Versione**: 1.0.0
**Ultimo Aggiornamento**: Ottobre 2025
**Autore**: Sviluppato con Claude Code
