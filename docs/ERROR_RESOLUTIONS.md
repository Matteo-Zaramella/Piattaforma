# 🔧 Error Resolutions - Piattaforma

Documentazione completa di tutti gli errori riscontrati e le relative soluzioni automatiche.

**Ultimo aggiornamento:** 30 Ottobre 2025

---

## 📋 Indice

1. [Errori Database](#errori-database)
2. [Errori 500 Server](#errori-500-server)
3. [Errori Migration](#errori-migration)
4. [Errori Deployment](#errori-deployment)
5. [Procedure Diagnostica](#procedure-diagnostica)

---

## 🗄️ Errori Database

### ERROR 1: Connection Refused - Wrong Database URL

**Sintomo:**
```
psycopg2.OperationalError: connection to server at "aws-1-eu-north-1.pooler.supabase.com" (51.21.18.29), port 5432 failed: Connection refused
```

**Causa:**
DATABASE_URL punta al database sbagliato (es. Supabase invece di Render)

**Diagnosi Automatica:**
```bash
# Controlla logs Render
render logs srv-d3of691r0fns73c5t110 | grep "Connection refused"

# Verifica DATABASE_URL configurata
render env srv-d3of691r0fns73c5t110 | grep DATABASE_URL
```

**Risoluzione Automatica:**
```python
# Aggiorna DATABASE_URL su Render
from mcp import render
render.update_environment_variables(
    serviceId="srv-d3of691r0fns73c5t110",
    envVars=[{
        "key": "DATABASE_URL",
        "value": "postgresql://piattaforma_user:PASSWORD@dpg-d3ogka1r0fns73c7230g-a.oregon-postgres.render.com/piattaforma"
    }]
)
# Questo triggera automaticamente un nuovo deploy
```

**Prevenzione:**
- DATABASE_URL deve sempre puntare a Render PostgreSQL (stesso datacenter)
- Verificare DATABASE_URL ad ogni deploy problematico
- Aggiungere health check che verifica connessione DB all'avvio

---

### ERROR 2: Table Does Not Exist

**Sintomo:**
```
psycopg2.errors.UndefinedTable: relation "users" does not exist
```

**Causa:**
Database vuoto o migration non applicata

**Diagnosi Automatica:**
```sql
-- Connetti a PostgreSQL e verifica tabelle
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;
```

**Risoluzione Automatica:**
```bash
# Applica schema completo
cd migrations
python apply_to_render.py

# Oppure con psql
psql $DATABASE_URL -f migrations/create_all_tables.sql
```

**Tabelle Richieste (17 totali):**
- `users` - Utenti sistema
- `pasti` - Tracciamento pasti
- `allenamenti` - Workout legacy
- `workout_sessions` - Sessioni workout
- `workout_exercises` - Esercizi workout
- `wishlist` - Lista desideri
- `settings` - Configurazione utente
- `game_participants` - Partecipanti Game Prize (100 codici)
- `game_challenges` - Sfide (13 totali)
- `game_clues` - Indizi puzzle
- `game_clue_solutions` - Soluzioni indizi
- `game_clue_completions` - Completamenti indizi
- `game_detailed_scores` - Punteggi dettagliati
- `game_user_completions` - Completamenti sfide
- `game_user_scores` - Punteggi utenti
- `game_attempt_logs` - Log tentativi anti-cheat
- `game_prize_config` - Configurazione gioco

---

### ERROR 3: Column Does Not Exist

**Sintomo:**
```
psycopg2.errors.UndefinedColumn: column "peso_s1" does not exist
```

**Causa:**
Query usa nomi colonne vecchi/sbagliati

**Diagnosi Automatica:**
```sql
-- Verifica schema tabella
\d+ workout_exercises

-- Colonne corrette:
-- peso (NUMERIC)
-- ripetizioni (INTEGER)
```

**Risoluzione:**
Modificare query per usare nomi corretti:
```python
# SBAGLIATO:
AVG(NULLIF(we.peso_s1, '')::NUMERIC)

# CORRETTO:
AVG(we.peso) as avg_peso
MAX(we.peso) as max_peso
MAX(we.ripetizioni) as record_rip
```

**File da controllare:**
- `modules/fitness.py` - Tutte le query statistiche
- `modules/game_prize.py` - Query sfide

---

## 🔴 Errori 500 Server

### ERROR 4: Generic 500 Internal Server Error

**Diagnosi Step-by-Step:**

1. **Controlla logs Render immediatamente:**
```bash
render logs srv-d3of691r0fns73c5t110 --tail 100
```

2. **Identifica il traceback:**
   - Cerca `ERROR in app:`
   - Leggi lo stack trace per identificare file e linea
   - Identifica l'exception type (psycopg2.OperationalError, KeyError, etc.)

3. **Categorie comuni 500:**
   - **Database**: Connection refused, table missing, column missing
   - **Template**: Variabile undefined, filter error
   - **Session**: Session expired, invalid session data
   - **Import**: Module not found, circular import

**Risoluzione Generale:**
```python
# Aggiungi try-except robusti in tutte le route
@app.route('/route')
def route():
    try:
        # Codice principale
        pass
    except psycopg2.OperationalError as e:
        app.logger.error(f"Database error: {e}")
        flash("Errore di connessione database. Riprova.", "danger")
        return redirect(url_for('index'))
    except Exception as e:
        app.logger.error(f"Unexpected error: {e}")
        flash("Errore interno. Contatta l'amministratore.", "danger")
        return redirect(url_for('index'))
```

---

### ERROR 5: Template Rendering Error

**Sintomo:**
```
jinja2.exceptions.UndefinedError: 'None' has no attribute 'clues'
```

**Causa:**
Variabili non passate al template o struttura dati errata

**Risoluzione:**
```python
# SEMPRE verificare dati prima di passare al template
challenges_with_clues = []
for challenge in challenges:
    challenges_with_clues.append({
        'challenge': challenge,
        'clues': clues or [],  # Default a lista vuota
        'solutions': solutions or []
    })

return render_template('template.html',
                      challenges_with_clues=challenges_with_clues)
```

**Template Safety:**
```jinja2
{# SEMPRE usa default e safe checks #}
{% if challenges_with_clues %}
    {% for item in challenges_with_clues %}
        {% set clues = item.clues|default([]) %}
        {% if clues %}
            {# Mostra indizi #}
        {% else %}
            <p>Nessun indizio</p>
        {% endif %}
    {% endfor %}
{% endif %}
```

---

## 🔄 Errori Migration

### ERROR 6: Migration Already Applied

**Sintomo:**
```
ERROR: relation "game_challenges" already exists
```

**Causa:**
Migration eseguita più volte

**Risoluzione:**
```sql
-- Usa sempre IF NOT EXISTS o DROP CASCADE
DROP TABLE IF EXISTS game_challenges CASCADE;
CREATE TABLE game_challenges (...);

-- Oppure verifica prima:
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables
                   WHERE table_name = 'game_challenges') THEN
        CREATE TABLE game_challenges (...);
    END IF;
END $$;
```

---

### ERROR 7: Foreign Key Violation

**Sintomo:**
```
ERROR: insert or update on table "game_clues" violates foreign key constraint
```

**Causa:**
Tentativo di inserire dati con FK che non esiste

**Risoluzione:**
```sql
-- ORDINE CORRETTO creazione tabelle (parent prima):
CREATE TABLE game_challenges (...);  -- Parent
CREATE TABLE game_clues (            -- Child
    challenge_id INTEGER REFERENCES game_challenges(id) ON DELETE CASCADE
);

-- ORDINE CORRETTO inserimento dati:
INSERT INTO game_challenges VALUES (...);  -- Prima parent
INSERT INTO game_clues VALUES (...);       -- Poi child
```

---

## 📦 Errori Deployment

### ERROR 8: Build Failed - Module Not Found

**Sintomo:**
```
ModuleNotFoundError: No module named 'psycopg2'
```

**Causa:**
Dipendenza mancante in requirements.txt

**Risoluzione:**
```bash
# Verifica requirements.txt contiene:
Flask==3.0.0
psycopg2-binary==2.9.9
gunicorn==21.2.0
python-dotenv==1.0.0

# Rebuild su Render triggera automaticamente
git add requirements.txt
git commit -m "fix: Add missing dependencies"
git push
```

---

### ERROR 9: Deploy Timeout

**Sintomo:**
Deploy rimane stuck in "build_in_progress" per >10 minuti

**Diagnosi:**
```bash
# Controlla build logs
render logs srv-d3of691r0fns73c5t110 --deploy dep-XXXXX

# Verifica status deploy
render deploys srv-d3of691r0fns73c5t110 --limit 1
```

**Risoluzione:**
1. Aspetta max 15 minuti (Render free tier può essere lento)
2. Se ancora stuck, cancella deploy e triggerane uno nuovo:
```bash
render deploy cancel dep-XXXXX
git commit --allow-empty -m "trigger: Force redeploy"
git push
```

---

## 🔍 Procedure Diagnostica

### Procedura Standard per Errore 500

**STEP 1: Recupera Logs (5 secondi)**
```bash
render logs srv-d3of691r0fns73c5t110 --tail 50 | grep ERROR
```

**STEP 2: Identifica Categoria (10 secondi)**
- Contiene "psycopg2" → Errore Database
- Contiene "jinja2" → Errore Template
- Contiene "KeyError" → Variabile mancante
- Contiene "ImportError" → Modulo mancante

**STEP 3: Applica Fix Specifico (2 minuti)**
- Vedi sezione specifica sopra

**STEP 4: Test Locale Prima di Deploy (2 minuti)**
```bash
# Test locale SEMPRE prima di push
export DATABASE_URL="postgresql://..."
python app.py

# Verifica route problematica
curl http://localhost:5000/route-con-errore
```

**STEP 5: Deploy e Verifica (3 minuti)**
```bash
git add .
git commit -m "fix: [descrizione errore risolto]"
git push

# Aspetta deploy
sleep 120

# Verifica fix
curl https://piattaforma.onrender.com/route-con-errore
```

---

### Checklist Pre-Deploy (SEMPRE!)

Esegui SEMPRE prima di ogni `git push`:

- [ ] `python app.py` funziona in locale
- [ ] Tutte le route critiche testate (login, dashboard, game_prize)
- [ ] DATABASE_URL corretto in `.env` locale
- [ ] `requirements.txt` aggiornato con nuove dipendenze
- [ ] Nessun print() o debug code dimenticato
- [ ] Commit message descrittivo con emoji

---

### Diagnostica Database Remoto

**Connessione Rapida:**
```bash
# Via psql
psql postgresql://piattaforma_user:PASSWORD@dpg-d3ogka1r0fns73c7230g-a.oregon-postgres.render.com/piattaforma

# Via Python
python migrations/apply_to_render.py --verify-only
```

**Query Diagnostiche:**
```sql
-- Conta tutte le tabelle
SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';
-- Deve essere 17

-- Verifica utenti
SELECT COUNT(*) FROM users;

-- Verifica sfide Game Prize
SELECT COUNT(*) FROM game_challenges;
-- Deve essere 13

-- Verifica codici partecipanti
SELECT COUNT(*) FROM game_participants;
-- Deve essere 100

-- Verifica date sfide (devono essere sabati)
SELECT challenge_number,
       TO_CHAR(start_date, 'DD/MM/YYYY') as data,
       TO_CHAR(start_date, 'Day') as giorno
FROM game_challenges
ORDER BY challenge_number;
```

---

## 🚨 Errori Critici che Richiedono Intervento Immediato

### CRITICAL 1: Database Completamente Inaccessibile

**Sintomo:** Tutti gli accessi falliscono, site down

**Azione:**
1. Verifica status database Render: https://dashboard.render.com/d/dpg-d3ogka1r0fns73c7230g-a
2. Se database è "suspended" o "unavailable", contatta Render support
3. Se IP allow list bloccata, aggiungi `0.0.0.0/0`

---

### CRITICAL 2: Perdita Dati Utente

**Sintomo:** Tabella `users` vuota o corrotta

**Azione:**
```sql
-- Backup immediato se dati ancora presenti
pg_dump $DATABASE_URL > backup_emergency_$(date +%Y%m%d).sql

-- Verifica integrità
SELECT COUNT(*) FROM users;

-- Se serve restore, usa backup più recente
psql $DATABASE_URL < backup_YYYYMMDD.sql
```

**Prevenzione:**
- Backup automatico settimanale (TODO: implementare)
- Non fare mai DROP senza CASCADE consapevole

---

## 📚 Risorse Utili

- **Render Dashboard:** https://dashboard.render.com/
- **PostgreSQL Render:** https://dashboard.render.com/d/dpg-d3ogka1r0fns73c7230g-a
- **Web Service Logs:** https://dashboard.render.com/web/srv-d3of691r0fns73c5t110
- **GitHub Repo:** https://github.com/Matteo-Zaramella/Piattaforma

---

## 🔄 Changelog Errori Risolti

### 30 Ottobre 2025
- ✅ **ERROR 1**: DATABASE_URL puntava a Supabase invece di Render → Aggiornato env var
- ✅ **ERROR 2**: Database vuoto → Applicato schema completo 17 tabelle
- ✅ **ERROR 3**: Column `peso_s1` doesn't exist → Fixed query in `fitness.py`
- ✅ **ERROR 5**: Template undefined variable in `admin_dashboard.html` → Fixed data structure

---

**Documento Vivo:** Aggiornare questo file ad ogni nuovo errore riscontrato e risolto.
