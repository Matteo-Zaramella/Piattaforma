# Piattaforma - Riepilogo Completo del Progetto

**Data ultimo aggiornamento**: 20 Ottobre 2025
**Versione**: 1.1.0
**Deployment**: https://piattaforma.onrender.com
**Repository**: https://github.com/Matteo-Zaramella/Piattaforma

---

## 📋 INDICE

1. [Panoramica del Progetto](#panoramica-del-progetto)
2. [Struttura Database](#struttura-database)
3. [Moduli e Blueprint](#moduli-e-blueprint)
4. [Home Pubblica](#home-pubblica)
5. [Area Privata](#area-privata)
6. [Funzionalità Implementate](#funzionalità-implementate)
7. [Problemi Risolti](#problemi-risolti)
8. [TODO e Funzionalità Future](#todo-e-funzionalità-future)
9. [Come Riprendere il Lavoro](#come-riprendere-il-lavoro)

---

## 🎯 PANORAMICA DEL PROGETTO

**Piattaforma** è un hub personale centralizzato per gestire fitness, alimentazione, appuntamenti, wishlist e informazioni sulla posizione. Include:

- **Home Pubblica**: Pagina visibile a tutti con 3 sezioni (Appuntamenti, Wishlist, Dove Sono)
- **Area Privata**: Dashboard con 8 app per gestire dati personali
- **Dark Mode**: Tema scuro per l'area privata
- **Responsive Design**: Layout ottimizzato per mobile e desktop

### Stack Tecnologico
- **Backend**: Flask 3.0.0 (Python)
- **Database**: PostgreSQL (Render) + SQLite (locale)
- **Frontend**: Bootstrap 5.3.0 + Bootstrap Icons
- **Deployment**: Render (auto-deploy da GitHub)
- **CSS**: Custom + variabili CSS per dark mode
- **ASCII Art**: Sfondo decorativo con emoji tradizionali

---

## 🗄️ STRUTTURA DATABASE

### Tabelle Principali

#### `users`
```sql
- id: INTEGER PRIMARY KEY
- username: TEXT UNIQUE NOT NULL
- password: TEXT NOT NULL
- created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

#### `user_preferences`
```sql
- id: INTEGER PRIMARY KEY
- user_id: INTEGER FOREIGN KEY
- dark_mode: BOOLEAN DEFAULT FALSE
- language: TEXT DEFAULT 'it' (it/en/es)
- notifications: BOOLEAN DEFAULT TRUE
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
```

#### `wishlist` (Lista di Babbo Natale)
```sql
- id: INTEGER PRIMARY KEY
- user_id: INTEGER FOREIGN KEY
- nome: TEXT NOT NULL
- descrizione: TEXT
- link: TEXT (URL prodotto)
- priorita: TEXT DEFAULT 'media' (alta/media/bassa)
- pubblico: BOOLEAN DEFAULT TRUE
- created_at: TIMESTAMP
```

#### `current_location` (Dove Sono)
```sql
- id: INTEGER PRIMARY KEY
- user_id: INTEGER FOREIGN KEY
- nome_luogo: TEXT NOT NULL
- indirizzo: TEXT
- google_maps_link: TEXT
- orario: TEXT
- note: TEXT
- immagine_url: TEXT
- attivo: BOOLEAN DEFAULT TRUE
- data_inizio: TIMESTAMP
- data_fine: TIMESTAMP
- created_at: TIMESTAMP
```

#### `appointments` (Appuntamenti)
```sql
- id: INTEGER PRIMARY KEY
- user_id: INTEGER FOREIGN KEY
- titolo: TEXT NOT NULL
- descrizione: TEXT
- data_ora: TIMESTAMP NOT NULL
- luogo: TEXT
- pubblico: BOOLEAN DEFAULT FALSE
- completato: BOOLEAN DEFAULT FALSE
- created_at: TIMESTAMP
```

#### Altre Tabelle
- `pasti`: Tracciamento pasti giornalieri
- `alimenti`: Database alimenti con calorie/macros
- `allenamenti`: Schede workout con esercizi
- `workout_history`: Storico allenamenti completati

---

## 📦 MODULI E BLUEPRINT

### File: `app.py`
**Ruolo**: File principale dell'applicazione
- Configurazione Flask
- Gestione database (PostgreSQL/SQLite)
- Context processor per dark mode
- Route principali: `/`, `/login`, `/register`, `/dashboard`
- Registrazione blueprint

### Moduli Implementati

#### `modules/settings.py`
**Route prefix**: `/settings`
**Funzioni**:
- `index()`: Visualizza pagina impostazioni
- `update()`: Salva preferenze (dark mode, lingua, notifiche)
- `toggle_dark_mode()`: Toggle rapido via AJAX
- `get_preferences()`: API per ottenere preferenze

#### `modules/wishlist.py`
**Route prefix**: `/wishlist`
**Funzioni**:
- `index()`: Lista wishlist completa
- `add_item()`: Aggiungi nuovo item
- `edit_item(id)`: Modifica item esistente
- `delete_item(id)`: Elimina item

#### `modules/location.py`
**Route prefix**: `/location`
**Funzioni**:
- `index()`: Visualizza tutte le posizioni
- `set_location()`: Imposta nuova posizione attiva
- `edit_location(id)`: Modifica posizione
- `delete_location(id)`: Elimina posizione
- `deactivate_all()`: Disattiva tutte (pulsante "Non Esisto")

#### `modules/appointments.py`
**Route prefix**: `/appointments`
**Funzioni**:
- `index()`: Lista tutti gli appuntamenti
- `add_appointment()`: Aggiungi nuovo appuntamento
- `edit_appointment(id)`: Modifica appuntamento
- `delete_appointment(id)`: Elimina appuntamento
- `toggle_complete(id)`: Segna completato/non completato

#### `modules/fitness.py`
**Route prefix**: `/fitness`
**Funzioni**:
- `index()`: Dashboard fitness
- `add_workout()`: Aggiungi allenamento
- `start_workout(id)`: Avvia sessione workout
- `complete_workout()`: Completa workout

#### `modules/pasti.py`
**Route prefix**: `/pasti`
**Funzioni**:
- `index()`: Visualizza pasti giornalieri
- `add_pasto()`: Aggiungi pasto con alimenti
- `edit_pasto(id)`: Modifica pasto
- `export_csv()`: Esporta storico CSV

---

## 🌐 HOME PUBBLICA

**File**: `templates/home.html`
**URL**: `/` (root)
**Caratteristiche**:

### Design
- Sfondo nero (#000000) con ASCII art emoji
- 20 emoji tradizionali sparse (:), :D, ♥, ★, ;), ^_^, *_*, :P, ♪, ☆)
- Opacità 80% per emoji, 30% per spaziatura (..., ---, ~~~)
- Layout responsive a 3 colonne
- Hero section con saluti random

### Sezioni

#### 1. Prossimi Impegni (Sinistra)
- Mostra appuntamenti pubblici futuri
- Ordinati per data crescente
- Visualizza: data/ora, titolo, descrizione, luogo
- Empty state: "Nessun impegno in programma"

#### 2. Lista di Babbo Natale (Centro)
- Mostra wishlist item pubblici
- Badge priorità colorati (alta=rosso, media=giallo, bassa=grigio)
- Link a prodotti esterni
- Empty state: "La lista è vuota al momento"

#### 3. Dove Sono (Destra)
- Mostra posizione attiva corrente
- Immagine preview del luogo
- Indirizzo, orario, note
- Link a Google Maps
- Empty state: "Al momento non esisto, torna più tardi"

### JavaScript Dinamico
- Rotazione random di 10 saluti
- Rotazione random di 8 claim
- Rotazione random di 8 descrizioni
- Animazioni fadeInUp al caricamento

---

## 🔒 AREA PRIVATA

**File**: `templates/dashboard.html`
**URL**: `/dashboard` (richiede login)

### 8 App Disponibili

1. **Impostazioni** 🎨
   - Gradiente: viola-rosa
   - Route: `/settings`
   - Gestione preferenze utente

2. **Fitness** 💪
   - Gradiente: arancione-rosa
   - Route: `/fitness`
   - Gestione allenamenti

3. **Pasti** 🍽️
   - Gradiente: verde-ciano
   - Route: `/pasti`
   - Tracciamento alimentazione

4. **Statistiche** 📊
   - Gradiente: blu-azzurro
   - Route: `/statistics` (TODO)
   - Grafici e analytics

5. **Lista Desideri** 🎁
   - Gradiente: rosso-arancio
   - Route: `/wishlist`
   - Gestione wishlist

6. **Dove Sono** 📍
   - Gradiente: rosa-azzurro
   - Route: `/location`
   - Gestione posizione pubblica

7. **Appuntamenti** 📅
   - Gradiente: rosso-rosa
   - Route: `/appointments`
   - Gestione appuntamenti

8. **Dev Tools** 🛠️
   - Gradiente: grigio-blu scuro
   - Route: `/dev_tools`
   - Strumenti sviluppo

---

## ✅ FUNZIONALITÀ IMPLEMENTATE

### Dark Mode ✔️
- **Status**: Funzionante
- **Come funziona**:
  - Classe `dark-mode` applicata al body
  - Context processor inietta `dark_mode` in tutti i template
  - Toggle rapido con AJAX + reload pagina
  - CSS variabili per colori tematici
  - Cache-control headers per prevenire caching
  - Conversione esplicita SQLite 0/1 → boolean

### Location Management ✔️
- Imposta dove ti trovi attualmente
- Supporto immagine preview
- Link Google Maps integrato
- Range date inizio/fine
- Pulsante "Non Esisto" per disattivare tutto
- Visibilità pubblica controllata da flag `attivo`

### Appointments Management ✔️
- Aggiungi/modifica/elimina appuntamenti
- Flag pubblico/privato
- Segna come completato
- Badge visivi per stato
- Filtro automatico futuri per home pubblica

### Wishlist ✔️
- Gestione completa CRUD
- Priorità (alta/media/bassa)
- Link esterni a prodotti
- Visibilità pubblica/privata
- Badge colorati per priorità

### Fitness & Nutrition ✔️
- Database alimenti con macro
- Schede allenamento personalizzate
- Tracciamento workout history
- Export CSV dei pasti
- Statistiche giornaliere calorie/proteine

---

## 🔧 PROBLEMI RISOLTI

### 1. Dark Mode Non Funzionava
**Problema**: Toggle dark mode non applicava il tema
**Causa**:
- Mancava `conn.commit()` in settings.py
- Conversione boolean non gestiva correttamente 0/1 di SQLite
**Soluzione**:
- Aggiunto `conn.commit()` in tutti gli UPDATE
- Conversione esplicita: `bool(int(prefs['dark_mode']))`
- JavaScript ora ricarica pagina dopo toggle
- Cache-control headers in base.html

### 2. Settings Form Malformato
**Problema**: Form tag incompleto in settings.html
**Causa**: Mancava `>` di chiusura
**Soluzione**: Corretto `<form method="POST" action="{{ url_for('settings.update') }}">`

### 3. CSV Export Errori Encoding
**Problema**: CSV generati con encoding errato
**Causa**: Python 3.x gestisce bytes diversamente
**Soluzione**: Usato `io.StringIO()` e `TextIOWrapper` per gestire correttamente l'encoding

### 4. Workout Non Mostrava Completati
**Problema**: Storico workout vuoto
**Causa**: Join SQL sbagliato tra workout_history e allenamenti
**Soluzione**: Corretto LEFT JOIN e aggiunta colonna `nome_allenamento`

---

## 🚀 TODO E FUNZIONALITÀ FUTURE

### Priorità Alta

#### 1. Google Calendar Integration
**Descrizione**: Sincronizzare appuntamenti con Google Calendar
**Cosa serve**:
- Google Calendar API credentials
- OAuth2 flow per autenticazione
- Sync bidirezionale eventi
- Pip install: `google-auth`, `google-auth-oauthlib`, `google-api-python-client`

#### 2. Push Notifications
**Descrizione**: Notifiche push al telefono per appuntamenti
**Cosa serve**:
- Firebase Cloud Messaging (FCM) o OneSignal
- Service worker per notifiche web
- Background task per check scadenze
- Pip install: `firebase-admin` o SDK OneSignal

#### 3. Todo App Avanzata
**Descrizione**: App todo completa con eventi/task, shopping list, progetti
**Features richieste**:
- Distinzione Eventi vs Task
- Liste della spesa
- Progetti con workflow
- Notifiche scadenze
- Tags e categorie

### Priorità Media

#### 4. Statistiche Dashboard
**URL**: `/statistics`
**Cosa mostrare**:
- Grafici trend peso/composizione corporea
- Calorie e macro giornaliere/settimanali
- Workout frequency
- Librerie: Chart.js o Plotly

#### 5. Export/Import Dati
**Descrizione**: Backup e restore completo
**Formati**:
- JSON per backup completo
- CSV per singoli moduli
- ZIP per export totale

#### 6. Multi-user Support
**Descrizione**: Permettere più utenti sulla stessa istanza
**Cosa aggiungere**:
- Sistema ruoli (admin/user)
- Privacy settings per visibilità dati
- User profile page

### Priorità Bassa

#### 7. PWA (Progressive Web App)
- Service worker per offline
- App installabile su mobile
- Cache strategico

#### 8. API REST
- Endpoint JSON per tutti i moduli
- Autenticazione JWT
- Documentazione Swagger

#### 9. Themes Personalizzati
- Oltre a light/dark, permettere colori custom
- Preset tematici (Ocean, Forest, Sunset, etc.)

---

## 🔄 COME RIPRENDERE IL LAVORO

### Setup Locale

1. **Naviga alla cartella**:
   ```bash
   cd C:\Users\offic\Desktop\Piattaforma
   ```

2. **Verifica ambiente Python**:
   ```bash
   python --version  # Dovrebbe essere 3.9+
   pip list  # Controlla dipendenze installate
   ```

3. **Avvia applicazione locale**:
   ```bash
   python app.py
   ```
   Apri: `http://localhost:5000`

4. **Database locale**:
   - SQLite: `piattaforma.db` (creato automaticamente)
   - Per ispezionare: `sqlite3 piattaforma.db`

### Git Workflow

1. **Verifica branch e stato**:
   ```bash
   git status
   git log --oneline -5  # Ultimi 5 commit
   ```

2. **Pull ultimi aggiornamenti** (se necessario):
   ```bash
   git pull origin main
   ```

3. **Workflow sviluppo**:
   ```bash
   # 1. Modifica file
   # 2. Stage changes
   git add <file>
   # 3. Commit
   git commit -m "Descrizione modifiche"
   # 4. Push (auto-deploy su Render)
   git push origin main
   ```

### Deployment Render

- **URL produzione**: https://piattaforma.onrender.com
- **Dashboard Render**: https://dashboard.render.com
- **Auto-deploy**: Attivo su push a `main`
- **Tempo deploy**: ~2-3 minuti
- **Logs**: Visibili nella dashboard Render

### Variabili d'Ambiente (Render)

```bash
DATABASE_URL=<postgres_url>  # Automatico da Render
SECRET_KEY=<your_secret_key>
USE_POSTGRES=true
```

### File Importanti da Conoscere

```
Piattaforma/
├── app.py                    # ⭐ Main application
├── db_utils.py              # Database helpers
├── requirements.txt         # Dipendenze Python
├── PROJECT_SUMMARY.md       # 📄 QUESTO FILE
├── modules/                 # Blueprint Flask
│   ├── settings.py
│   ├── wishlist.py
│   ├── location.py
│   ├── appointments.py
│   ├── fitness.py
│   └── pasti.py
├── templates/               # Jinja2 templates
│   ├── base.html           # Template base con dark mode
│   ├── home.html           # ⭐ Home pubblica con ASCII art
│   ├── dashboard.html      # Dashboard privata
│   ├── settings.html
│   ├── appointments/
│   ├── location/
│   ├── wishlist/
│   ├── fitness/
│   └── pasti/
└── static/
    └── css/
        └── style.css       # Dark mode CSS
```

---

## 💡 TIPS PER NUOVA SESSIONE

### Se Dark Mode Non Funziona Ancora
1. Apri DevTools (F12) → Console
2. Controlla errori JavaScript
3. Vai a Network → Disabilita cache
4. Controlla che il body abbia classe `dark-mode` quando attivo
5. Prova modalità incognito per escludere cache browser

### Se Database Dà Errori
1. Verifica che `piattaforma.db` esista
2. Se corrotto, elimina e riavvia app (verrà ricreato)
3. Per Postgres, controlla `DATABASE_URL` su Render

### Per Testare Nuove Feature
1. Testa sempre prima in locale
2. Commit su branch separato se feature grande
3. Merge su main solo quando funziona
4. Render deploierà automaticamente

### Per Aggiungere Nuova App
1. Crea file in `modules/nome_app.py`
2. Definisci Blueprint con route
3. Registra in `app.py`: `app.register_blueprint(nome_app_bp)`
4. Crea template in `templates/nome_app/`
5. Aggiungi icona in `dashboard.html`
6. Aggiorna database se servono nuove tabelle

---

## 📞 CONTATTI E RISORSE

- **Repository**: https://github.com/Matteo-Zaramella/Piattaforma
- **Deployment**: https://piattaforma.onrender.com
- **Flask Docs**: https://flask.palletsprojects.com/
- **Bootstrap Docs**: https://getbootstrap.com/docs/5.3/
- **Render Docs**: https://render.com/docs

---

## 📝 NOTE FINALI

**Ultimo aggiornamento**: 20 Ottobre 2025, ore 16:30
**Commits recenti**:
1. `e0ff98b` - Aggiunto sfondo ASCII art con emoji tradizionali
2. `7ace18a` - Fix dark mode toggle e template location/appointments
3. `8afdfbe` - Aggiunte app Location e Appointments

**Stato generale**: ✅ Tutto funzionante e deployato
**Prossimi passi suggeriti**: Google Calendar integration, Push notifications, Todo app avanzata

**Buon lavoro domani! 🚀**

---

*Documento generato da Claude Code*
