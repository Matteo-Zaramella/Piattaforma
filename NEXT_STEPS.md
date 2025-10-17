# 🚀 PROSSIMI PASSI - Piattaforma

**Data creazione**: 2025-10-17 (Sessione 1)

---

## 🔴 PRIORITÀ MASSIMA: Fixare Errore 500

### Problema
Il sito carica ma la registrazione utenti fallisce con Internal Server Error 500.

### Causa
`psycopg2` non viene installato correttamente su Render nonostante sia in `requirements.txt`

### Soluzioni da Provare (in ordine)

#### Soluzione 1: Attendere deploy in corso ⏳
**Status**: Deploy `4d42174` in corso (psycopg2-binary senza versione)

**Azione**:
1. Aspetta che deploy completi
2. Testa endpoint: `curl https://matteozaramella.com/init-database-tables`
3. Se ritorna `{"success": true}` → Problema risolto!
4. Se ritorna ancora errore psycopg2 → Prova Soluzione 2

#### Soluzione 2: Aggiungi dipendenze di sistema
**Problema**: Render potrebbe non avere libpq-dev necessario per psycopg2

**Azione**:
1. Crea file `render.yaml`:
```yaml
services:
  - type: web
    name: piattaforma
    env: python
    buildCommand: apt-get update && apt-get install -y libpq-dev && pip install -r requirements.txt
    startCommand: gunicorn app:app
```

2. Commit e push:
```bash
cd C:\Users\offic\Desktop\Piattaforma
git add render.yaml
git commit -m "Add render.yaml con libpq-dev"
git push
```

#### Soluzione 3: Usa Aptfile (Render buildpack)
**Azione**:
1. Crea file `Aptfile` (senza estensione):
```
libpq-dev
```

2. Commit e push:
```bash
git add Aptfile
git commit -m "Add Aptfile per libpq-dev"
git push
```

#### Soluzione 4: Verifica logs build
**Azione**:
```bash
# Ottieni ultimo deploy ID
curl -H "Authorization: Bearer rnd_VIWjnZZkLnc7bfd0GHPSmzt7V838" "https://api.render.com/v1/services/srv-d3of691r0fns73c5t110/deploys?limit=1" | grep '"id"'

# Cerca errori build (sostituisci DEPLOY_ID)
# Logs non disponibili via API - vai su dashboard Render manualmente
```

**Dashboard Render**: https://dashboard.render.com/web/srv-d3of691r0fns73c5t110

Cerca tab "Logs" o "Events" per vedere errori installazione pip

#### Soluzione 5: Fallback a SQLite temporaneo
**Se nulla funziona**, usa temporaneamente SQLite:

```bash
# Rimuovi DATABASE_URL da Render env vars
curl -X DELETE -H "Authorization: Bearer rnd_VIWjnZZkLnc7bfd0GHPSmzt7V838" "https://api.render.com/v1/services/srv-d3of691r0fns73c5t110/env-vars/DATABASE_URL"
```

**Problema**: Dati non persistono (ephemeral filesystem)
**Usa solo come test temporaneo**

---

## ✅ DOPO Risolto Errore 500

### Step 1: Inizializza Tabelle Supabase

**Endpoint creato**: `/init-database-tables`

```bash
curl https://matteozaramella.com/init-database-tables
```

**Output atteso**:
```json
{"success": true, "message": "Database inizializzato con successo!"}
```

Se errore, esegui init manualmente (vedi sotto)

### Step 2: Test Registrazione Utente

```bash
# Registra utente test
curl -X POST https://matteozaramella.com/register \
  -d "username=testuser&password=testpass123" \
  -L -i

# Dovrebbe ritornare redirect (302) a /login
```

### Step 3: Test Completo

1. Apri browser su: https://matteozaramella.com
2. Registra account reale
3. Logout
4. Login di nuovo
5. Aggiungi dati (scommessa, task, etc.)
6. **ASPETTA 20 MINUTI** (Render va in sleep)
7. Riapri sito e fai login
8. Verifica che **dati ci siano ancora** ✅

### Step 4: Rimuovi Endpoint Temporaneo

**Sicurezza**: `/init-database-tables` è pubblico!

**Azione**:
1. Apri `app.py`
2. Rimuovi o commenta:
```python
@app.route('/init-database-tables')
def init_database_tables():
    ...
```

3. Oppure aggiungi password protection:
```python
@app.route('/init-database-tables')
def init_database_tables():
    password = request.args.get('password')
    if password != 'SECRET_PASSWORD_QUI':
        return jsonify({'error': 'Unauthorized'}), 401
    ...
```

### Step 5: Aggiorna Moduli Rimanenti

File da aggiornare per PostgreSQL:
- `modules/task_lavoro.py`
- `modules/task_privati.py`
- `modules/fitness.py`
- `modules/settings.py`

**Azione**: Usa stesso pattern di `matched_betting.py`:

```python
# Prima riga del file
from db_utils import get_db, execute_query, USE_POSTGRES

# Sostituisci db.execute() con execute_query()
# Esempio:
# Prima:
db = get_db()
result = db.execute('SELECT * FROM table WHERE id = ?', (id,)).fetchone()

# Dopo:
conn = get_db()
result = execute_query(conn, 'SELECT * FROM table WHERE id = ?', (id,), fetch_one=True)
```

---

## 📊 Inizializzazione Manuale Database Supabase

Se `/init-database-tables` non funziona, esegui SQL manualmente:

### Via Dashboard Supabase

1. Vai su: https://supabase.com/dashboard/project/wuvuapmjclahbmngntku
2. Click **SQL Editor** (sidebar sinistra)
3. Click **New query**
4. Copia SQL da `app.py` funzione `init_db()` (righe 72-221 circa)
5. **Sostituisci**:
   - `INTEGER PRIMARY KEY AUTOINCREMENT` → `SERIAL PRIMARY KEY`
   - `TEXT` → `VARCHAR`
   - `BOOLEAN DEFAULT 0` → `BOOLEAN DEFAULT FALSE`
6. Esegui query

### SQL Rapido (Tabella Users esempio)

```sql
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR UNIQUE NOT NULL,
    password VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Ripeti per tutte le tabelle: matched_betting, task_lavoro, task_privati, pasti, allenamenti, workout_sessions, workout_exercises, user_preferences

---

## 🔄 Workflow Mantenimento

### Ogni Volta che Modifichi Codice

```bash
cd C:\Users\offic\Desktop\Piattaforma

# 1. Test locale (opzionale)
python app.py  # Testa su localhost:5000

# 2. Commit
git add .
git commit -m "Descrizione modifiche"
git push origin main

# 3. Render fa auto-deploy (aspetta 2-3 min)

# 4. Verifica
curl https://matteozaramella.com
```

### Backup Database Periodico

**Ogni settimana** (raccomandato):

1. Dashboard Supabase: https://supabase.com/dashboard/project/wuvuapmjclahbmngntku
2. Database → Backups
3. Download backup manuale
4. Salva in cloud storage (OneDrive/Google Drive)

### Monitoraggio

**Settimanale**:
- Verifica sito funzionante: https://matteozaramella.com
- Check Supabase usage: Dashboard → Settings → Usage

**Mensile**:
- Review Render logs per errori
- Update dipendenze Python se necessario

---

## 🎯 Prossime Funzionalità (Opzionali)

### Fase 2: Miglioramenti UX

1. **Dashboard migliorata** con statistiche grafiche
2. **Export dati** (CSV, JSON)
3. **Filtri avanzati** per task e scommesse
4. **Notifiche email** per scadenze

### Fase 3: Sicurezza

1. **2FA** (autenticazione a due fattori)
2. **Rate limiting** su login
3. **IP whitelist** via Cloudflare
4. **Backup automatici** daily

### Fase 4: Nuovi Moduli

1. **Finanze** - Tracking entrate/uscite
2. **Note** - Sistema note personali
3. **Calendario integrato** - Eventi e scadenze
4. **API** - Endpoint REST per app mobile

---

## ⚡ Comandi Rapidi

```bash
# Deploy manuale (forza rebuild)
curl -X POST -H "Authorization: Bearer rnd_VIWjnZZkLnc7bfd0GHPSmzt7V838" -H "Content-Type: application/json" -d '{"clearCache":"clear"}' "https://api.render.com/v1/services/srv-d3of691r0fns73c5t110/deploys"

# Stato servizio
curl -H "Authorization: Bearer rnd_VIWjnZZkLnc7bfd0GHPSmzt7V838" "https://api.render.com/v1/services/srv-d3of691r0fns73c5t110"

# Test init database
curl https://matteozaramella.com/init-database-tables

# Test registrazione
curl -X POST https://matteozaramella.com/register -d "username=test&password=test"
```

---

## 📝 Note per Claude Futuro

**Quando leggi questo file**:

1. Controlla sempre `STATUS.md` prima
2. Verifica MCP connettori funzionanti: `claude mcp list`
3. Segui soluzioni in ordine (non saltare step)
4. Aggiorna questo file dopo ogni progresso
5. Aggiungi note su cosa hai provato e risultati

**Pattern Git Commit**:
```
Titolo breve azione

Dettagli cosa è stato modificato e perché

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

**Ultimo aggiornamento**: 2025-10-17 14:45 (Fine Sessione 1)

**Prossima azione**: Verificare deploy `4d42174` e testare `/init-database-tables`
