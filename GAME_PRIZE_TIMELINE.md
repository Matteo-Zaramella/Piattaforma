# ⏰ Game Prize - Timeline e Meccanica di Visualizzazione

## Timeline Principale

### Oggi fino al 23 Gennaio 2026 (00:00)
**Stato: ⏳ COUNTDOWN**

Tutti i visitatori vedranno nella homepage pubblica:
- Sezione "Qualcosa di Speciale in Arrivo..."
- Mini countdown aggiornato in tempo reale (giorni, ore, minuti, secondi)
- Bottone "Visualizza il Countdown Completo" che rimanda a `/game-prize-reveal`

La pagina pubblica `/game-prize-reveal` mostra:
- Countdown a schermo intero con animazioni
- Descrizione del gioco
- Feature highlights (12 Sfide, Indizi Settimanali, Classifica Live, Un Vincitore)
- Al login, bottoni per accedere (che rimangono disabilitati fino al 24/01/2026)

**Area privata (Dopo login):**
- Game Prize NON è accessibile prima del 24/01/2026
- Se un utente prova ad accedere a `/game-prize/dashboard` prima della data, verrà reindirizzato
- Dashboard utente non mostra il link al Game Prize

---

### Mezzanotte del 24 Gennaio 2026 (00:00 esatte)
**Stato: 🎉 ATTIVO**

**Cosa cambia automaticamente:**

#### Homepage Pubblica
- La sezione countdown scompare automaticamente
- Appare la sezione "Game Prize è Attivo!"
- Bottoni per accedere al Game Prize e visualizzare classifica
- Mini countdown scompare

#### Area Privata
- Route `/game-prize/dashboard` diventa accessibile
- Route `/game-prize/admin/setup` diventa accessibile
- Tutti i link al Game Prize nella dashboard funzionano
- Admin panel diventa accessibile

#### Pagina Pubblica `/game-prize-reveal`
- Countdown scompare
- Messaggio di benvenuto appare
- Bottoni per giocare diventano abilitati
- Se non loggato: bottone "Accedi" attivo
- Se loggato: bottone "Accedi al Game Prize" attivo

---

## Implementazione Tecnica

### Context Processor in app.py
```python
@app.context_processor
def inject_game_prize_status():
    """Inietta lo stato del Game Prize in tutti i template"""
    from datetime import datetime
    game_reveal_date = datetime(2026, 1, 24, 0, 0, 0)
    is_game_revealed = datetime.now() >= game_reveal_date
    return dict(is_game_prize_revealed=is_game_revealed)
```

Questo fornisce a **TUTTI** i template la variabile `is_game_prize_revealed`:
- `True` dopo il 24/01/2026 00:00
- `False` prima di quella data

### Condizioni nei Template

#### Home pubblica (home.html)
```jinja2
{% if is_game_prize_revealed %}
    <!-- Sezione Game Prize Attivo -->
{% else %}
    <!-- Sezione Countdown -->
{% endif %}
```

#### Pagina Countdown (game_prize_countdown.html)
```javascript
const targetDate = new Date('2026-01-24T00:00:00').getTime();

function updateCountdown() {
    if (timeRemaining <= 0) {
        // Mostra contenuto rivelato
        document.getElementById('timerContent').style.display = 'none';
        document.getElementById('revealedContent').style.display = 'block';
    }
}
```

---

## Comportamento Dettagliato

### PRIMA del 24 Gennaio 2026

#### Visitatore Anonimo
1. Accede alla home pubblica `/`
2. Vede il countdown con mini timer aggiornato ogni secondo
3. Clicca "Visualizza il Countdown Completo"
4. Va a `/game-prize-reveal`
5. Vede countdown a schermo intero con feature description
6. Se clicca login/register e torna, vede "Devi essere loggato"
7. Se si registra/loga, vede bottoni disabilitati o rimandati al 24/01

#### Visitatore Loggato
1. Accede alla home privata `/dashboard`
2. Vede normalmente la sua dashboard
3. NO link al Game Prize nel menu
4. Se tenta di andare a `/game-prize/dashboard`: **ERRORE** o redirect
5. Nella homepage pubblica vede countdown come gli altri

### DOPO il 24 Gennaio 2026 (00:00)

#### Visitatore Anonimo
1. Accede alla home pubblica `/`
2. Vede "Game Prize è Attivo!" con bottoni
3. Se clicca "Accedi al Game Prize" -> va a `/login`
4. Dopo login, accede a `/game-prize/dashboard`

#### Visitatore Loggato
1. Accede a `/game-prize/dashboard`
2. Vede la dashboard con sfide
3. Accede alla classifica
4. Vede admin dashboard se admin

---

## Route Pubbliche vs Private

### Pubbliche (Sempre Accessibili)
```
GET  /                           Homepage (con countdown condizionato)
GET  /game-prize-reveal          Countdown page (con contenuto condizionato)
GET  /login                      Login
GET  /register                   Registrazione
```

### Private (Prima del 24/01: BLOCCATE, Dopo: APERTE)
```
GET  /game-prize/dashboard       Dashboard game (bloccato prima)
GET  /game-prize/challenge/<id>  Dettagli sfida (bloccato prima)
GET  /game-prize/leaderboard     Classifica (bloccato prima)
POST /game-prize/complete-challenge/<id> Completa sfida (bloccato prima)
```

### Admin (Prima del 24/01: BLOCCATE, Dopo: APERTE)
```
GET  /game-prize/admin/setup                Setup (bloccato prima)
GET  /game-prize/admin/dashboard            Dashboard admin (bloccato prima)
GET  /game-prize/admin/challenge/add        Aggiungi sfida (bloccato prima)
... altri admin routes ...
```

---

## Protezione con Decoratore (Opzionale)

Nel modulo `game_prize.py`, puoi aggiungere protezione con decoratore:

```python
from functools import wraps
from datetime import datetime

def game_prize_active(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        game_reveal_date = datetime(2026, 1, 24, 0, 0, 0)
        if datetime.now() < game_reveal_date:
            flash('Game Prize non è ancora attivo!', 'warning')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Usare come:
@bp.route('/dashboard')
@login_required
@game_prize_active  # <-- Protezione aggiuntiva
def dashboard():
    ...
```

---

## Mini Countdown nella Homepage

Il countdown nella homepage si aggiorna ogni secondo via JavaScript:
- Non ricarica la pagina
- Calcoli lato client (veloce e responsivo)
- Animazioni CSS smooth
- Fallback: reload automatico ogni 1 minuto per sincronizzazione

---

## Countdown Completo in `/game-prize-reveal`

La pagina a schermo intero:
- Animazioni più elaborate
- Pulse effect negli ultimi 10 secondi
- Transizione fluida quando il countdown scade
- Auto-refresh della pagina ogni 1 minuto per sincronizzazione

---

## Considerazioni Importanti

### Timezone
⚠️ **Attenzione:** Il countdown usa l'ora locale del browser client.

Se vuoi sincronizzare con un server time specifico:
```javascript
// Fetch server time
fetch('/api/server-time')
    .then(r => r.json())
    .then(data => {
        const serverTime = new Date(data.time).getTime();
        // Usa serverTime come riferimento
    });
```

### Caching
I template vengono cachati dal browser. Per forzare un refresh:
```python
@app.route('/game-prize-reveal')
def game_prize_reveal():
    response = make_response(render_template('game_prize_countdown.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response
```

### Mobile
Il countdown è fully responsive:
- Layout adattivo per mobile
- Touch-friendly buttons
- Font sizes readable su tutti i device

---

## Testing

Per testare il countdown senza aspettare gennaio 2026:

### Test 1: Modificare la data target
```python
# Nel context processor
game_reveal_date = datetime(2025, 10, 25, 0, 0, 0)  # Domani
```

### Test 2: Browser DevTools
```javascript
// Console
new Date('2026-01-24T00:00:00').getTime()
new Date().getTime()
// Calcola il differenziale
```

### Test 3: Sistema Operativo
Cambia la data sistema a gennaio 2026 (non consigliato per produzione)

---

## File Modificati/Creati

### Nuovi
- `templates/game_prize_countdown.html` - Countdown page
- `GAME_PRIZE_TIMELINE.md` - Questo file

### Modificati
- `app.py`:
  - Aggiunto context processor `inject_game_prize_status()`
  - Aggiunta route `/game-prize-reveal`

- `templates/home.html`:
  - Aggiunta sezione condizionata per countdown
  - Aggiunto mini countdown con JavaScript

---

## Flusso di Attivazione Riassunto

```
├─ Oggi → 23 Gennaio 2026 23:59:59
│  ├─ Homepage: Countdown visibile
│  ├─ /game-prize-reveal: Countdown visibile
│  └─ /game-prize/*: NON accessibili
│
└─ 24 Gennaio 2026 00:00:00 →
   ├─ Homepage: Game Prize Attivo visibile
   ├─ /game-prize-reveal: Contenuto rivelato
   └─ /game-prize/*: ACCESSIBILI
```

---

**Data Ultima Modifica:** 22 Ottobre 2025
**Target Release:** 24 Gennaio 2026 00:00
**Tempo Rimanente:** ~443 giorni (approssimativamente)
