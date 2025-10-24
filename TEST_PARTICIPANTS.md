# 🧪 Game Prize - Participants Feature TEST PLAN

**Data:** 23 Ottobre 2025
**Status:** ✅ Ready for Testing

---

## Test Scenarios

### Test 1: Database Field Creation ✓
**Prerequisito:** Database deve essere inizializzato

```sql
-- Verificare che il field esista
SELECT * FROM game_prize_config LIMIT 1;

-- Dovrebbe mostrare:
-- ... , max_participants INTEGER DEFAULT 100, ...
```

**Expected Result:** Campo `max_participants` esiste con default 100

---

### Test 2: Admin Setup Form Loading
**URL:** `/game-prize/admin/setup`
**Utente:** Admin autenticato

**Steps:**
1. Accedi come admin
2. Inserisci password "The Game"
3. Vai a `/game-prize/admin/setup`

**Expected Results:**
- ✓ Form carica correttamente
- ✓ Campo "Numero di Partecipanti Invitati" è visibile
- ✓ Input type è "number"
- ✓ Min value è 1
- ✓ Default value è 100 (se config esiste)

**Test HTML:**
```html
<label for="max_participants" class="form-label">
    Numero di Partecipanti Invitati
</label>
<input type="number" class="form-control" id="max_participants"
       name="max_participants" value="100" min="1" required>
```

---

### Test 3: Saving Participant Count
**URL:** `/game-prize/admin/setup`
**Method:** POST

**Steps:**
1. Modifica il campo a un valore diverso (es: 150)
2. Clicca "Salva Configurazione"
3. Verifica che il valore sia salvato

**Expected Results:**
- ✓ Form viene salvato
- ✓ Redirect a `/game-prize/admin/dashboard`
- ✓ Messaggio "Configurazione gioco salvata con successo"
- ✓ Il valore 150 è persistente nel database

**Database Check:**
```sql
SELECT max_participants FROM game_prize_config WHERE id = 1;
-- Risultato atteso: 150
```

---

### Test 4: Admin Dashboard Display
**URL:** `/game-prize/admin/dashboard`
**User:** Admin

**Expected Results:**
- ✓ Card "Partecipanti Invitati" è visibile nel primo slot
- ✓ Mostra il valore salvato (es: 150)
- ✓ Sezione configurazione mostra "Partecipanti Invitati: ~150"

**Visual Check:**
```
┌──────────────────────┐
│ Partecipanti Invitati│
│        150           │  ← Card visualizza il valore
└──────────────────────┘

ℹ️ Configurazione Gioco:
   Partecipanti Invitati: ~150
```

---

### Test 5: Player Dashboard Display
**URL:** `/game-prize/dashboard`
**User:** Giocatore loggato

**Expected Results:**
- ✓ Header mostra "👥 ~150 partecipanti invitati"
- ✓ Testo è chiaro e facilmente leggibile
- ✓ Il numero corrisponde a quello configurato

**Visual Check:**
```
🎮 Game Prize
Premio di Compleanno

👥 ~150 partecipanti invitati
```

---

### Test 6: Default Value Fallback
**Scenario:** Config non ancora salvata

**Expected Results:**
- ✓ Se nessuna config esiste, mostra default 100
- ✓ Form usa 100 come placeholder
- ✓ Dashboard mostra 100

**Test Case:**
```
config = None
Display: {{ config[5] if config else 100 }}
Result: 100  ✓
```

---

### Test 7: Input Validation
**URL:** `/game-prize/admin/setup`

**Test Cases:**

1. **Min Value (1):**
   - Input: 1
   - Expected: Accettato ✓

2. **Valid Number (100):**
   - Input: 100
   - Expected: Accettato ✓

3. **Large Number (1000):**
   - Input: 1000
   - Expected: Accettato ✓

4. **Zero (0):**
   - Input: 0
   - Expected: Rejected (min=1) ✗

5. **Negative (-50):**
   - Input: -50
   - Expected: Rejected (min=1) ✗

6. **Non-numeric:**
   - Input: "abc"
   - Expected: HTML5 validation error ✗

7. **Float (100.5):**
   - Input: 100.5
   - Expected: Converted to 100 (integer) ✓

---

### Test 8: Data Persistence Across Pages
**Scenario:** Cambia il valore e verifica su tutte le pagine

**Steps:**
1. Setup: Imposta max_participants = 75
2. Salva
3. Verifica su Admin Dashboard
4. Verifica su Player Dashboard
5. Verifica su Admin Setup (reload)

**Expected Results:**
- ✓ Admin Dashboard mostra 75
- ✓ Player Dashboard mostra 75
- ✓ Admin Setup form mostra 75

---

### Test 9: Multiple Admin Users
**Scenario:** Admin A cambia il valore, Admin B accede

**Steps:**
1. Admin A imposta max_participants = 120
2. Salva
3. Admin B accede a /game-prize/admin/dashboard
4. Verifica il valore

**Expected Results:**
- ✓ Admin B vede il valore 120 aggiornato
- ✓ No race conditions o cache issues

---

### Test 10: Database Recovery
**Scenario:** App restart e recupero dal database

**Steps:**
1. Imposta max_participants = 200
2. Salva
3. Riavvia l'app
4. Accedi nuovamente
5. Verifica il valore

**Expected Results:**
- ✓ Valore 200 è persistente dopo restart
- ✓ Nessuna perdita di dati

---

## Performance Tests

### Test 11: Query Performance
**Verificare che la query di SELECT sia veloce**

```sql
-- Timing test
SELECT COUNT(*) FROM game_prize_config;
-- Expected: < 1ms

SELECT * FROM game_prize_config WHERE id = 1;
-- Expected: < 5ms
```

---

### Test 12: Form Submission Time
**Misurare il tempo di submit del form**

**Expected:**
- ✓ Form submit completa in < 500ms
- ✓ Database update completa in < 100ms
- ✓ Redirect avviene istantaneamente

---

## Edge Cases

### Test 13: Concurrent Updates
**Scenario:** Due admin modificano il valore contemporaneamente

**Expected Results:**
- ✓ Database gestisce il conflict
- ✓ L'ultimo update vince
- ✓ Nessun errore di integrità

---

### Test 14: Extreme Values
**Test Case:** Inserire valori molto grandi

```
Input: 999999
Expected: Accettato ✓
Display: 999999 ✓
```

---

## Regression Tests

### Test 15: Existing Features Not Broken
Verificare che le modifiche non rompono le feature esistenti:

- ✓ Admin setup salva altri campi (game_name, dates, challenges)
- ✓ Dashboard mostra statistiche corrette
- ✓ Leaderboard funziona
- ✓ Challenge views funzionano
- ✓ Player dashboard funziona

---

## Integration Tests

### Test 16: With Database Migration
**Scenario:** Applicare a database esistente

**Expected:**
- ✓ Migrazione aggiunge campo max_participants
- ✓ Existing records ricevono default 100
- ✓ No data loss

---

## User Acceptance Tests

### Test 17: Admin User Flow
**Steps:**
1. Admin accede
2. Legge la guida su numero partecipanti
3. Modifica il valore a 150
4. Salva
5. Verifica in dashboard
6. Verifica che i giocatori vedono il numero

**Expected:**
- ✓ Workflow è intuitivo
- ✓ Il numero è chiaro e visibile
- ✓ Nessuna confusione su cosa significhi "~100 partecipanti"

---

### Test 18: Player User Flow
**Steps:**
1. Giocatore accede al game
2. Vede il numero di partecipanti invitati
3. Capisce che è approssimativo ("~")
4. Non è confuso dal numero

**Expected:**
- ✓ Il testo "~100 partecipanti invitati" è chiaro
- ✓ Non crea aspettative sbagliate
- ✓ I giocatori capiscono che non tutti accetteranno

---

## Checklist Finale

- [ ] Database field creato
- [ ] Backend handler aggiornato
- [ ] Admin setup form aggiornato
- [ ] Admin dashboard aggiornato
- [ ] Player dashboard aggiornato
- [ ] Valore salvato e recuperato correttamente
- [ ] Default funziona (100)
- [ ] Input validation funziona
- [ ] Data persiste dopo restart
- [ ] No feature regressions
- [ ] UI/UX è intuitiva
- [ ] Documentazione completa

---

## Test Report Template

```
TEST ID: TEST-PARTICIPANTS-001
NAME: Admin Setup Form Loading
DATE: 23-OCT-2025
TESTER: [Name]
STATUS: [PASS/FAIL]
COMMENTS: [Any issues found]
```

---

## Bug Report Template (if needed)

```
BUG ID: BUG-PARTICIPANTS-001
TITLE: [Bug title]
SEVERITY: [Critical/High/Medium/Low]
DATE FOUND: 23-OCT-2025
REPRODUCER:
  1. [Step 1]
  2. [Step 2]
  3. [Step 3]
EXPECTED: [What should happen]
ACTUAL: [What actually happened]
LOGS: [Any error messages]
```

---

## Approval Sign-Off

- [ ] Development Complete
- [ ] Testing Complete
- [ ] QA Approved
- [ ] Production Ready

---

**Status:** 🟢 Ready for Testing
**Priority:** Medium
**Complexity:** Low
