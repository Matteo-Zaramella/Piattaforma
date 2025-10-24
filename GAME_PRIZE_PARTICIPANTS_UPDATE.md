# 🎮 Game Prize - Aggiornamento Numero Partecipanti

**Data:** 23 Ottobre 2025
**Status:** ✅ COMPLETATO

---

## Sommario Modifiche

Il sistema Game Prize è stato aggiornato per supportare il numero di partecipanti invitati (~100), con la possibilità che ognuno sia libero di accettare l'invito.

---

## Modifiche Apportate

### 1. Database Schema (app.py)

**Tabella:** `game_prize_config`

Aggiunto nuovo campo:
```sql
max_participants INTEGER DEFAULT 100
```

Questo campo memorizza il numero di invitati al gioco. Il valore di default è impostato a **100**.

---

### 2. Backend (modules/game_prize.py)

#### Route: `/game-prize/admin/setup` (POST)

Aggiornato il form handler per gestire il nuovo parametro:

```python
max_participants = int(request.form.get('max_participants', 100))
```

Modificati gli UPDATE/INSERT per includere `max_participants`:

**UPDATE:**
```python
cursor.execute('''
    UPDATE game_prize_config
    SET game_name = %s, start_date = %s, end_date = %s,
        total_challenges = %s, max_participants = %s, description = %s, updated_at = CURRENT_TIMESTAMP
    WHERE id = 1
''', (game_name, start_date, end_date, total_challenges, max_participants, description))
```

**INSERT:**
```python
cursor.execute('''
    INSERT INTO game_prize_config (game_name, start_date, end_date, total_challenges, max_participants, description)
    VALUES (%s, %s, %s, %s, %s, %s)
''', (game_name, start_date, end_date, total_challenges, max_participants, description))
```

---

### 3. Admin Setup Template

**File:** `templates/game_prize/admin_setup.html`

Aggiunto nuovo campo input nella sezione configurazione:

```html
<div class="col-md-6">
    <div class="mb-3">
        <label for="max_participants" class="form-label">
            Numero di Partecipanti Invitati
        </label>
        <input type="number" class="form-control" id="max_participants"
               name="max_participants"
               value="{{ config[5] if config else 100 }}" min="1" required>
        <small class="text-muted">Default: ~100 invitati</small>
    </div>
</div>
```

Aggiornato l'info box per includere il nuovo parametro.

---

### 4. Admin Dashboard Template

**File:** `templates/game_prize/admin_dashboard.html`

#### Statistiche Superiori

Aggiunto nuovo card al primo posto:
```html
<div class="col-md-6 col-lg-3">
    <div class="card text-center">
        <div class="card-body">
            <h6 class="card-title text-muted">Partecipanti Invitati</h6>
            <p class="display-5">{{ config[5] if config else 100 }}</p>
        </div>
    </div>
</div>
```

#### Sezione Configurazione

Aggiornata per mostrare il numero di partecipanti:
```html
<p><strong>Partecipanti Invitati:</strong> ~{{ config[5] if config else 100 }}</p>
```

---

### 5. Game Dashboard Template

**File:** `templates/game_prize/dashboard.html`

Aggiunto indicatore di partecipanti invitati sotto il titolo principale:

```html
<p class="text-muted small">
    👥 <strong>~{{ game_config[5] }}</strong> partecipanti invitati
</p>
```

---

## Struttura Dati

### Config Index Reference

La struttura della riga config nella tabella `game_prize_config` è:

| Index | Campo | Descrizione |
|-------|-------|-------------|
| 0 | id | ID della configurazione |
| 1 | game_name | Nome del gioco |
| 2 | start_date | Data inizio |
| 3 | end_date | Data fine |
| 4 | total_challenges | Numero sfide |
| 5 | max_participants | **[NUOVO]** Numero partecipanti invitati |
| 6 | description | Descrizione |
| 7 | created_at | Data creazione |
| 8 | updated_at | Data ultimo aggiornamento |

---

## Features Implementate

### ✅ Admin Setup
- Input campo per numero partecipanti
- Default: 100
- Salvato nel database
- Editabile da admin

### ✅ Admin Dashboard
- Card che mostra i partecipanti invitati
- Confronto con giocatori attivi
- Info box aggiornata

### ✅ Player Dashboard
- Visualizzazione numero partecipanti
- Icona 👥 per chiarezza visiva

---

## Come Utilizzare

### Per l'Admin

1. Accedi a `/game-prize/admin/setup`
2. Modifica il campo "Numero di Partecipanti Invitati"
3. Salva la configurazione
4. Il numero si aggiorna automaticamente in tutto il sistema

### Default

Se non configurato, il sistema usa il default di **100 partecipanti**.

---

## Prossimi Passi (Opzionali)

Se in futuro avrai bisogno di:

1. **Gestione inviti attivi** - Tracciare chi ha accettato l'invito
2. **Dashboard partecipanti** - Mostrare tasso di accettazione
3. **Inviti email** - Integrare sistema di invio inviti
4. **Lista partecipanti** - Gestire lista completa di invitati

Fammi sapere e implemento subito!

---

## Testing Checklist

✅ Campo aggiunti al database
✅ Backend aggiornato per gestire il parametro
✅ Admin setup mostra il campo
✅ Admin dashboard mostra il numero
✅ Player dashboard mostra il numero
✅ Default impostato a 100
✅ Salvaggio e recupero dati funziona

---

## Note Importanti

- Il numero di partecipanti è configurabile (non hardcoded)
- Il valore è memorizzato nel database
- Il "~" (circa) indica che non tutti gli invitati accetteranno
- Perfetto per il scenario: 100 invitati → alcuni accettano → partecipano al gioco

---

**Status:** 🟢 READY FOR USE
**Data Completamento:** 23 Ottobre 2025
