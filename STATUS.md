# 📊 STATUS PROGETTO PIATTAFORMA

**Ultimo aggiornamento**: 2025-10-17 14:40 (Sessione 1)

---

## 🎯 OBIETTIVO

Web app privata personale accessibile su **matteozaramella.com** con:
- Database permanente (dati persistono sempre)
- Accesso protetto da password
- Moduli: Matched Betting, Task Lavoro, Task Privati, Fitness
- Gestibile autonomamente da Claude tramite MCP

---

## ✅ COMPLETATO

### 1. Migrazione Database
- ✅ Database migrato da Render PostgreSQL (90 giorni) a **Supabase PostgreSQL (PERMANENTE)**
- ✅ Codice aggiornato per supportare PostgreSQL con fallback SQLite
- ✅ File `db_utils.py` creato per gestione database unificata
- ✅ Connection string Supabase configurata su Render

### 2. Dominio Personalizzato
- ✅ Dominio **matteozaramella.com** configurato su Cloudflare
- ✅ DNS CNAME puntano a `piattaforma.onrender.com`
- ✅ Cloudflare Proxy attivo (CDN + DDoS protection)
- ✅ Custom domain aggiunto su Render
- ✅ Sito raggiungibile su https://matteozaramella.com

### 3. Connettori MCP Configurati
- ✅ **Render MCP**: Configurato e funzionante
  - File: `C:\Users\offic\.claude.json`
  - Comando: `claude mcp list` per verificare
- ✅ **Cloudflare MCP**: Configurato (connessione fallita, ma API funziona)
  - API Token disponibile e testato
  - Posso gestire DNS via API dirette

### 4. Documentazione
- ✅ `CREDENTIALS.md` - Tutte le credenziali e API keys
- ✅ `RENDER_DEPLOY.md` - Guida deploy su Render
- ✅ `MCP_SETUP.md` - Setup MCP connettori
- ✅ `CLOUDFLARE_SETUP.md` - Setup dominio custom
- ✅ `WORKFLOW_MULTI_TERMINAL.md` - Lavorare da più PC
- ✅ `STATUS.md` - Questo file (stato progetto)

---

## ⚠️ PROBLEMI ATTUALI (DA RISOLVERE)

### 🔴 CRITICO: Internal Server Error 500

**Problema**: Registrazione utenti fallisce con errore 500

**Causa identificata**: `psycopg2` non viene installato correttamente su Render

**Dettagli tecnici**:
- DATABASE_URL configurato correttamente su Render
- Supabase connection string valida
- `requirements.txt` contiene `psycopg2-binary`
- Ma l'app su Render non riesce a importare psycopg2
- Errore: "psycopg2 non installato ma DATABASE_URL configurato"

**Ultimo tentativo in corso**:
- Commit `4d42174`: Rimosso numero versione da psycopg2-binary
- Deploy in corso al momento della scrittura
- Deploy ID: da verificare

**Possibili soluzioni da provare**:
1. Aggiungere `libpq-dev` alle dipendenze sistema (apt-buildpack)
2. Usare variabile `PYTHON_VERSION` in Render
3. Verificare logs build Render per errori installazione
4. Creare script `build.sh` custom

---

## 📁 STRUTTURA FILE PROGETTO

```
Piattaforma/
├── app.py                          # ✅ Main app con supporto PostgreSQL
├── db_utils.py                     # ✅ Helper database (PostgreSQL + SQLite)
├── requirements.txt                # ⚠️ Con psycopg2-binary (problemi install)
├── modules/
│   ├── matched_betting.py         # ✅ Aggiornato per PostgreSQL
│   ├── task_lavoro.py             # ❌ Da aggiornare per PostgreSQL
│   ├── task_privati.py            # ❌ Da aggiornare per PostgreSQL
│   ├── fitness.py                 # ❌ Da aggiornare per PostgreSQL
│   └── settings.py                # ❌ Da aggiornare per PostgreSQL
├── templates/                      # ✅ Tutti i template HTML
├── static/                         # ✅ CSS, JS
├── CREDENTIALS.md                  # ✅ API keys (NON su Git)
├── STATUS.md                       # ✅ Questo file
├── NEXT_STEPS.md                   # ⏳ Prossimi passi da seguire
└── [altre guide].md                # ✅ Documentazione completa
```

---

## 🔑 CREDENZIALI E ACCESSI

### Render
- **API Key**: `rnd_VIWjnZZkLnc7bfd0GHPSmzt7V838`
- **Service ID**: `srv-d3of691r0fns73c5t110`
- **Dashboard**: https://dashboard.render.com/web/srv-d3of691r0fns73c5t110

### Supabase PostgreSQL (DATABASE PERMANENTE)
- **Project ID**: `wuvuapmjclahbmngntku`
- **Password**: `n5x8%XnUK5xMWnV5qWg6`
- **Connection String**: `postgresql://postgres.wuvuapmjclahbmngntku:n5x8%25XnUK5xMWnV5qWg6@aws-0-eu-central-1.pooler.supabase.com:6543/postgres`
- **Dashboard**: https://supabase.com/dashboard/project/wuvuapmjclahbmngntku

### Cloudflare
- **API Token**: `BV4VRnluBBc2zslf5NpmwKGw5CFloEY5E_Zls7D0`
- **Zone ID**: `fa6d2990c04ceae6905ef3a01e06bd10`
- **Dominio**: matteozaramella.com

### GitHub
- **Repository**: https://github.com/Matteo-Zaramella/Piattaforma
- **Branch**: main
- **Auto-deploy**: Attivo su Render

---

## 🤖 CONNETTORI MCP (Model Context Protocol)

### Cosa sono i Connettori MCP

MCP permette a Claude di connettersi direttamente ai servizi cloud per gestirli autonomamente.

### Connettori Configurati

#### 1. Render MCP ✅
**File config**: `C:\Users\offic\.claude.json`

**Verifica stato**:
```bash
claude mcp list
```

**Output atteso**:
```
render: https://mcp.render.com/mcp (HTTP) - ✓ Connected
```

**Cosa può fare Claude**:
- ✅ Vedere tutti i servizi Render
- ✅ Triggerare deploy
- ✅ Leggere/modificare variabili d'ambiente
- ✅ Vedere logs (limitato via API)
- ✅ Gestire custom domains

**Riconfigurazione** (se necessario):
```bash
claude mcp add --transport http render https://mcp.render.com/mcp --header "Authorization: Bearer rnd_VIWjnZZkLnc7bfd0GHPSmzt7V838"
```

#### 2. Cloudflare MCP ⚠️
**Stato**: Configurato ma connessione fallita

**File config**: `C:\Users\offic\.claude.json`

**Problema**: Package MCP Cloudflare non esistente o nome errato

**Workaround**: Uso API Cloudflare dirette (funzionano perfettamente)

**API disponibili**:
- ✅ Gestione DNS records
- ✅ Configurazione proxy/CDN
- ✅ SSL/TLS settings
- ✅ Firewall rules

**Riconfigurazione** (già fatto, ma fallisce):
```bash
claude mcp add --transport stdio cloudflare --env CLOUDFLARE_API_TOKEN=BV4VRnluBBc2zslf5NpmwKGw5CFloEY5E_Zls7D0 -- npx -y @cloudflare/mcp-server-cloudflare
```

---

## 🔄 WORKFLOW CLAUDE PER PROSSIME SESSIONI

### Quando inizi una nuova sessione:

1. **Leggi questo file** (`STATUS.md`)
2. **Leggi** `NEXT_STEPS.md` per sapere cosa fare
3. **Verifica connettori MCP**:
   ```bash
   claude mcp list
   ```
4. **Se Render MCP non connesso**, riconfigura:
   ```bash
   claude mcp add --transport http render https://mcp.render.com/mcp --header "Authorization: Bearer rnd_VIWjnZZkLnc7bfd0GHPSmzt7V838"
   ```

### Come verificare stato servizio:

```bash
# Via MCP Render (se connesso)
curl -H "Authorization: Bearer rnd_VIWjnZZkLnc7bfd0GHPSmzt7V838" https://api.render.com/v1/services/srv-d3of691r0fns73c5t110

# Test sito
curl -I https://matteozaramella.com
```

### Come fare deploy manuale:

```bash
curl -X POST -H "Authorization: Bearer rnd_VIWjnZZkLnc7bfd0GHPSmzt7V838" -H "Content-Type: application/json" -d '{"clearCache":"clear"}' "https://api.render.com/v1/services/srv-d3of691r0fns73c5t110/deploys"
```

---

## 📈 PROGRESSI SESSIONE

**Sessione 1** (2025-10-17):
- ✅ Migrato a Supabase database permanente
- ✅ Configurato dominio matteozaramella.com
- ✅ Setup MCP Render
- ✅ Creata documentazione completa
- ⚠️ Problema psycopg2 su Render (in corso)

---

## 🎯 PROSSIMO OBIETTIVO

**PRIORITÀ 1**: Risolvere errore 500 (psycopg2 non installato)

Vedere file **NEXT_STEPS.md** per azioni specifiche.

---

## 📞 COMANDI UTILI RAPIDI

```bash
# Verifica MCP
claude mcp list

# Test sito
curl https://matteozaramella.com

# Deploy manuale
curl -X POST -H "Authorization: Bearer rnd_VIWjnZZkLnc7bfd0GHPSmzt7V838" -H "Content-Type: application/json" -d '{"clearCache":"clear"}' "https://api.render.com/v1/services/srv-d3of691r0fns73c5t110/deploys"

# Stato ultimo deploy
curl -H "Authorization: Bearer rnd_VIWjnZZkLnc7bfd0GHPSmzt7V838" "https://api.render.com/v1/services/srv-d3of691r0fns73c5t110/deploys?limit=1"

# Git push
cd C:\Users\offic\Desktop\Piattaforma && git push
```

---

**Nota per Claude futuro**: Leggi sempre questo file all'inizio di ogni sessione per sapere lo stato del progetto!
