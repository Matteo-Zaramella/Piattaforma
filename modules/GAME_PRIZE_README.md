# Game Prize Module

Modulo Flask Blueprint per gestire un gioco a premi annuale con sfide, indizi e sistema di classifica.

## Accesso Rapido

### Per i Giocatori
- Dashboard: `/game-prize/dashboard`
- Classifica: `/game-prize/leaderboard`
- Singola sfida: `/game-prize/challenge/<id>`

### Per l'Admin
- Setup: `/game-prize/admin/setup`
- Dashboard admin: `/game-prize/admin/dashboard`
- Aggiungi sfida: `/game-prize/admin/challenge/add`
- Modifica sfida: `/game-prize/admin/challenge/<id>/edit`
- Aggiungi indizio: `/game-prize/admin/clue/add/<challenge_id>`

## Funzioni Principali

### Gestione Sfide
- Creare fino a 12 sfide
- Assegnare punti a ogni sfida
- Impostare date di inizio/fine
- Aggiungere istruzioni e location

### Sistema di Indizi
- Aggiungi indizi multipli per sfida
- Pianifica la rivelazione degli indizi
- Gli indizi sono spalmati settimanalmente

### Tracciamento Progressi
- Punti totali per giocatore
- Sfide completate
- Classifica in tempo reale
- Rivelazione vincitore al 50%

## Decoratori

### @login_required
Protegge le route che richiedono accesso autenticato

```python
@bp.route('/dashboard')
@login_required
def dashboard():
    # Solo utenti loggati
```

### @admin_required
Per future protezioni admin (da implementare in fase 2)

```python
@bp.route('/admin/setup')
@admin_required
def admin_setup():
    # Solo admin
```

## Helper Functions

### get_db()
Ottiene la connessione al database dal modulo principale

```python
conn = get_db()
cursor = conn.cursor()
```

## API Endpoints (JSON)

### GET /game-prize/clues/<challenge_id>
Restituisce gli indizi di una sfida in formato JSON

```json
[
  {
    "id": 1,
    "clue_number": 1,
    "text": "Indizio testo",
    "revealed_date": "2024-11-15T14:00:00"
  }
]
```

### POST /game-prize/complete-challenge/<challenge_id>
Marca una sfida come completata

Response (success):
```json
{
  "success": true,
  "points": 100,
  "message": "Hai guadagnato 100 punti!"
}
```

Response (error):
```json
{
  "error": "Sfida già completata"
}
```

## Logica di Business

### Rivelazione del Vincitore
1. **Prima del 50%**: La classifica esiste ma il vincitore non è ancora "ufficiale"
2. **Al raggiungimento del 50% (6/12 sfide)**:
   - Appare un avviso "MILESTONE RAGGIUNTO!"
   - Nessuna modifica alla classifica
3. **Al termine (festa)**: Il vincitore viene ufficialmente rivelato

### Assegnazione Punti
- Ogni sfida ha un valore in punti
- I punti vengono assegnati al completamento
- La somma determina la posizione in classifica
- Possono completare la stessa sfida una sola volta

## Integrazioni Future

- Sistema di notifiche email per indizi
- Protezione password admin
- Foto/media per sfide
- Chat privata giocatori
- Export classifica

## Note di Sviluppo

- SQLite + PostgreSQL supportati
- Tutti i template usano Bootstrap 5
- Nessuna dipendenza esterna oltre Flask
- Sistema di punti estensibile

## Troubleshooting

### La tabella non viene creata?
Le tabelle vengono create automaticamente in `app.py::init_db()`

### Gli indizi non si rivelano?
Verifica la `revealed_date` della tabella `game_clues`. Deve essere in passato per apparire.

### Impossibile completare una sfida?
Verifica che:
1. L'utente sia loggato
2. La sfida non sia già stata completata
3. La sfida esista nel database

## File Principali

- `game_prize.py` - Logica e routes (620+ linee)
- `templates/game_prize/` - 7 file HTML
- Database tables - 7 tabelle + indici

---

Per documentazione completa vedi `GAME_PRIZE_SETUP.md`
