# 🚀 Istruzioni per Applicare Migration Game Prize V2.0

## ⚠️ IMPORTANTE
Le tabelle Game Prize NON esistono ancora su PostgreSQL Render.
Questa migration le creerà da zero con:
- ✅ Date sfide CORRETTE (12 sabati + 1 domenica)
- ✅ 100 codici univoci partecipanti
- ✅ Schema completo V2.0

---

## 📋 Metodo 1: Script Python Automatico (Raccomandato)

### Passo 1: Ottieni DATABASE_URL da Render

1. Vai su https://dashboard.render.com/d/dpg-d3ogka1r0fns73c7230g-a
2. Clicca su **"Connect"** (in alto a destra)
3. Seleziona **"External Connection"**
4. Copia la **"External Database URL"** (inizia con `postgresql://...`)

### Passo 2: Applica la Migration

Apri terminale nella cartella del progetto ed esegui:

```bash
# Windows (PowerShell)
$env:DATABASE_URL="postgresql://piattaforma_user:password@host/piattaforma"
python migrations/apply_to_render.py

# Windows (CMD)
set DATABASE_URL=postgresql://piattaforma_user:password@host/piattaforma
python migrations/apply_to_render.py

# Linux/Mac
export DATABASE_URL="postgresql://piattaforma_user:password@host/piattaforma"
python migrations/apply_to_render.py
```

**Sostituisci** `postgresql://...` con l'URL copiata al passo 1.

### Passo 3: Verifica

Lo script ti mostrerà:
- ✅ Numero tabelle create
- ✅ Codici univoci generati (dovrebbe essere 100)
- ✅ Sfide create (dovrebbe essere 13)
- ✅ Date di tutte le sfide con giorno della settimana

---

## 📋 Metodo 2: psql Diretto (Alternativo)

Se hai `psql` installato:

```bash
# Ottieni DATABASE_URL come sopra, poi:
psql "postgresql://piattaforma_user:password@host/piattaforma" -f migrations/apply_production_fixes.sql
```

---

## 📋 Metodo 3: Render Shell (Solo se altri metodi falliscono)

1. Vai su https://dashboard.render.com/web/srv-d3of691r0fns73c5t110
2. Clicca su **"Shell"** nel menu laterale
3. Esegui:

```bash
# Copia il file SQL nel container
cat > /tmp/migration.sql << 'EOF'
[Copia TUTTO il contenuto di migrations/apply_production_fixes.sql qui]
EOF

# Applica la migration
psql $DATABASE_URL -f /tmp/migration.sql
```

---

## ✅ Verifica Applicazione

Dopo aver applicato la migration, verifica su https://piattaforma.onrender.com:

1. **Vai su Game Prize** (inserisci password "The Game")
2. **Controlla se vedi le 13 sfide**
3. **Verifica le date:**
   - Sfida 1-12 devono essere SABATI
   - Sfida 13 deve essere DOMENICA 24/01/2027

Se vedi le sfide con le date corrette, **la migration è andata a buon fine!** 🎉

---

## 🔍 Troubleshooting

### Errore: "psycopg2 not installed"
```bash
pip install psycopg2-binary
```

### Errore: "DATABASE_URL not set"
Assicurati di aver copiato correttamente l'URL dal dashboard Render (Passo 1).

### Errore: "connection refused"
Verifica che:
1. L'IP Allow List del database includa `0.0.0.0/0` (dovrebbe già esserlo)
2. La DATABASE_URL sia corretta e completa
3. Il database Render sia attivo (status "available")

### Le tabelle esistono già ma con date sbagliate
La migration farà automaticamente `DROP TABLE IF EXISTS ... CASCADE` quindi resetterà tutto.

---

## 📊 Cosa fa lo Script

1. **DROP CASCADE** di tutte le tabelle Game Prize esistenti
2. **Crea 10 tabelle** del sistema V2.0
3. **Genera 100 codici univoci** (GP2026-0001 a GP2026-0100)
4. **Inserisce 13 sfide** con date corrette:
   ```
   Sfida 1:  24/01/2026 (Sabato)
   Sfida 2:  21/02/2026 (Sabato)
   Sfida 3:  21/03/2026 (Sabato)
   Sfida 4:  25/04/2026 (Sabato)
   Sfida 5:  23/05/2026 (Sabato)
   Sfida 6:  27/06/2026 (Sabato)
   Sfida 7:  25/07/2026 (Sabato)
   Sfida 8:  22/08/2026 (Sabato)
   Sfida 9:  26/09/2026 (Sabato)
   Sfida 10: 24/10/2026 (Sabato)
   Sfida 11: 21/11/2026 (Sabato)
   Sfida 12: 26/12/2026 (Sabato)
   Sfida 13: 24/01/2027 (Domenica) ⭐ FINALE
   ```

---

## 🎯 Dopo la Migration

Il sistema sarà completamente pronto:
- ✅ Endpoint API funzionanti (`/api/validate-clue`, `/api/register-participant`)
- ✅ 100 codici univoci disponibili per partecipanti
- ✅ Punteggi progressivi configurati
- ✅ Anti-cheat logging attivo
- ✅ Date sfide CORRETTE

Puoi iniziare a:
1. Aggiungere soluzioni agli indizi tramite admin
2. Configurare indizi per ogni sfida
3. Far registrare i partecipanti

---

**Creato:** 30 Ottobre 2025
**Versione:** Game Prize V2.0
**Database:** PostgreSQL 17 (Render)
