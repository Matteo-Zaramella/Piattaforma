# 🚀 Piattaforma - Onboarding & Maintenance Guide

Guida completa per gestione autonoma e manutenzione della piattaforma.

**Ultimo aggiornamento:** 30 Ottobre 2025

---

## 📋 Indice

1. [Architettura Sistema](#architettura-sistema)
2. [Setup Locale](#setup-locale)
3. [Deployment Procedure](#deployment-procedure)
4. [Troubleshooting Autonomo](#troubleshooting-autonomo)
5. [Maintenance Tasks](#maintenance-tasks)

---

## 🏗️ Architettura Sistema

### Stack Tecnologico
- **Backend:** Flask 3.0.0 (Python)
- **Database:** PostgreSQL 17 (Render)
- **Frontend:** Bootstrap 5.3.0, Jinja2 templates
- **Hosting:** Render.com (Free tier)
- **Version Control:** GitHub

### Struttura Progetto
```
Piattaforma/
├── app.py                    # Entry point principale
├── requirements.txt          # Dipendenze Python
├── modules/                  # Moduli Flask Blueprint
│   ├── fitness.py           # Workout e nutrizione
│   ├── game_prize.py        # The Game logic
│   ├── wishlist.py          # Lista desideri
│   ├── location.py          # Dove sono
│   └── appointments.py      # Appuntamenti
├── templates/               # Template Jinja2
│   ├── base.html           # Template base
│   ├── home.html           # Homepage pubblica
│   ├── login.html          # Login page
│   ├── dashboard.html      # Dashboard privata
│   ├── fitness/            # Template workout
│   ├── game_prize/         # Template The Game
│   └── ...
├── migrations/              # Migration SQL
│   ├── create_all_tables.sql
│   ├── apply_production_fixes.sql
│   └── apply_to_render.py
└── docs/                    # Documentazione
    ├── ERROR_RESOLUTIONS.md # ⚠️ LEGGI SEMPRE PER ERRORI
    └── ONBOARDING.md        # Questo file
```

### Database Schema (17 Tabelle)

**Tabelle App Core:**
1. `users` - Utenti sistema (admin)
2. `pasti` - Tracking pasti
3. `allenamenti` - Workout legacy
4. `workout_sessions` - Sessioni workout
5. `workout_exercises` - Esercizi per sessione
6. `wishlist` - Lista desideri
7. `settings` - Configurazioni utente

**Tabelle Game Prize:**
8. `game_participants` - 100 codici univoci
9. `game_challenges` - 13 sfide (12 sabati + finale)
10. `game_clues` - Indizi puzzle
11. `game_clue_solutions` - Soluzioni parole
12. `game_clue_completions` - Chi ha risolto indizi
13. `game_detailed_scores` - Punteggi dettagliati
14. `game_user_completions` - Sfide completate
15. `game_user_scores` - Punteggi utenti
16. `game_attempt_logs` - Anti-cheat logs
17. `game_prize_config` - Configurazione gioco

---

## 💻 Setup Locale

### Prerequisiti
- Python 3.11+
- PostgreSQL installato (opzionale, può usare SQLite locale)
- Git

### Setup Step-by-Step

```bash
# 1. Clone repository
git clone https://github.com/Matteo-Zaramella/Piattaforma.git
cd Piattaforma

# 2. Crea virtual environment
python -m venv venv
source venv/bin/activate  # Su Windows: venv\Scripts\activate

# 3. Installa dipendenze
pip install -r requirements.txt

# 4. Configura environment variables
# Crea file .env nella root:
DATABASE_URL=postgresql://piattaforma_user:PASSWORD@dpg-d3ogka1r0fns73c7230g-a.oregon-postgres.render.com/piattaforma
SECRET_KEY=your-secret-key-here
FLASK_ENV=development

# 5. Avvia app
python app.py

# App disponibile su http://localhost:5000
```

### Test Locale Pre-Deploy

**SEMPRE testare in locale prima di push:**
```bash
# Test login
curl http://localhost:5000/login

# Test dashboard (richiede login)
# Usa browser per testare manualmente

# Verifica database connection
python -c "from app import get_db; get_db()"
```

---

## 🚀 Deployment Procedure

### Deploy Workflow (Auto-Deploy Attivo)

```bash
# 1. Sviluppo locale
# ... modifica codice ...

# 2. Test locale
python app.py
# Testa tutte le route modificate

# 3. Commit & Push
git add .
git commit -m "feat: Descrizione modifica con emoji 🎨"
git push origin main

# 4. Render Auto-Deploy
# Render rileva push automaticamente
# Build starts (~2 minuti)
# Deploy completa (~1 minuto)

# 5. Verifica deploy
curl https://piattaforma.onrender.com
# Oppure apri browser
```

### Monitoring Deploy

```bash
# Controlla status deploy
render deploys srv-d3of691r0fns73c5t110 --limit 3

# Segui logs in real-time
render logs srv-d3of691r0fns73c5t110 --tail

# Verifica variabili ambiente
render env srv-d3of691r0fns73c5t110
```

---

## 🔧 Troubleshooting Autonomo

### ⚠️ PRIMA COSA DA FARE AD OGNI ERRORE

**Leggi `docs/ERROR_RESOLUTIONS.md` - Contiene tutte le soluzioni!**

### Flowchart Diagnostica Rapida

```
ERRORE 500?
    ↓
Controlla logs Render
    ↓
Identifica exception type
    ↓
┌─────────────────────────────────────┐
│                                     │
│  psycopg2.Error?                   │
│  → Vedi ERROR_RESOLUTIONS.md #1-3  │
│                                     │
│  jinja2.Error?                     │
│  → Vedi ERROR_RESOLUTIONS.md #5    │
│                                     │
│  ImportError/ModuleNotFoundError?  │
│  → Vedi ERROR_RESOLUTIONS.md #8    │
│                                     │
└─────────────────────────────────────┘
    ↓
Applica fix documentato
    ↓
Test locale
    ↓
Push & Deploy
    ↓
Verifica fix
```

### Quick Commands Diagnostica

```bash
# 1. Logs ultimi 50 errori
render logs srv-d3of691r0fns73c5t110 | grep ERROR | tail -50

# 2. Verifica DATABASE_URL
render env srv-d3of691r0fns73c5t110 | grep DATABASE_URL

# 3. Controlla tabelle database
psql $DATABASE_URL -c "\dt"

# 4. Test connessione DB
psql $DATABASE_URL -c "SELECT COUNT(*) FROM users;"

# 5. Verifica deploy status
render deploys srv-d3of691r0fns73c5t110 --limit 1
```

---

## 🛠️ Maintenance Tasks

### Settimanali

**Lunedì mattina:**
```bash
# 1. Verifica health generale
curl https://piattaforma.onrender.com
# Status code 200 = OK

# 2. Controlla logs errori settimana scorsa
render logs srv-d3of691r0fns73c5t110 --since 7d | grep ERROR

# 3. Verifica spazio database
psql $DATABASE_URL -c "SELECT pg_size_pretty(pg_database_size('piattaforma'));"

# 4. Backup database (TODO: automatizzare)
pg_dump $DATABASE_URL > backups/backup_$(date +%Y%m%d).sql
```

### Mensili

**Primo del mese:**
```bash
# 1. Aggiorna dipendenze (se necessario)
pip list --outdated
# Aggiorna solo security patches

# 2. Pulisci vecchi logs (Render fa automatico dopo 7 giorni)

# 3. Review ERROR_RESOLUTIONS.md
# Aggiungi nuovi errori riscontrati

# 4. Verifica backup funzionanti
# Test restore su database locale
```

### Game Prize Specific (Durante l'anno del gioco)

**Ogni Sabato a mezzanotte:**
```sql
-- Verifica sfida del giorno pubblicata
SELECT * FROM game_challenges
WHERE DATE(start_date) = CURRENT_DATE;

-- Verifica indizi del giorno
SELECT * FROM game_clues
WHERE DATE(revealed_date) = CURRENT_DATE;
```

**Post-Sfida (lunedì dopo sfida):**
```sql
-- Controlla completamenti
SELECT COUNT(*) FROM game_user_completions
WHERE challenge_id = [ID_SFIDA_WEEKEND];

-- Verifica classifica
SELECT * FROM game_detailed_scores
ORDER BY total_points DESC
LIMIT 10;

-- Check anti-cheat logs
SELECT * FROM game_attempt_logs
WHERE created_at >= NOW() - INTERVAL '3 days'
ORDER BY created_at DESC;
```

---

## 🔐 Variabili Ambiente (Render)

**Config Attuale:**
```bash
DATABASE_URL=postgresql://piattaforma_user:Ax9yzqvELNm6Whazz5MJbuhyYY3610Pb@dpg-d3ogka1r0fns73c7230g-a.oregon-postgres.render.com/piattaforma
SECRET_KEY=[generato automaticamente da Render]
PYTHON_VERSION=3.13
```

**Aggiornare variabile:**
```python
# Via MCP tool
render.update_environment_variables(
    serviceId="srv-d3of691r0fns73c5t110",
    envVars=[{"key": "VAR_NAME", "value": "VAR_VALUE"}]
)
# Triggera automaticamente redeploy
```

---

## 📊 Monitoring & Analytics

### Metriche da Monitorare

1. **Uptime:** Deve essere >99%
2. **Response Time:** <500ms per route principali
3. **Error Rate:** <1% richieste
4. **Database Connections:** Non deve superare limit PostgreSQL

### Render Dashboard Links

- **Service:** https://dashboard.render.com/web/srv-d3of691r0fns73c5t110
- **Database:** https://dashboard.render.com/d/dpg-d3ogka1r0fns73c7230g-a
- **Deploys:** https://dashboard.render.com/web/srv-d3of691r0fns73c5t110/deploys
- **Logs:** https://dashboard.render.com/web/srv-d3of691r0fns73c5t110/logs

---

## 🚨 Escalation Path

### Livello 1: Self-Service (Tu - AI Assistant)
- Consulta `ERROR_RESOLUTIONS.md`
- Applica fix documentati
- Test e deploy

### Livello 2: User Intervention Required
- Errori non documentati
- Decisioni di design
- Cambio architettura

### Livello 3: External Support
- Render platform issues
- PostgreSQL corruption
- Security breach

---

## 📝 Best Practices

### Commit Messages
```bash
# Use conventional commits con emoji
feat: ✨ Nuova feature
fix: 🐛 Bug fix
docs: 📝 Documentazione
style: 💄 UI/CSS changes
refactor: ♻️ Code refactoring
perf: ⚡ Performance improvement
test: ✅ Test aggiunto
```

### Code Review Checklist
- [ ] Funziona in locale
- [ ] Tutti i route testati
- [ ] Nessun hardcoded secrets
- [ ] Error handling presente
- [ ] Logs appropriati
- [ ] Database query ottimizzate
- [ ] Template safe (default values)

### Security Checklist
- [ ] Nessuna password in codice
- [ ] SESSION_SECRET randomizzato
- [ ] SQL injection prevenuto (usa %s placeholder)
- [ ] XSS prevenuto (Jinja2 auto-escape)
- [ ] Registrazione pubblica disabilitata
- [ ] Admin routes protected

---

## 🎯 Quick Reference

### File Critici da Non Toccare (Senza Backup)
- `app.py` - Entry point
- `migrations/create_all_tables.sql` - Schema master
- `requirements.txt` - Dipendenze

### File Sicuri da Modificare
- Templates in `templates/` - Solo UI
- CSS inline nei templates
- `docs/` - Documentazione

### Comandi Utili Memorizzabili

```bash
# Alias utili da aggiungere
alias piattaforma-logs="render logs srv-d3of691r0fns73c5t110"
alias piattaforma-deploy="git push && echo 'Deploy in corso...'"
alias piattaforma-db="psql $DATABASE_URL"
alias piattaforma-test="python app.py"
```

---

## 📚 Learning Resources

- **Flask Docs:** https://flask.palletsprojects.com/
- **Jinja2 Docs:** https://jinja.palletsprojects.com/
- **PostgreSQL Docs:** https://www.postgresql.org/docs/
- **Render Docs:** https://render.com/docs
- **Bootstrap 5:** https://getbootstrap.com/docs/5.3/

---

**Documento Vivo:** Aggiornare ad ogni cambio significativo all'architettura o procedure.

**Prossimi Step:**
- [ ] Implementare backup automatico settimanale
- [ ] Aggiungere health check endpoint `/health`
- [ ] Setup monitoring alerts (Render notifications)
- [ ] Implementare rate limiting per API Game Prize
