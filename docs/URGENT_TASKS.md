# 🚨 URGENT TASKS - Priorità Immediata

**Data:** 30 Ottobre 2025
**Status:** CRITICO - Dati persi da recuperare

---

## ⚠️ TASK CRITICHE DA COMPLETARE DOMANI

### 1. RECUPERO DATI DA SUPABASE (PRIORITÀ MASSIMA) ⏰ 15 min

**Problema:**
Cambio DATABASE_URL da Supabase a Render ha perso tutti i dati utente:
- Utente admin
- Pasti registrati
- Allenamenti completati
- Workout sessions
- Wishlist

**Soluzione - Migrazione Completa:**

```bash
# STEP 1: Dump database Supabase (5 min)
# Recupera DATABASE_URL Supabase vecchia
export SUPABASE_URL="postgresql://postgres:[PASSWORD]@aws-1-eu-north-1.pooler.supabase.com:5432/postgres"

# Dump solo i dati (non schema, quello nuovo è corretto)
pg_dump $SUPABASE_URL \
  --data-only \
  --table=users \
  --table=pasti \
  --table=allenamenti \
  --table=workout_sessions \
  --table=workout_exercises \
  --table=wishlist \
  --table=settings \
  > supabase_data_backup.sql

# STEP 2: Restore su Render PostgreSQL (5 min)
export RENDER_URL="postgresql://piattaforma_user:Ax9yzqvELNm6Whazz5MJbuhyYY3610Pb@dpg-d3ogka1r0fns73c7230g-a.oregon-postgres.render.com/piattaforma"

psql $RENDER_URL -f supabase_data_backup.sql

# STEP 3: Verifica dati migrati (2 min)
psql $RENDER_URL -c "SELECT * FROM users;"
psql $RENDER_URL -c "SELECT COUNT(*) FROM pasti;"
psql $RENDER_URL -c "SELECT COUNT(*) FROM workout_sessions;"

# STEP 4: Test login sul sito (3 min)
# Prova login con credenziali admin
# Verifica dati visibili in dashboard
```

**Backup da conservare:**
- `supabase_data_backup.sql` - NON cancellare mai

---

### 2. AGGIORNARE ERROR_RESOLUTIONS.md (5 min)

Aggiungere nuovo errore critico:

```markdown
### CRITICAL ERROR 10: Database Switch Senza Migrazione Dati

**Sintomo:** Tutti i dati utente spariti dopo cambio DATABASE_URL

**Causa:** Switch da un database a un altro senza dump/restore

**Prevenzione CRITICA:**
1. ⚠️ **MAI cambiare DATABASE_URL senza backup**
2. Prima di switch: `pg_dump $OLD_DB > backup.sql`
3. Dopo switch: `psql $NEW_DB -f backup.sql`
4. Verificare dati prima di confermare cambio

**Recovery:**
- Recupera vecchio DATABASE_URL
- Dump dati
- Restore su nuovo database
- Testa login e dati visibili
```

---

### 3. CREARE PROCEDURA BACKUP AUTOMATICO (10 min)

**File:** `scripts/backup_database.py`

```python
#!/usr/bin/env python3
"""
Backup automatico database Render PostgreSQL
Da eseguire settimanalmente via cron/scheduler
"""
import os
import subprocess
from datetime import datetime

DATABASE_URL = os.getenv('DATABASE_URL')
BACKUP_DIR = 'backups/'

def backup():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{BACKUP_DIR}piattaforma_backup_{timestamp}.sql"

    # Dump completo (schema + data)
    subprocess.run([
        'pg_dump',
        DATABASE_URL,
        '-f', filename
    ])

    print(f"✅ Backup creato: {filename}")

    # Verifica dimensione
    size = os.path.getsize(filename)
    print(f"📊 Dimensione: {size / 1024:.2f} KB")

if __name__ == '__main__':
    backup()
```

**Aggiungere a git ma IGNORARE backup files:**
```bash
# .gitignore
backups/*.sql
!backups/.gitkeep
```

---

### 4. VERIFICARE GAME PRIZE ADMIN PAGE (5 min)

- [ ] Login con credenziali admin
- [ ] Accedi a Game Prize admin dashboard
- [ ] Verifica accordion si apre correttamente
- [ ] Verifica colori sfide (6 gradient)
- [ ] Verifica indizi visibili quando espandi sfida
- [ ] Test pulsante "Descrizione" e "Classifica"

**Se problemi visivi:**
- Controlla browser console per errori JavaScript
- Verifica Bootstrap 5.3.0 caricato
- Verifica template accordion corretto

---

### 5. DOCUMENTARE DECISIONE DATABASE (3 min)

**Aggiungere a ONBOARDING.md:**

```markdown
## 🗄️ Database Choice: Render PostgreSQL

**Decisione:** Usare Render PostgreSQL invece di Supabase

**Motivi:**
1. ✅ Stesso datacenter del web service (latenza ~1ms vs ~100ms)
2. ✅ Gestione unificata in Render dashboard
3. ✅ Costi inferiori (free tier più generoso)
4. ✅ Backup integrato con Render

**⚠️ LESSON LEARNED:**
- Cambio database richiede SEMPRE migrazione dati
- Backup obbligatorio prima di modifiche infrastructure
- Testare restore backup regolarmente
```

---

## 📋 CHECKLIST COMPLETA DOMANI

```
[ ] 1. Dump dati da Supabase
[ ] 2. Restore dati su Render PostgreSQL
[ ] 3. Verificare login admin funzionante
[ ] 4. Verificare dati visibili (pasti, workout, wishlist)
[ ] 5. Aggiornare ERROR_RESOLUTIONS.md con errore 10
[ ] 6. Creare script backup automatico
[ ] 7. Test completo Game Prize admin page
[ ] 8. Aggiornare ONBOARDING.md con scelta database
[ ] 9. Commit tutto con messaggio "fix: Recupero dati Supabase"
[ ] 10. Deploy e test finale
```

---

## 🔑 INFORMAZIONI NECESSARIE

**Supabase Database URL:**
- Recupera da vecchio config o dashboard Supabase
- Formato: `postgresql://postgres:PASSWORD@aws-1-eu-north-1.pooler.supabase.com:5432/postgres`
- Necessaria per pg_dump

**Render Database URL (già configurata):**
```
postgresql://piattaforma_user:Ax9yzqvELNm6Whazz5MJbuhyYY3610Pb@dpg-d3ogka1r0fns73c7230g-a.oregon-postgres.render.com/piattaforma
```

---

## ⏱️ TEMPO STIMATO TOTALE: ~40 minuti

**Breakdown:**
- Migrazione dati: 15 min
- Documentazione errori: 5 min
- Script backup: 10 min
- Verifica Game Prize: 5 min
- Doc database choice: 3 min
- Test finale: 2 min

---

## 🚫 ERRORE DA NON RIPETERE

**MAI PIÙ:**
❌ Cambiare DATABASE_URL senza verificare dati esistenti
❌ Switch database senza dump/restore
❌ Modificare infrastructure senza backup

**SEMPRE:**
✅ Backup prima di modifiche infrastructure
✅ Verifica dati esistenti prima di switch
✅ Test restore backup dopo creazione
✅ Documentare decisioni database

---

**NOTA:** Dati Supabase ancora esistenti e recuperabili!
Non è stata fatta cancellazione, solo cambio puntatore.
