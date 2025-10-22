# 🎮 Game Prize - Guida di Setup e Utilizzo

## Panoramica del Progetto

**Game Prize** è un'app interna della piattaforma che gestisce un gioco a premi strutturato della durata di un anno, che culmina nella festa di compleanno dei 25 anni.

### Caratteristiche Principali

- **12 Sfide** distribuite nell'arco di un anno
- **Sistema di Punti** per tracciare i progressi
- **Classifica in Tempo Reale** con posizionamenti
- **Indizi Settimanali** per guidare i giocatori alla prossima sfida
- **Rivelazione del Vincitore** al 50% del gioco (dopo 6 sfide)
- **Finale alla Festa** di compleanno con la 12ª sfida

---

## Setup Iniziale

### 1. Accedi al Dashboard Admin
```
URL: /game-prize/admin/dashboard
```

### 2. Configura il Gioco
Vai a `/game-prize/admin/setup` e compila:
- **Nome del Gioco**: es. "Premio di Compleanno - 24→25 Anni"
- **Data Inizio**: Quando inizia il gioco
- **Data Fine**: Il giorno della festa (24+1 anni)
- **Numero Totale Sfide**: Default 12
- **Descrizione**: Breve descrizione del gioco

### 3. Crea le 12 Sfide
Dal dashboard admin, clicca "➕ Aggiungi Sfida" e configura:
- Numero sfida (1-12)
- Titolo e descrizione
- Punti (es. 100 punti per sfida)
- Istruzioni dettagliate
- Data inizio/fine (opzionale)
- Luogo (opzionale)

### 4. Aggiungi Indizi per Ogni Sfida
Per ogni sfida, clicca "💡 Aggiungi Indizio":
- **Numero Indizio**: 1°, 2°, 3° indizio
- **Testo**: L'indizio che aiuta a trovare la sfida
- **Data Rivelazione**: Quando mostrare l'indizio

**Suggerimento**: Spalma gli indizi nella settimana
- Lunedì: 1° indizio
- Mercoledì: 2° indizio
- Venerdì: 3° indizio

---

## Flusso del Gioco per i Giocatori

### Dashboard Principale
`/game-prize/dashboard`

Mostra:
- Punti totali accumulati
- Barra di progresso sfide completate
- Elenco di tutte le sfide (completate/non completate)
- Link alla classifica

### Pagina Singola Sfida
`/game-prize/challenge/<id>`

Mostra:
- Descrizione completa della sfida
- Indizi disponibili (organizzati in accordion)
- Bottone "Segna come Completata"
- Punti da guadagnare

### Classifica
`/game-prize/leaderboard`

Mostra:
- Posizioni attuali di tutti i giocatori
- Punti totali per giocatore
- Numero sfide completate
- Avviso quando il 50% delle sfide è stato raggiunto

---

## Meccanica di Rivelazione del Vincitore

### Fase 1: Primo 50% (6 sfide su 12)
- Nessuno sa chi sta vincendo
- I giocatori completano sfide alla cieca
- La classifica mostra posizioni ma non è determinante

### Fase 2: Rivelazione al 50%
Quando il 50% delle sfide (6 su 12) è stato completato da almeno un giocatore:
- **Avviso**: Appare nelle classifica e dashboard
- **Alert**: "È stato raggiunto il 50% del gioco!"
- **Effetto**: I giocatori ora sanno che c'è una competizione vera

### Fase 3: Finale
Alla festa di compleanno (data_end):
- Si gioca la 12ª sfida finale
- Viene annunciato il vincitore finale
- Celebrazione e premio

---

## Database Schema

### Tabelle Principali

#### `game_prize_config`
Configurazione generale del gioco
- `game_name`: Nome del gioco
- `start_date`: Inizio gioco
- `end_date`: Fine gioco (data festa)
- `total_challenges`: Numero totale sfide
- `description`: Descrizione

#### `game_challenges`
Le singole sfide
- `challenge_number`: Numero sfida (1-12)
- `title`: Nome sfida
- `description`: Descrizione
- `points`: Punti da assegnare
- `start_date`, `end_date`: Disponibilità
- `location`: Dove si svolge
- `instructions`: Come completarla

#### `game_clues`
Indizi per trovare le sfide
- `challenge_id`: Sfida a cui appartiene
- `clue_number`: Numero indizio (1°, 2°, etc)
- `clue_text`: Testo dell'indizio
- `revealed_date`: Quando mostrarlo

#### `game_user_completions`
Traccia quali sfide hanno completato i giocatori
- `user_id`: Chi ha completato
- `challenge_id`: Quale sfida
- `completed_date`: Quando

#### `game_user_scores`
Punti guadagnati
- `user_id`: Chi ha guadagnato
- `challenge_id`: Da quale sfida
- `points`: Quanti punti

#### `game_winner_reveal`
Traccia la rivelazione del vincitore
- `revealed`: Se è già stato rivelato
- `revealed_date`: Quando
- `winner_user_id`: ID del vincitore

---

## Routes API

### Per Utenti
```
GET  /game-prize/dashboard              → Dashboard principale
GET  /game-prize/challenge/<id>         → Dettagli singola sfida
POST /game-prize/complete-challenge/<id> → Marca sfida completata (JSON)
GET  /game-prize/clues/<id>             → Ottieni indizi (JSON API)
GET  /game-prize/leaderboard            → Classifica
```

### Per Admin
```
GET  /game-prize/admin/setup             → Configurazione gioco
POST /game-prize/admin/setup             → Salva configurazione
GET  /game-prize/admin/dashboard         → Dashboard admin
GET  /game-prize/admin/challenge/add     → Form aggiungi sfida
POST /game-prize/admin/challenge/add     → Salva nuova sfida
GET  /game-prize/admin/challenge/<id>/edit → Form modifica
POST /game-prize/admin/challenge/<id>/edit → Salva modifiche
GET  /game-prize/admin/clue/add/<id>     → Form aggiungi indizio
POST /game-prize/admin/clue/add/<id>     → Salva indizio
```

---

## TODO e Prossimi Passi

### Fase 1 (Completata ✅)
- [x] Struttura database
- [x] Routes e blueprint
- [x] Template HTML
- [x] Sistema di punti base

### Fase 2 (Da implementare)
- [ ] Protezione password per admin (?)
- [ ] Email notifications per indizi settimanali
- [ ] Statistiche avanzate nel dashboard admin
- [ ] Export classifica (CSV, PDF)
- [ ] Chat/Forum privato per giocatori
- [ ] Foto/media per sfide

### Fase 3 (Integrazioni future)
- [ ] Integrazione con Instagram (posting automatici)
- [ ] QR codes per sfide location-based
- [ ] Mobile app nativa
- [ ] Countdown timer verso il giorno finale

---

## Configurazione Suggerita

### Esempio: 12 Sfide per 12 Mesi

```
Sfida 1:  Novembre (inizio)
Sfida 2:  Dicembre
Sfida 3:  Gennaio
Sfida 4:  Febbraio
Sfida 5:  Marzo
Sfida 6:  Aprile      ← 50% Rivelazione vincitore
Sfida 7:  Maggio
Sfida 8:  Giugno
Sfida 9:  Luglio
Sfida 10: Agosto
Sfida 11: Settembre
Sfida 12: Ottobre (Festa di compleanno)
```

---

## Monetizzazione / Premi Suggeriti

Quando deciderai il numero esatto di partecipanti e la lista:
- Considera un pool premi
- Premi per piazzamenti: 1°, 2°, 3°
- Premi speciali per milestone (50% raggiunto, etc)
- Premi consolazione per partecipazione

---

## File Struttura

```
piattaforma/
├── modules/
│   └── game_prize.py           ← Logica e routes
├── templates/
│   └── game_prize/
│       ├── dashboard.html
│       ├── challenge_detail.html
│       ├── leaderboard.html
│       ├── admin_setup.html
│       ├── admin_dashboard.html
│       ├── admin_add_challenge.html
│       ├── admin_edit_challenge.html
│       └── admin_add_clue.html
├── app.py                      ← Blueprint registrato
└── GAME_PRIZE_SETUP.md         ← Questo file
```

---

## Contatti e Domande

Per domande o modifiche futuri:
- Vedi PROJECT_SUMMARY.md per panoramica generale
- Vedi TECHNICAL_DOCS.md per dettagli tecnici
- Contatta per aggiornamenti su partecipanti

---

**Buona fortuna con il gioco! 🎉🎮**
