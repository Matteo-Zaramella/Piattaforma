# Workflow Multi-Terminale per Piattaforma

## Come lavorare sul progetto da qualsiasi computer

Questo documento spiega come configurare l'ambiente di sviluppo su più computer per lavorare sul progetto Piattaforma da ovunque.

---

## Metodo Consigliato: GitHub + Git + Claude MCP

### Setup su Nuovo PC/Terminale

#### 1. Installa Prerequisites

**Windows:**
- Python 3.10+: https://python.org
- Git: https://git-scm.com
- Node.js: https://nodejs.org (per Claude MCP)
- Claude Code: https://claude.com/code

**Mac/Linux:**
```bash
# Python (di solito già installato)
python3 --version

# Git
git --version

# Node.js
node --version
```

#### 2. Clone Repository

```bash
git clone https://github.com/Matteo-Zaramella/Piattaforma.git
cd Piattaforma
```

#### 3. Setup Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 4. Configure Claude MCP

```bash
claude mcp add --transport http render https://mcp.render.com/mcp --header "Authorization: Bearer rnd_VIWjnZZkLnc7bfd0GHPSmzt7V838"
```

Verifica connessione:
```bash
claude mcp list
# Dovrebbe mostrare: render: ✓ Connected
```

#### 5. Test Locale

```bash
python app.py
```
Apri browser: http://localhost:5000

---

## Workflow Quotidiano

### Inizio Lavoro (Qualsiasi PC)

```bash
# 1. Vai nella cartella progetto
cd Piattaforma

# 2. Pull ultime modifiche
git pull origin main

# 3. Attiva virtual environment
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# 4. Avvia app locale
python app.py
```

### Durante Sviluppo

```bash
# Fai modifiche ai file con editor preferito

# Test modifiche localmente
# Browser: http://localhost:5000

# Commit frequenti
git add .
git commit -m "Descrizione delle modifiche"
```

### Fine Lavoro / Push Modifiche

```bash
# Push su GitHub
git push origin main

# Render fa auto-deploy automaticamente!
# Verifica su: https://piattaforma.onrender.com
```

### Cambio PC

Sul nuovo PC:
```bash
git pull origin main
# Continua da dove hai lasciato!
```

---

## Accesso alle Credenziali su Altri PC

Il file `CREDENTIALS.md` contiene tutte le API keys e credenziali ma **NON è su Git** per sicurezza.

### Opzioni per Accedere alle Credenziali:

#### 1. Password Manager (CONSIGLIATO)
- Salva CREDENTIALS.md in 1Password / Bitwarden / LastPass
- Accessibile da ovunque con master password
- Più sicuro

#### 2. Cloud Storage Privato
- OneDrive / Google Drive / Dropbox
- Cartella privata (non condivisa)
- Sync automatico

#### 3. Email Criptata
- Invia a te stesso con crittografia
- Gmail con confidential mode

#### 4. Copia Manuale
- Porta su USB criptata
- Trasferisci via canale sicuro

### Rigenerazione Credenziali (se perse)

**Render API Key:**
1. Vai su https://dashboard.render.com/account/api-keys
2. Revoca vecchia key
3. Crea nuova key
4. Riconfigura Claude MCP

**PostgreSQL Password:**
1. Render Dashboard → Database
2. Click "Reset Password"
3. Aggiorna DATABASE_URL in env vars

**SECRET_KEY:**
```bash
python -c "import os; print(os.urandom(24).hex())"
```
Aggiorna su Render environment variables

---

## Claude MCP su Nuovi Terminali

Su ogni nuovo PC dove vuoi usare Claude Code:

### Configurazione Automatica:

```bash
claude mcp add --transport http render https://mcp.render.com/mcp --header "Authorization: Bearer rnd_VIWjnZZkLnc7bfd0GHPSmzt7V838"
```

### File di Configurazione

Claude MCP salva config in:
- **Windows**: `C:\Users\[USERNAME]\.claude.json`
- **Mac/Linux**: `~/.claude.json`

Puoi copiare questo file tra PC per sync rapido!

### Verifica Connessione

```bash
claude mcp list

# Output atteso:
# render: https://mcp.render.com/mcp (HTTP) - ✓ Connected
```

---

## Best Practices

### 1. Commit Frequenti

```bash
# Ogni volta che completi una funzionalità
git add .
git commit -m "Descrizione chiara"

# Push almeno 1 volta al giorno
git push origin main
```

### 2. Test Prima del Push

Prima di fare push:
- ✓ Test locale funziona
- ✓ Nessun errore Python
- ✓ Login/registrazione OK

### 3. Branch per Nuove Funzionalità (Opzionale)

```bash
# Crea branch per nuova feature
git checkout -b feature/nome-funzionalita

# Lavora sul branch
git add .
git commit -m "Work in progress"

# Push branch
git push origin feature/nome-funzionalita

# Quando pronto: crea Pull Request su GitHub
# Merge su main quando testato
```

---

## Troubleshooting Multi-PC

### Conflitti Git

```bash
# Se vedi "conflict" durante pull
git status
git diff

# Risolvi manualmente file in conflitto
# Poi:
git add .
git commit -m "Risolti conflitti"
git push
```

### Virtual Environment Non Funziona

```bash
# Elimina venv corrotto
rm -rf venv  # Mac/Linux
# Windows: elimina cartella manualmente

# Ricrea
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Claude MCP Non Connette

```bash
# Verifica configurazione
claude mcp list

# Se non connesso, riconfigura
claude mcp add --transport http render https://mcp.render.com/mcp --header "Authorization: Bearer rnd_VIWjnZZkLnc7bfd0GHPSmzt7V838"

# Riavvia Claude Code
```

---

## Checklist Setup Nuovo PC

- [ ] Installa Python 3.10+
- [ ] Installa Git
- [ ] Installa Node.js
- [ ] Installa Claude Code
- [ ] Clone repository: `git clone https://github.com/Matteo-Zaramella/Piattaforma.git`
- [ ] Crea virtual environment: `python -m venv venv`
- [ ] Attiva venv: `venv\Scripts\activate`
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Configure Claude MCP
- [ ] Test locale: `python app.py`
- [ ] Test push/pull: modifica un file, commit, push

---

## Alternative Avanzate

### GitHub Codespaces

Ambiente cloud completo nel browser:
1. Vai su https://github.com/Matteo-Zaramella/Piattaforma
2. Click "Code" → "Codespaces" → "Create codespace"
3. Lavora nel browser, 60h/mese gratis

### VS Code Settings Sync

Sync impostazioni VS Code tra PC:
1. VS Code → Ctrl+Shift+P
2. "Settings Sync: Turn On"
3. Login con GitHub
4. Automaticamente sync su altri PC

---

## Riepilogo File Importanti

- `CREDENTIALS.md` - Credenziali (NON su Git!)
- `WORKFLOW_MULTI_TERMINAL.md` - Questo file
- `RENDER_DEPLOY.md` - Guida deploy Render
- `MCP_SETUP.md` - Setup Claude MCP
- `CLOUDFLARE_SETUP.md` - Setup dominio custom
- `.gitignore` - File da NON committare

---

## Domande Frequenti

**Q: Posso lavorare offline?**
A: Sì, puoi sviluppare localmente offline. Quando torni online fai `git pull` poi `git push`.

**Q: Cosa succede se faccio push mentre Render sta deployando?**
A: Render metterà in coda il nuovo deploy. Il più recente andrà live.

**Q: Posso avere più PC che lavorano contemporaneamente?**
A: Sì, ma fai sempre `git pull` prima di iniziare per evitare conflitti.

**Q: Claude MCP funziona anche da PC diversi?**
A: Sì, basta riconfigurare con stessa API key Render su ogni PC.

---

Ultimo aggiornamento: 2025-10-17
