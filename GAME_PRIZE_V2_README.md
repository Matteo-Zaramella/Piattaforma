# Game Prize V2.0 - Implementazione Completa

## 📋 Panoramica

Sistema completamente rinnovato per il Game Prize 2026-2027 con:
- **Punteggi progressivi** basati su posizione di arrivo
- **Validazione parole** per indizi (case insensitive, exact match)
- **100 codici univoci** pre-generati per partecipanti
- **13 sfide** con date verificate (12 sabati + 1 domenica finale)
- **Anti-cheat** con logging IP e timestamp
- **Separazione punteggi** indizi/sfide

---

## ✅ Implementazioni Completate

### 1. Schema Database

#### Nuove Tabelle:
- **`game_participants`**: Partecipanti con codici univoci (GP2026-0001 a GP2026-0100)
- **`game_clue_solutions`**: Soluzioni (parole corrette) per ogni indizio
- **`game_clue_completions`**: Tracking completamenti indizi con posizione e punti
- **`game_detailed_scores`**: Punteggi separati (indizi + sfide) per partecipante
- **`game_attempt_logs`**: Log tentativi (anti-cheat con IP + timestamp)

#### Tabelle Esistenti Aggiornate:
- **`game_user_completions`**: Aggiunte colonne `position` e `points_earned`
- **`game_challenges`**: Popolata con 13 sfide (date 2026-2027)
- **`game_prize_config`**: Configurazione generale gioco

### 2. Sistema Punteggi Progressivi

#### Indizi (Clues):
| Posizione | Punti |
|-----------|-------|
| 1°        | 50    |
| 2°        | 40    |
| 3°        | 30    |
| 4°        | 20    |
| 5°        | 10    |
| 6°        | 5     |
| 7° e oltre| 1     |

#### Sfide (Challenges):
| Posizione | Punti |
|-----------|-------|
| 1°        | 500   |
| 2°        | 450   |
| 3°        | 400   |
| 4°        | 350   |
| 5°        | 300   |
| 6°        | 250   |
| 7°        | 200   |
| 8°        | 150   |
| 9°        | 100   |
| 10°       | 50    |
| 11° e oltre| 5    |

### 3. API Endpoints

#### `/game-prize/api/validate-clue` (POST)
Valida la parola inserita per un indizio.

**Request:**
```json
{
  "clue_id": 1,
  "word": "parola"
}
```

**Response (successo):**
```json
{
  "success": true,
  "message": "Corretto! Sei arrivato 3°",
  "points": 30,
  "position": 3
}
```

**Response (errore):**
```json
{
  "success": false,
  "message": "Parola errata. Riprova!"
}
```

**Caratteristiche:**
- ✅ Case insensitive ("Parola" = "parola" = "PAROLA")
- ✅ Exact match (deve essere esatta)
- ✅ Calcolo automatico posizione
- ✅ Assegnazione punti basata su posizione
- ✅ Anti-cheat: log di ogni tentativo con IP
- ✅ Previene completamenti multipli dello stesso indizio

---

#### `/game-prize/api/register-participant` (POST)
Registra un partecipante assegnando un codice univoco.

**Request:**
```json
{
  "nome": "Mario",
  "cognome": "Rossi",
  "email": "mario.rossi@example.com"  // opzionale
}
```

**Response:**
```json
{
  "success": true,
  "message": "Registrazione completata! Il tuo codice è GP2026-0023",
  "unique_code": "GP2026-0023"
}
```

**Caratteristiche:**
- ✅ Assegnazione automatica codice univoco disponibile
- ✅ Previene registrazioni multiple stesso utente
- ✅ Crea automaticamente record punteggi (0 punti iniziali)
- ✅ 100 codici totali disponibili

---

#### `/game-prize/api/add-clue-solution` (POST) [ADMIN ONLY]
Aggiunge/aggiorna la soluzione per un indizio.

**Request:**
```json
{
  "clue_id": 1,
  "solution_word": "enigma",
  "points_base": 50
}
```

**Response:**
```json
{
  "success": true,
  "message": "Soluzione aggiunta"
}
```

---

### 4. Sfide Popolate

| # | Titolo | Data | Giorno | Punti |
|---|--------|------|--------|-------|
| 1 | Sfida 1 - Gennaio | 24/01/2026 | Sabato | 500 |
| 2 | Sfida 2 - Febbraio | 21/02/2026 | Sabato | 500 |
| 3 | Sfida 3 - Marzo | 21/03/2026 | Sabato | 500 |
| 4 | Sfida 4 - Aprile | 25/04/2026 | Sabato | 500 |
| 5 | Sfida 5 - Maggio | 23/05/2026 | Sabato | 500 |
| 6 | Sfida 6 - Giugno | 27/06/2026 | Sabato | 500 |
| 7 | Sfida 7 - Luglio | 25/07/2026 | Sabato | 500 |
| 8 | Sfida 8 - Agosto | 22/08/2026 | Sabato | 500 |
| 9 | Sfida 9 - Settembre | 26/09/2026 | Sabato | 500 |
| 10 | Sfida 10 - Ottobre | 24/10/2026 | Sabato | 500 |
| 11 | Sfida 11 - Novembre | 21/11/2026 | Sabato | 500 |
| 12 | Sfida 12 - Dicembre | 26/12/2026 | Sabato | 500 |
| 13 | **FINALE** | **24/01/2027** | **Domenica** | **1000** |

**Nota:** Ogni sfida è disponibile dalle 00:00 alle 23:59 del giorno indicato.

---

### 5. Codici Univoci Partecipanti

✅ **100 codici pre-generati**: da `GP2026-0001` a `GP2026-0100`

**Stato iniziale:**
- `user_id`: NULL (non assegnato)
- `email`: NULL
- `nome`: NULL
- `cognome`: NULL
- `is_active`: TRUE

**Dopo registrazione:**
- Codice assegnato a user_id
- Nome, cognome, email popolati
- `registered_at`: timestamp registrazione

---

## 🚧 Da Implementare

### 1. Interfacce Admin per Gestione Soluzioni Indizi

**Obiettivo:** Creare una pagina admin dove:
- Visualizzare tutti gli indizi di una sfida
- Aggiungere/modificare la parola soluzione per ogni indizio
- Vedere chi ha completato ogni indizio (con posizione e punti)

**Endpoint già pronto:** `/game-prize/api/add-clue-solution`

**Suggerimento implementazione:**
```html
<!-- In admin_dashboard.html o nuova pagina -->
<div class="clue-solution-form">
  <h3>Indizio #1 - Sfida Gennaio</h3>
  <p>Testo indizio: "La risposta è nel titolo..."</p>

  <form id="solution-form-1">
    <input type="text" name="solution_word" placeholder="Parola corretta">
    <button onclick="saveSolution(1, this.form)">Salva Soluzione</button>
  </form>

  <!-- Lista completamenti -->
  <h4>Chi ha completato:</h4>
  <ol>
    <li>GP2026-0003 - Mario Rossi (50 punti) - 10:23</li>
    <li>GP2026-0012 - Laura Bianchi (40 punti) - 11:45</li>
    <!-- ... -->
  </ol>
</div>

<script>
function saveSolution(clueId, form) {
  fetch('/game-prize/api/add-clue-solution', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      clue_id: clueId,
      solution_word: form.solution_word.value
    })
  })
  .then(r => r.json())
  .then(data => alert(data.message));
}
</script>
```

---

### 2. Classifica con Visibilità Controllata

**Requisiti:**
- Prima 6 mesi: classifica visibile solo all'admin
- Dopo 6 mesi (dal 24/07/2026): classifica visibile a tutti

**Implementazione suggerita:**

#### Backend (`modules/game_prize.py`):
```python
@bp.route('/leaderboard')
@login_required
def leaderboard():
    conn = get_db()
    cursor = conn.cursor()
    user_id = session['user_id']

    # Determina se mostrare classifica completa
    from datetime import datetime, timedelta
    start_date = datetime(2026, 1, 24)
    reveal_date = start_date + timedelta(days=182)  # 6 mesi
    now = datetime.now()

    is_admin = session.get('game_admin_authenticated', False)
    show_full_leaderboard = (now >= reveal_date) or is_admin

    # Query classifica
    cursor.execute('''
        SELECT p.unique_code, p.nome, p.cognome,
               ds.points_from_clues, ds.points_from_challenges, ds.total_points,
               RANK() OVER (ORDER BY ds.total_points DESC) as position
        FROM game_participants p
        JOIN game_detailed_scores ds ON p.id = ds.participant_id
        WHERE p.is_active = 1 AND p.user_id IS NOT NULL
        ORDER BY ds.total_points DESC
    ''')

    leaderboard = cursor.fetchall()
    conn.close()

    return render_template('game_prize/leaderboard.html',
                         leaderboard=leaderboard,
                         show_full=show_full_leaderboard,
                         reveal_date=reveal_date)
```

#### Frontend (`templates/game_prize/leaderboard.html`):
```html
{% if show_full %}
  <!-- Mostra classifica completa -->
  <table>
    <tr>
      <th>Pos.</th>
      <th>Codice</th>
      <th>Nome</th>
      <th>Pt. Indizi</th>
      <th>Pt. Sfide</th>
      <th>Totale</th>
    </tr>
    {% for entry in leaderboard %}
    <tr>
      <td>{{ entry.position }}</td>
      <td>{{ entry.unique_code }}</td>
      <td>{{ entry.nome }} {{ entry.cognome }}</td>
      <td>{{ entry.points_from_clues }}</td>
      <td>{{ entry.points_from_challenges }}</td>
      <td><strong>{{ entry.total_points }}</strong></td>
    </tr>
    {% endfor %}
  </table>
{% else %}
  <!-- Classifica nascosta -->
  <div class="alert alert-warning">
    <h3>🔒 Classifica Bloccata</h3>
    <p>La classifica verrà rivelata il <strong>24 Luglio 2026</strong></p>
    <p>Mancano {{ (reveal_date - now).days }} giorni</p>
  </div>
{% endif %}
```

---

### 3. Completamento Sfide con Posizione

**Da modificare:** Endpoint `/game-prize/complete-challenge/<int:challenge_id>`

Attualmente assegna punti fissi (500). Deve:
1. Calcolare la posizione (1°, 2°, 3°...)
2. Assegnare punti basati su posizione usando `calculate_challenge_points()`
3. Salvare position e points_earned in `game_user_completions`

```python
@bp.route('/complete-challenge/<int:challenge_id>', methods=['POST'])
@login_required
def complete_challenge(challenge_id):
    conn = get_db()
    cursor = conn.cursor()
    user_id = session['user_id']

    # Ottieni participant_id
    cursor.execute('SELECT id FROM game_participants WHERE user_id = ?', (user_id,))
    participant = cursor.fetchone()

    if not participant:
        return jsonify({'error': 'Devi registrarti al gioco'}), 403

    participant_id = participant[0]

    # Calcola posizione
    cursor.execute('''
        SELECT COUNT(*) + 1 FROM game_user_completions
        WHERE challenge_id = ?
    ''', (challenge_id,))

    position = cursor.fetchone()[0]
    points = calculate_challenge_points(position)

    # Salva completamento
    cursor.execute('''
        INSERT INTO game_user_completions
        (user_id, challenge_id, position, points_earned)
        VALUES (?, ?, ?, ?)
    ''', (user_id, challenge_id, position, points))

    # Aggiorna punteggi dettagliati...
    # (simile a validate_clue)

    conn.commit()
    conn.close()

    return jsonify({
        'success': True,
        'position': position,
        'points': points,
        'message': f'Completato! Sei arrivato {position}° ({points} punti)'
    })
```

---

## 🧪 Testing

### Test Locali (SQLite)

1. **Applicare migration:**
   ```bash
   cd C:\Users\offic\Desktop\Piattaforma
   python migrations/apply_game_prize_v2.py
   python migrations/populate_challenges.py
   ```

2. **Testare registrazione partecipante:**
   ```bash
   python -c "
   import sqlite3
   conn = sqlite3.connect('piattaforma.db')
   cursor = conn.cursor()

   # Simula registrazione
   cursor.execute(\"\"\"
     UPDATE game_participants
     SET user_id = 1, nome = 'Test', cognome = 'User',
         email = 'test@test.com', registered_at = CURRENT_TIMESTAMP
     WHERE unique_code = 'GP2026-0001'
   \"\"\")
   conn.commit()

   cursor.execute('SELECT * FROM game_participants WHERE user_id = 1')
   print('Partecipante registrato:', cursor.fetchone())
   conn.close()
   "
   ```

3. **Testare validazione indizio:**
   - Creare un indizio tramite admin dashboard
   - Aggiungere soluzione: POST `/game-prize/api/add-clue-solution`
   - Testare validazione: POST `/game-prize/api/validate-clue`
   - Verificare punteggi: `SELECT * FROM game_detailed_scores`

---

## 🚀 Deploy su Render

### Preparazione:

1. **Applicare migration su PostgreSQL:**
   - Il file `migrations/game_prize_v2_schema.sql` contiene lo schema completo
   - Connettersi al database PostgreSQL di produzione
   - Eseguire lo script SQL

2. **Verificare compatibilità query:**
   - Tutte le query usano `?` (SQLite)
   - ⚠️ **IMPORTANTE:** PostgreSQL usa `%s` come placeholder
   - Modificare le query in `modules/game_prize.py` per supportare entrambi

### Script Helper per Dual Database Support:

```python
# In modules/game_prize.py, aggiungere all'inizio:

def execute_query(conn, query, params=(), fetch_one=False, fetch_all=False):
    """
    Esegue query compatibili con SQLite (?) e PostgreSQL (%s)
    """
    cursor = conn.cursor()

    if USE_POSTGRES:
        # Converti ? in %s per PostgreSQL
        query = query.replace('?', '%s')

    cursor.execute(query, params)

    if fetch_one:
        return cursor.fetchone()
    elif fetch_all:
        return cursor.fetchall()

    return cursor

# Usare sempre execute_query() invece di cursor.execute()
```

---

## 📊 Monitoraggio Anti-Cheat

### Query utili per admin:

**Visualizza tentativi falliti di un partecipante:**
```sql
SELECT attempted_word, attempted_at, ip_address
FROM game_attempt_logs
WHERE participant_id = ? AND is_correct = 0
ORDER BY attempted_at DESC;
```

**Trova partecipanti con troppi tentativi (sospetti):**
```sql
SELECT p.unique_code, p.nome, p.cognome,
       COUNT(*) as total_attempts,
       SUM(CASE WHEN is_correct = 0 THEN 1 ELSE 0 END) as failed_attempts
FROM game_attempt_logs l
JOIN game_participants p ON l.participant_id = p.id
GROUP BY p.id, p.unique_code, p.nome, p.cognome
HAVING COUNT(*) > 50  -- soglia sospetta
ORDER BY total_attempts DESC;
```

**Verifica IP multipli per stesso partecipante:**
```sql
SELECT p.unique_code, COUNT(DISTINCT l.ip_address) as unique_ips
FROM game_attempt_logs l
JOIN game_participants p ON l.participant_id = p.id
GROUP BY p.id, p.unique_code
HAVING COUNT(DISTINCT l.ip_address) > 3  -- sospetto se > 3 IP
ORDER BY unique_ips DESC;
```

---

## 📝 Note Importanti

### Sicurezza:
- ✅ Anti-cheat logging implementato
- ✅ Validazione univocità completamenti (no double-submit)
- ✅ Protezione admin con password
- ⚠️ Considerare rate limiting per `/api/validate-clue` (es. max 10 tentativi/minuto)

### Performance:
- ✅ Indici creati su colonne chiave (clue_id, participant_id, position)
- ✅ Nessuna operazione JOIN pesante in validazione
- ✅ Query classifica ottimizzata (può essere cachata)

### Accuratezza:
- ✅ Calcolo posizione atomico (nessun race condition)
- ✅ Punteggi sempre consistenti (trigger/manual update)
- ✅ Validazione case-insensitive ma exact match garantito

---

## 🎯 Prossimi Passi Consigliati

1. **Creare interfaccia admin gestione soluzioni** (1-2 ore)
2. **Implementare classifica con visibilità controllata** (30 min)
3. **Aggiornare complete_challenge con posizioni** (30 min)
4. **Testing completo locale** (1 ora)
5. **Deploy su Render + migration PostgreSQL** (1 ora)
6. **Testing produzione** (30 min)

**Tempo totale stimato:** ~5 ore

---

## 📞 Supporto

Se ci sono errori o comportamenti anomali:

1. Controllare `game_attempt_logs` per debug tentativi
2. Verificare `game_detailed_scores` per consistenza punteggi
3. Controllare log applicazione per errori SQL
4. Verificare compatibilità SQLite vs PostgreSQL

---

**Implementato da:** Claude Code
**Data:** 30 Ottobre 2025
**Versione:** 2.0.0
