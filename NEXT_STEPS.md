# 🚀 PROSSIMI PASSI - Piattaforma

**Data creazione**: 2025-10-17 (Sessione 1)
**Ultimo aggiornamento**: 2025-10-17 (Sessione 2)

---

## ✅ COMPLETATO: Errore 500 Risolto!

### Problema (RISOLTO)
Il sito caricava ma la registrazione utenti falliva con Internal Server Error 500.

### Causa Identificata
1. `psycopg2-binary` con versione specifica non si installava → Risolto usando `psycopg2-binary` senza versione
2. Connection string Supabase errata → Hostname pooler sbagliato (`aws-0-eu-central-1` invece di `aws-1-eu-north-1`)

### Soluzione Applicata
- ✅ Aggiornato `requirements.txt` con `psycopg2-binary` (senza versione)
- ✅ Corretto hostname pooler: `aws-1-eu-north-1.pooler.supabase.com`
- ✅ Database inizializzato con successo
- ✅ Registrazione e login funzionanti

---

## 🎯 PRIORITÀ ATTUALE

### 1. Rimuovi Endpoint `/init-database-tables` (Sicurezza) ⚠️

**Problema**: L'endpoint `/init-database-tables` è pubblico e chiunque può chiamarlo.

**Azione**:
Apri `app.py` e rimuovi o proteggi l'endpoint (linee 467-474 circa):

**Opzione A - Rimuovi** (consigliato):
```python
# Commenta o elimina queste righe
# @app.route('/init-database-tables')
# def init_database_tables():
#     ...
```

**Opzione B - Proteggi con password**:
```python
@app.route('/init-database-tables')
def init_database_tables():
    password = request.args.get('password')
    if password != 'SECRET_PASSWORD_QUI':
        return jsonify({'error': 'Unauthorized'}), 401
    try:
        init_db()
        return jsonify({'success': True, 'message': 'Database inizializzato con successo!'}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
```

Poi commit e push.

### 2. Test Persistenza Dati

**Importante**: Verifica che i dati sopravvivano al sleep di Render

1. Registra un utente reale su https://matteozaramella.com
2. Aggiungi alcuni dati (scommessa, task, etc.)
3. **Aspetta 20-30 minuti** (Render Free va in sleep dopo inattività)
4. Riapri il sito e fai login
5. Verifica che tutti i dati ci siano ancora ✅

### 3. Test Completo

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
