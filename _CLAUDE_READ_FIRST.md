# ⚠️ CLAUDE: LEGGI QUESTO FILE PRIMA DI QUALSIASI AZIONE

**IMPORTANTE**: Questo file contiene TUTTE le informazioni operative critiche. NON procedere senza averlo letto completamente.

---

## 🚨 REGOLA D'ORO

**PRIMA di modificare QUALSIASI cosa:**
1. Leggi QUESTO file completamente
2. Verifica lo schema database Supabase
3. Proponi soluzione all'utente
4. Aspetta conferma
5. Testa in locale
6. Solo dopo: commit e push

**MAI modificare codice senza conferma utente.**

---

## 📊 STATO ATTUALE PROGETTO

**Data ultimo aggiornamento**: 3 Novembre 2025
**Versione**: 1.2.0
**URL Produzione**: https://matteozaramella.com
**Repository**: https://github.com/Matteo-Zaramella/Piattaforma

### Deployment
- **Hosting**: Render Web Service
  - Service ID: `srv-d3of691r0fns73c5t110`
  - Region: Oregon
  - Auto-deploy: Attivo da branch `main`
  - Tempo deploy: ~2-3 minuti

- **Database**: Supabase PostgreSQL (ATTIVO E PERMANENTE)
  - Project ID: `wuvuapmjclahbmngntku`
  - Region: EU North (Stockholm)
  - Connection String: `postgresql://postgres.wuvuapmjclahbmngntku:n5x8%25XnUK5xMWnV5qWg6@aws-1-eu-north-1.pooler.supabase.com:6543/postgres`

### Moduli Attivi (Post-Cleanup)
1. **Game Prize** 🏆 - PRIORITÀ MASSIMA
2. **Fitness** 💪
3. **Pasti** 🍽️
4. **Wishlist** 🎁
5. **Settings** ⚙️
6. **Dev Tools** 🛠️

### Moduli Rimossi
- ❌ Location (Dove Sono)
- ❌ Appointments (Appuntamenti)
- ❌ Statistiche

---

## 🗄️ DATABASE: SUPABASE POSTGRESQL

### Credenziali
```
Project URL: https://wuvuapmjclahbmngntku.supabase.co
Project ID: wuvuapmjclahbmngntku
Password: n5x8%XnUK5xMWnV5qWg6

CONNECTION STRING (Transaction Mode - ATTIVA):
postgresql://postgres.wuvuapmjclahbmngntku:n5x8%25XnUK5xMWnV5qWg6@aws-1-eu-north-1.pooler.supabase.com:6543/postgres

Dashboard: https://supabase.com/dashboard/project/wuvuapmjclahbmngntku
```

### Schema Tabelle Complete

#### users
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR UNIQUE NOT NULL,
    password VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### user_preferences
```sql
CREATE TABLE user_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES users(id),
    dark_mode BOOLEAN DEFAULT FALSE,
    language VARCHAR DEFAULT 'it',
    notifications BOOLEAN DEFAULT TRUE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### wishlist (Schema Supabase - QUESTO È QUELLO ATTIVO)
```sql
CREATE TABLE wishlist (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    nome VARCHAR NOT NULL,
    descrizione TEXT,
    link VARCHAR,
    priorita VARCHAR DEFAULT 'media',
    pubblico BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
**NOTA CRITICA**: NON esiste `titolo`, `prezzo`, `acquistato`. Usa `nome`, `link`, `pubblico`.

#### pasti
```sql
CREATE TABLE pasti (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    data DATE NOT NULL,
    tipo_pasto VARCHAR NOT NULL,
    descrizione TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### allenamenti
```sql
CREATE TABLE allenamenti (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    data DATE NOT NULL,
    esercizio VARCHAR NOT NULL,
    ripetizioni INTEGER,
    peso NUMERIC,
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### workout_sessions
```sql
CREATE TABLE workout_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    data DATE NOT NULL,
    workout_type VARCHAR NOT NULL,
    completato BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### workout_exercises
```sql
CREATE TABLE workout_exercises (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES workout_sessions(id),
    esercizio VARCHAR NOT NULL,
    serie_numero INTEGER,
    ripetizioni INTEGER,
    peso NUMERIC,
    note TEXT
);
```

#### GAME PRIZE - 10 Tabelle

##### game_prize_config
```sql
CREATE TABLE game_prize_config (
    id SERIAL PRIMARY KEY,
    game_name VARCHAR DEFAULT 'Premio di Compleanno',
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    total_challenges INTEGER DEFAULT 12,
    max_participants INTEGER DEFAULT 100,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

##### game_challenges
```sql
CREATE TABLE game_challenges (
    id SERIAL PRIMARY KEY,
    challenge_number INTEGER NOT NULL,
    title VARCHAR NOT NULL,
    description TEXT,
    points INTEGER DEFAULT 100,
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    location VARCHAR,
    instructions TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

##### game_clues
```sql
CREATE TABLE game_clues (
    id SERIAL PRIMARY KEY,
    challenge_id INTEGER REFERENCES game_challenges(id),
    clue_number INTEGER NOT NULL,
    clue_text TEXT NOT NULL,
    revealed_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

##### game_user_completions
```sql
CREATE TABLE game_user_completions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    challenge_id INTEGER REFERENCES game_challenges(id),
    completed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, challenge_id)
);
```

##### game_user_scores
```sql
CREATE TABLE game_user_scores (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    challenge_id INTEGER REFERENCES game_challenges(id),
    points INTEGER NOT NULL,
    awarded_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

##### game_winner_reveal
```sql
CREATE TABLE game_winner_reveal (
    id SERIAL PRIMARY KEY,
    revealed BOOLEAN DEFAULT FALSE,
    revealed_date TIMESTAMP,
    winner_user_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

##### game_participants
```sql
CREATE TABLE game_participants (
    id SERIAL PRIMARY KEY,
    code VARCHAR UNIQUE NOT NULL,
    user_id INTEGER REFERENCES users(id),
    registered_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

##### game_clue_solutions
```sql
CREATE TABLE game_clue_solutions (
    id SERIAL PRIMARY KEY,
    clue_id INTEGER REFERENCES game_clues(id),
    solution_text VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

##### game_clue_completions
```sql
CREATE TABLE game_clue_completions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    clue_id INTEGER REFERENCES game_clues(id),
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, clue_id)
);
```

##### game_attempt_logs
```sql
CREATE TABLE game_attempt_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    clue_id INTEGER REFERENCES game_clues(id),
    attempted_solution VARCHAR,
    success BOOLEAN,
    attempt_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔧 VARIABILI D'AMBIENTE RENDER

```bash
DATABASE_URL=postgresql://postgres.wuvuapmjclahbmngntku:n5x8%25XnUK5xMWnV5qWg6@aws-1-eu-north-1.pooler.supabase.com:6543/postgres
SECRET_KEY=3a5c60705938cc71d56fe604e7f0b4fad686e37a08eef519
DEBUG=False
```

**VERIFICARE SEMPRE** che DATABASE_URL punti a Supabase, NON a Render PostgreSQL vecchio.

---

## 🚨 ERRORI PASSATI E COME EVITARLI

### ERRORE 1: Migrazione Supabase → Render (Ottobre 2025)
**Cosa successe**:
- Migrato database da Supabase a Render PostgreSQL
- **PERSI TUTTI I DATI** incluse credenziali utente
- Schema rimasto inconsistente

**Lezione**: NON migrare database senza backup completo e piano di rollback.

### ERRORE 2: Schema Wishlist Inconsistente (Novembre 2025)
**Cosa successe**:
- Codice Python modificato per usare `nome` invece di `titolo`
- Database Render aveva ancora schema vecchio
- Sito ROTTO in produzione

**Lezione**:
- SEMPRE verificare schema database PRIMA di modificare codice
- SEMPRE testare in locale con schema identico a produzione
- MAI pushare senza test

### ERRORE 3: Column "peso_s1" Does Not Exist
**Cosa successe**:
- Query fitness usava nomi colonne inesistenti
- Errore 500 in produzione

**Lezione**:
- Usare nomi colonne corretti: `peso`, `ripetizioni` (senza suffissi)
- Verificare query con EXPLAIN prima di deploy

---

## 📋 WORKFLOW OBBLIGATORIO

### Per QUALSIASI Modifica

```
1. LETTURA (5 min)
   - Leggi questo file completamente
   - Leggi documentazione specifica del modulo

2. VERIFICA DATABASE (2 min)
   - Connetti a Supabase
   - Verifica schema tabelle coinvolte:
     SELECT column_name, data_type
     FROM information_schema.columns
     WHERE table_name = 'nome_tabella'

3. ANALISI (3 min)
   - Identifica cosa va modificato
   - Verifica se serve migrazione DB o modifica codice

4. PROPOSTA ALL'UTENTE (OBBLIGATORIO)
   - Spiega situazione attuale
   - Proponi soluzione dettagliata
   - ASPETTA CONFERMA
   - NON procedere senza OK esplicito

5. TEST LOCALE (10 min)
   - Configura DATABASE_URL locale a Supabase
   - Testa modifiche
   - Verifica funzionamento
   - Fix eventuali errori

6. DEPLOY (solo dopo OK utente)
   - Commit descrittivo
   - Push
   - Monitora deploy su Render (2-3 min)
   - Verifica sito produzione
   - Controlla logs per errori
```

### Checklist Pre-Commit

- [ ] Ho letto _CLAUDE_READ_FIRST.md?
- [ ] Ho verificato schema database Supabase?
- [ ] Ho testato in locale?
- [ ] Ho ricevuto OK dall'utente?
- [ ] Il commit message è descrittivo?

**Se anche UNA risposta è NO: FERMATI e completa il passo mancante.**

---

## 🎮 GAME PRIZE - INFORMAZIONI CRITICHE

### Date Chiave
- **Inizio**: 25 Gennaio 2026 00:00 (Domenica)
- **Fine**: 25 Gennaio 2027 00:00 (Lunedì)
- **Festa Premiazione**: 30 Gennaio 2027 (Venerdì)

### Parametri
- Premio: €500
- Partecipanti: ~50
- Sfide: 13 (12 sabati + 1 domenica finale)
- Codici univoci: 100 (GP2026-0001 a GP2026-0100)

### Password Admin
- Password Game Prize: `The Game`
- Route: `/game-prize/admin/welcome`

### Sistema Punteggi
- Sfide: 500-50 punti (1° a ultimo)
- Indizi: 100-10 punti (1° a ultimo)
- Bonus compleanno: 200 punti
- Soglia finale: 4,500 punti

### Tabelle Game Prize (10 totali)
Vedi sezione DATABASE sopra per schema completo.

### Migrazione Game Prize
File: `migrations/apply_game_prize_v2.py`
**NON eseguire** senza conferma utente - fa DROP CASCADE di tabelle esistenti.

---

## 🛠️ COMANDI UTILI

### Connessione Database Supabase
```bash
# Via MCP Supabase (se disponibile)
# Oppure via psql:
PGPASSWORD='n5x8%XnUK5xMWnV5qWg6' psql -h aws-1-eu-north-1.pooler.supabase.com -p 6543 -U postgres.wuvuapmjclahbmngntku -d postgres
```

### Verifica Schema Tabella
```sql
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'wishlist'
ORDER BY ordinal_position;
```

### Verifica DATABASE_URL Render
```bash
# Via MCP Render
render env srv-d3of691r0fns73c5t110 | grep DATABASE_URL
```

### Deploy Manuale
```bash
cd Desktop/Piattaforma
git add .
git commit -m "Descrizione modifiche"
git push origin main
# Render auto-deploya in ~2-3 minuti
```

### Logs Produzione
```bash
# Via Render dashboard
https://dashboard.render.com/web/srv-d3of691r0fns73c5t110

# O via API
curl -H "Authorization: Bearer rnd_VIWjnZZkLnc7bfd0GHPSmzt7V838" \
  "https://api.render.com/v1/services/srv-d3of691r0fns73c5t110/logs?limit=100"
```

---

## 🔑 CREDENZIALI COMPLETE

### Render
- API Key: `rnd_VIWjnZZkLnc7bfd0GHPSmzt7V838`
- Service ID: `srv-d3of691r0fns73c5t110`
- Dashboard: https://dashboard.render.com

### Supabase
- Project ID: `wuvuapmjclahbmngntku`
- Password: `n5x8%XnUK5xMWnV5qWg6`
- Dashboard: https://supabase.com/dashboard/project/wuvuapmjclahbmngntku
- API Key (anon): `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

### GitHub
- Repository: https://github.com/Matteo-Zaramella/Piattaforma
- Branch: main
- Auto-deploy: Attivo

### Cloudflare
- API Token: `BV4VRnluBBc2zslf5NpmwKGw5CFloEY5E_Zls7D0`
- Zone ID: `fa6d2990c04ceae6905ef3a01e06bd10`
- Dominio: matteozaramella.com

---

## 📁 STRUTTURA FILE PROGETTO

```
Piattaforma/
├── _CLAUDE_READ_FIRST.md       ⭐ QUESTO FILE - LEGGI SEMPRE
├── app.py                       # Main Flask app
├── requirements.txt
├── render.yaml
│
├── modules/                     # Blueprint Flask
│   ├── fitness.py              ✅ Attivo
│   ├── settings.py             ✅ Attivo
│   ├── wishlist.py             ✅ Attivo
│   ├── game_prize.py           ✅ Attivo - PRIORITÀ
│   ├── location.py             ❌ Da rimuovere
│   └── appointments.py         ❌ Da rimuovere
│
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── dashboard.html
│   ├── fitness/
│   ├── wishlist/
│   ├── game_prize/
│   ├── settings/
│   ├── location/               ❌ Da rimuovere
│   └── appointments/           ❌ Da rimuovere
│
├── static/
│   └── css/
│       └── style.css
│
└── migrations/
    ├── apply_game_prize_v2.py
    ├── apply_to_render.py
    └── *.sql
```

---

## 🎯 PROSSIMI PASSI (Post-Cleanup)

### Immediati
1. ✅ Compattare documentazione (questo file)
2. ⏳ Ripristinare DATABASE_URL a Supabase
3. ⏳ Rimuovere moduli: location, appointments
4. ⏳ Verificare Game Prize funzionante
5. ⏳ Testare wishlist

### Futuri
- Google Calendar integration
- Push notifications
- Todo app avanzata

---

## ⚠️ REGOLE ASSOLUTE

1. **SEMPRE leggere questo file** prima di qualsiasi azione
2. **MAI modificare database** senza verificare schema
3. **MAI pushare** senza test locale
4. **SEMPRE chiedere conferma** prima di modifiche importanti
5. **MAI assumere** - SEMPRE verificare

### Se In Dubbio
1. FERMATI
2. Leggi questo file
3. Verifica database
4. Chiedi all'utente

---

## 📞 SUPPORTO

### Dashboard Utili
- Render: https://dashboard.render.com
- Supabase: https://supabase.com/dashboard
- GitHub: https://github.com/Matteo-Zaramella/Piattaforma
- Produzione: https://matteozaramella.com

### Documentazione
- Flask: https://flask.palletsprojects.com/
- Bootstrap: https://getbootstrap.com/
- Render: https://render.com/docs

---

**RICORDA**: Questo file contiene TUTTE le informazioni necessarie. Non serve leggere altri 45 file. Tutto è qui.

**ULTIMA REGOLA**: Se non hai letto COMPLETAMENTE questo file, NON procedere con nessuna modifica.

---

*Creato: 3 Novembre 2025*
*Versione: 1.0*
*Scopo: Evitare errori e perdite di dati*
