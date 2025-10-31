# 🚀 Checklist Scalabilità e Stabilità - 1000 Utenti Simultanei

**Target:** 1000 utenti collegati contemporaneamente
**Periodo critico:** 25 Gennaio 2026 - 25 Gennaio 2027
**Data:** 31 Ottobre 2025

---

## 🔴 PROBLEMI CRITICI ATTUALI

### 1. **Piano Render FREE - INSUFFICIENTE** ⚠️
**Problema:**
- Piano attuale: **FREE**
- Limiti FREE tier:
  - CPU condivisa limitata
  - 512MB RAM
  - Spin down dopo 15 min inattività (richiede 30-60 sec per riavvio)
  - 750 ore/mese (poi si spegne)
  - Nessuna autoscaling
  - 1 istanza singola (no load balancing)

**Con 1000 utenti simultanei:**
- ❌ Sito andrà in crash immediato
- ❌ Timeout su tutte le richieste
- ❌ 502 Bad Gateway costanti
- ❌ Database connections esaurite

**SOLUZIONE OBBLIGATORIA:**
```
Upgrade a Piano STARTER (minimo) o PRO
- Starter: $7/mese - 512MB RAM, sempre attivo, no spin-down
- Standard: $25/mese - 2GB RAM, better CPU
- Pro: $85/mese - 4GB RAM, autoscaling disponibile
```

**Raccomandazione:** Piano **Standard ($25/mese)** + Autoscaling

---

### 2. **Database PostgreSQL FREE - SCADE IL 15 NOVEMBRE 2025** 🚨
**Problema:**
- Database attuale: dpg-d3ogka1r0fns73c7230g-a
- Piano: FREE
- **Scadenza: 15 NOVEMBRE 2025** (tra 15 giorni!)
- Dopo scadenza: Database viene cancellato

**SOLUZIONE URGENTE:**
1. **Opzione A - Upgrade Render PostgreSQL** (raccomandato)
   - Basic: $7/mese - 256MB storage (sufficiente per 1000 utenti)
   - Standard: $20/mese - 10GB storage

2. **Opzione B - Migrazione a Supabase** (già configurato)
   - Free tier permanente (500MB, 2GB transfer/mese)
   - Upgrade a Pro: $25/mese (8GB database, 50GB transfer)

**AZIONE RICHIESTA ENTRO 7 GIORNI:**
- Decidere quale database usare
- Fare backup completo
- Upgrade o migrazione

---

### 3. **Connection Pooling Database - NON CONFIGURATO** ⚠️
**Problema:**
- Ogni richiesta apre nuova connessione PostgreSQL
- Con 1000 utenti = 1000+ connessioni simultanee
- Limite PostgreSQL free: 97 connessioni
- Risultato: "too many connections" → errore 500

**SOLUZIONE:**
Implementare **PgBouncer** (connection pooler):
```python
# In app.py - da aggiungere
from psycopg2 import pool

# Connection pool globale
db_pool = pool.ThreadedConnectionPool(
    minconn=5,
    maxconn=20,  # Max 20 connessioni invece di 1000
    dsn=DATABASE_URL
)

def get_db():
    """Ottiene connessione dal pool invece di crearne una nuova"""
    return db_pool.getconn()

def return_db(conn):
    """Restituisce connessione al pool"""
    db_pool.putconn(conn)
```

---

### 4. **Nessuna Cache Implementata** ⚠️
**Problema:**
- Ogni richiesta fa query al database
- Home page fa 4-5 query per ogni utente
- 1000 utenti = 5000 query/secondo al database
- Database va in timeout

**SOLUZIONE:**
Implementare caching con **Redis** o **Flask-Caching**:
```python
# Opzione 1: Redis (raccomandato per produzione)
from flask_caching import Cache

cache = Cache(app, config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': os.environ.get('REDIS_URL')
})

# Opzione 2: Simple memory cache (solo per sviluppo)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Esempio uso:
@app.route('/')
@cache.cached(timeout=300)  # Cache per 5 minuti
def index():
    # Query pesanti vengono eseguite solo ogni 5 minuti
    pass
```

**Render Redis:**
- Starter: $10/mese - 256MB (sufficiente)

---

### 5. **Query Non Ottimizzate** ⚠️
**Problema:**
- Query nella home page caricano troppi dati
- Nessun indice sui campi frequenti
- Uso di ORDER BY senza indici

**SOLUZIONE:**
```sql
-- Aggiungere indici critici
CREATE INDEX idx_wishlist_pubblico ON wishlist(pubblico);
CREATE INDEX idx_appointments_pubblico_data ON appointments(pubblico, data_ora);
CREATE INDEX idx_challenges_start_date ON game_challenges(start_date);
CREATE INDEX idx_location_attivo ON current_location(attivo);

-- Limitare risultati
-- Invece di caricare TUTTA la wishlist:
SELECT * FROM wishlist WHERE pubblico = TRUE LIMIT 10;
```

---

### 6. **Sessioni Utente Non Scalabili** ⚠️
**Problema:**
- Sessioni Flask salvate in memoria server
- Con spin-down Render, sessioni vengono perse
- Con autoscaling, ogni istanza ha sessioni diverse

**SOLUZIONE:**
Usare **Redis Session Store** o **Database Sessions**:
```python
from flask_session import Session

app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.from_url(os.environ['REDIS_URL'])
Session(app)
```

---

### 7. **Nessun Rate Limiting** ⚠️
**Problema:**
- Nessuna protezione contro spam/DOS
- Un utente può fare 1000 richieste/secondo
- API validation indizi senza limiti

**SOLUZIONE:**
Implementare **Flask-Limiter**:
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per hour", "50 per minute"]
)

# API critiche
@app.route('/api/validate-clue', methods=['POST'])
@limiter.limit("10 per minute")  # Max 10 tentativi al minuto
def validate_clue():
    pass
```

---

### 8. **Nessun Monitoring/Alerting** ⚠️
**Problema:**
- Se il sito va down, non lo saprai finché qualcuno non ti avvisa
- Nessun tracking errori 500
- Nessuna visibilità su performance

**SOLUZIONE:**
1. **Render Dashboard** (built-in)
   - Monitoring gratuito basic
   - CPU, Memory, Response Time

2. **Sentry** (error tracking)
   - Free tier: 5000 errors/mese
   - Cattura errori 500 automaticamente
   - Notifiche email/Slack

3. **UptimeRobot** (uptime monitoring)
   - Gratuito per 50 monitor
   - Controlla ogni 5 minuti
   - Notifica via email se down

```python
# Sentry setup
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn=os.environ['SENTRY_DSN'],
    integrations=[FlaskIntegration()],
    traces_sample_rate=0.1  # 10% delle richieste
)
```

---

### 9. **Gunicorn Non Configurato Per Alta Concorrenza** ⚠️
**Problema:**
- Start command: `gunicorn app:app`
- Workers: 1 (default)
- Timeout: 30 sec (default)
- 1 worker può gestire max ~100 richieste simultanee

**SOLUZIONE:**
Configurare Gunicorn per alta concorrenza:
```bash
# In render.yaml o Render Dashboard
gunicorn app:app \
  --workers 4 \
  --threads 2 \
  --worker-class gthread \
  --timeout 120 \
  --keepalive 5 \
  --max-requests 1000 \
  --max-requests-jitter 50
```

**Formula workers:**
```
Workers = (2 x CPU cores) + 1
Piano Standard (2 vCPU) → 5 workers
```

---

### 10. **Static Files Serviti da Flask** ⚠️
**Problema:**
- CSS, JS, immagini serviti da Flask
- Spreca risorse server
- Lento per utenti lontani

**SOLUZIONE:**
Usare **CDN Cloudflare** (già configurato):
```python
# Verificare che Cloudflare Proxy sia ATTIVO
# Dashboard: https://dash.cloudflare.com
# DNS Record per matteozaramella.com → Proxy: ON (arancione)
```

Cloudflare cachea automaticamente:
- CSS, JS (1 anno)
- Immagini (1 mese)
- HTML (no cache, ma con compression)

---

## 📋 CHECKLIST COMPLETA PRE-LANCIO

### INFRASTRUTTURA (CRITICO) 🚨

- [ ] **Upgrade Web Service a Piano Standard** ($25/mese)
  - Render Dashboard → srv-d3of691r0fns73c5t110 → Settings → Plan

- [ ] **Upgrade Database o Migrazione a Supabase** (entro 7 giorni)
  - Opzione A: Upgrade Render DB a Basic ($7/mese)
  - Opzione B: Migra a Supabase (free permanente)

- [ ] **Configurare Gunicorn Workers**
  - Dashboard → Environment → Start Command
  - Aggiungere: `--workers 4 --threads 2 --timeout 120`

- [ ] **Aggiungere Redis per Cache e Sessioni** ($10/mese)
  - Render Dashboard → New → Redis
  - Collegare a web service

### CODICE (IMPORTANTE) ⚠️

- [ ] **Implementare Connection Pooling**
  - Modificare `app.py` con psycopg2 pool

- [ ] **Implementare Caching**
  - Installare Flask-Caching
  - Cachare home, classifica, sfide

- [ ] **Aggiungere Rate Limiting**
  - Flask-Limiter su API validation
  - Protezione anti-spam

- [ ] **Ottimizzare Query Database**
  - Aggiungere indici
  - Limitare risultati (LIMIT)

- [ ] **Error Handling Robusto**
  - Try-catch su tutte le route
  - Fallback graceful se DB down

### DATABASE (URGENTE) 🚨

- [ ] **Backup Database Completo**
  - `pg_dump` manuale
  - Salvare in locale + cloud

- [ ] **Creare Indici Performance**
  - Indici su campi WHERE/ORDER BY

- [ ] **Test Carico Database**
  - Simulare 1000 query/sec
  - Verificare connection limits

### MONITORING (RACCOMANDATO) 📊

- [ ] **Setup Sentry Error Tracking**
  - Account free su sentry.io
  - Integrare in Flask

- [ ] **Setup UptimeRobot**
  - Monitor ogni 5 minuti
  - Alert se down > 2 minuti

- [ ] **Configurare Render Health Checks**
  - Dashboard → Settings → Health Check Path: `/api/ping`

### CDN & PERFORMANCE (IMPORTANTE) 🚀

- [ ] **Verificare Cloudflare Attivo**
  - DNS Proxy ON (arancione)
  - Cache Level: Standard

- [ ] **Minificare CSS/JS**
  - Cloudflare Auto Minify: ON

- [ ] **Compressione Gzip**
  - Abilitata di default su Render

### SICUREZZA (CRITICO) 🔒

- [ ] **Rate Limiting API**
  - Max 10 tentativi/minuto per validazione indizi

- [ ] **HTTPS Enforced**
  - Già attivo su Render (verificare)

- [ ] **SECRET_KEY Forte**
  - Già configurato (verificare)

- [ ] **Protezione CSRF**
  - Flask-WTF per forms critici

### TEST PRE-LANCIO (OBBLIGATORIO) ✅

- [ ] **Load Test con 100 Utenti Simultanei**
  - Tool: Locust o Apache Bench
  - Verificare nessun errore 500

- [ ] **Test Spin-Down Recovery** (se piano free)
  - Aspettare 15 min inattività
  - Verificare riavvio sotto 60 sec

- [ ] **Test Database Connection Pool**
  - Simulare 200 connessioni
  - Verificare nessun "too many connections"

- [ ] **Test Cache Hit Rate**
  - Verificare home page caricata da cache
  - Monitoring Redis hits/misses

---

## 💰 COSTI MENSILI STIMATI

### Setup Minimo (Stabile per 1000 utenti)
```
Web Service Standard:     $25/mese
PostgreSQL Basic:         $7/mese
Redis Starter:           $10/mese
CDN Cloudflare:          $0 (free)
Monitoring Sentry:       $0 (free tier)
UptimeRobot:             $0 (free)
--------------------------------
TOTALE:                  $42/mese
```

### Setup Raccomandato (Alta affidabilità)
```
Web Service Pro:         $85/mese
PostgreSQL Standard:     $20/mese
Redis Standard:          $20/mese
Sentry Business:         $26/mese
--------------------------------
TOTALE:                  $151/mese
```

### Setup Budget (Rischio medio)
```
Web Service Starter:     $7/mese
Supabase Free:           $0
Flask-Caching Simple:    $0
Monitoring free tier:    $0
--------------------------------
TOTALE:                  $7/mese
```

**Raccomandazione:** Setup Minimo ($42/mese)

---

## 🚨 TIMELINE AZIONI URGENTI

### ENTRO 3 GIORNI (CRITICO)
1. Decidere piano database (Render upgrade vs Supabase)
2. Fare backup database completo
3. Upgrade database PRIMA della scadenza (15 nov)

### ENTRO 1 SETTIMANA (IMPORTANTE)
1. Upgrade web service a Standard
2. Implementare connection pooling
3. Aggiungere indici database
4. Setup monitoring base

### ENTRO 2 SETTIMANE (RACCOMANDATO)
1. Implementare caching con Redis
2. Rate limiting API
3. Load testing 100+ utenti
4. Ottimizzare query

### PRIMA DEL 25 GENNAIO 2026 (LANCIO)
1. Load test 1000 utenti
2. Monitoring completo attivo
3. Backup automatici configurati
4. Disaster recovery plan testato

---

## 📞 CONTATTI SUPPORTO

**Render Support:**
- Email: support@render.com
- Docs: https://docs.render.com
- Community: https://community.render.com

**Supabase Support:**
- Email: support@supabase.io
- Docs: https://supabase.com/docs

---

## 🎯 KPI DA MONITORARE

1. **Response Time:** < 500ms (media)
2. **Error Rate:** < 0.1% (max 1 errore ogni 1000 richieste)
3. **Uptime:** > 99.5% (max 3.6 ore down/mese)
4. **Database Connections:** < 80% del limite
5. **Memory Usage:** < 80% della RAM disponibile
6. **CPU Usage:** < 70% (picchi max 90%)

---

**Creato:** 31 Ottobre 2025
**Versione:** 1.0
**Review ogni:** 2 settimane fino al lancio
