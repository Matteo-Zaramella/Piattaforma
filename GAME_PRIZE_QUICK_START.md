# ⚡ Game Prize - Quick Start

## 🚀 5 Minuti di Setup

### Step 1: Accedi al Setup
```
http://localhost:5000/game-prize/admin/setup
```

### Step 2: Compila il Form
- Nome: "Premio di Compleanno"
- Inizio: 2024-11-01
- Fine: 2025-10-24 (tuo compleanno)
- Sfide: 12
- Clicca "Salva Configurazione"

### Step 3: Vai al Dashboard Admin
```
http://localhost:5000/game-prize/admin/dashboard
```

### Step 4: Aggiungi 12 Sfide
Clicca "➕ Aggiungi Sfida" 12 volte:
- Numero: 1-12
- Titolo: es. "Sfida del Lago"
- Punti: 100 (o quello che preferisci)
- Clicca "Crea Sfida"

### Step 5: Aggiungi Indizi
Per ogni sfida:
- Clicca "💡 Aggiungi Indizio"
- Numero indizio: 1, 2, 3
- Testo: L'indizio per trovare la sfida
- Data rivelazione: settimanale (lunedì/mercoledì/venerdì)
- Clicca "Aggiungi Indizio"

## ✅ Fatto!

Il gioco è attivo. Ora:

1. **Invita i giocatori** a registrarsi
2. **Condividi il link**: `/game-prize/dashboard`
3. **Monitora dal dashboard admin**: `/game-prize/admin/dashboard`

---

## 🎯 URL Principales

| Chi | URL | Cosa Vede |
|-----|-----|-----------|
| Giocatore | `/game-prize/dashboard` | Sfide e punti |
| Giocatore | `/game-prize/challenge/1` | Sfida dettagliata |
| Giocatore | `/game-prize/leaderboard` | Classifica |
| Admin | `/game-prize/admin/setup` | Configurazione |
| Admin | `/game-prize/admin/dashboard` | Gestione sfide |

---

## 📋 Checklist

- [ ] Ho completato il setup
- [ ] Ho creato 12 sfide
- [ ] Ho aggiunto indizi per ogni sfida
- [ ] Ho invitato i giocatori
- [ ] Ho testato il dashboard dei giocatori
- [ ] Ho testato la classifica

---

## 🎮 Come Testare

1. **Accedi come giocatore** (registrati)
2. **Vai a `/game-prize/dashboard`**
3. **Clicca su una sfida**
4. **Clicca "Segna come Completata"**
5. **Vedi i punti aumentare**
6. **Vai a `/game-prize/leaderboard`**
7. **Vedi la tua posizione**

---

## 🚨 Se Qualcosa Non Funziona

1. **Sfide non appaiono?**
   - Verifica di aver salvato le sfide nel setup
   - Controlla che le sfide siano create nel dashboard admin

2. **Indizi non si vedono?**
   - La `revealed_date` deve essere nel passato

3. **Errore di login?**
   - Registrati prima da `/register`
   - Poi accedi da `/login`

4. **Errore database?**
   - Restart l'app: `python app.py`
   - Verifica che il database sia inizializzato

---

## 📞 Aiuto

Vedi la documentazione completa in:
- `GAME_PRIZE_SETUP.md` - Guida dettagliata
- `modules/GAME_PRIZE_README.md` - Dettagli tecnici

---

**Buon gioco! 🎉**
