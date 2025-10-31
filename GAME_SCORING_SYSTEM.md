# Sistema Punteggi Game Prize

## Struttura Punteggi

### Sfide Principali (12 sfide)
- **1° posto**: 500 punti
- **2° posto**: 400 punti
- **3° posto**: 300 punti
- **4° posto**: 250 punti
- **5° posto**: 200 punti
- **6°-10° posto**: 150 punti
- **11°-20° posto**: 100 punti
- **21°+ posto**: 50 punti

### Indizi (4 indizi per sfida = 48 indizi totali)
- **1° a completare indizio**: 100 punti
- **2° posto**: 75 punti
- **3° posto**: 50 punti
- **4°-10° posto**: 25 punti
- **11°+ posto**: 10 punti

### Bonus Presentazione (21/02/2026)
- Presenza alla festa: **200 punti** (bonus starter)

## Calcolo Punteggi

### Scenario BEST CASE (tutto primo posto)
```
Bonus presentazione:        200 punti
12 sfide × 500:          6,000 punti
48 indizi × 100:         4,800 punti
─────────────────────────────────────
TOTALE MASSIMO:         11,000 punti
```

### Scenario WORST CASE (tutto ultimo posto)
```
Bonus presentazione:        200 punti (se presente)
12 sfide × 50:            600 punti
48 indizi × 10:           480 punti
─────────────────────────────────────
TOTALE MINIMO:          1,280 punti
```

### Scenario MEDIO (mix posizioni)
```
Bonus presentazione:        200 punti
6 sfide top 10 (media 250): 1,500 punti
6 sfide 11-20 posto:        600 punti
24 indizi top 10 (media 50): 1,200 punti
24 indizi dopo 10° (10pt):  240 punti
─────────────────────────────────────
TOTALE MEDIO:           3,740 punti
```

## Soglia Accesso Sfida Finale

### Analisi Distribuzione
Con ~100 partecipanti:
- Top 10% (10 persone): 7,000+ punti
- Top 30% (30 persone): **4,500+ punti** ✅
- Top 50% (50 persone): 3,500+ punti
- Bottom 50%: < 3,500 punti

### SOGLIA SCELTA: 4,500 punti

**Motivazione:**
- Richiede partecipazione costante
- ~30 persone qualificate per finale
- Deve fare almeno 6-7 sfide in top 10
- + completare ~50% indizi tempestivamente

## Sfida Finale (13° Sfida - 24/01/2027)

### Accesso
- **REQUISITO**: Minimo 4,500 punti accumulati
- Chi non raggiunge soglia: NON può partecipare
- Notifica automatica a chi è qualificato

### Punteggio Finale
```
Punteggio accumulato (fino a 11,000): peso 60%
Performance sfida finale:              peso 40%

FORMULA:
Punteggio Finale = (Punti Accumulati × 0.6) + (Punti Sfida Finale × 0.4)
```

### Esempio
```
Giocatore A: 8,000 punti + 500 finale = (8,000×0.6) + (500×0.4) = 5,000 FINALE
Giocatore B: 6,000 punti + 500 finale = (6,000×0.6) + (500×0.4) = 3,800 FINALE
Giocatore C: 4,600 punti + 500 finale = (4,600×0.6) + (500×0.4) = 2,960 FINALE
Giocatore D: 4,400 punti = NON QUALIFICATO ❌
```

## Implementazione Database

### Tabella punteggi dettagliati
```sql
CREATE TABLE game_detailed_scores (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    challenge_id INTEGER,
    clue_id INTEGER,
    position INTEGER NOT NULL,
    points INTEGER NOT NULL,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (challenge_id) REFERENCES game_challenges(id),
    FOREIGN KEY (clue_id) REFERENCES game_clues(id)
);
```

### Query soglia finale
```sql
SELECT u.id, u.username, SUM(gds.points) as total_points
FROM users u
JOIN game_detailed_scores gds ON u.id = gds.user_id
GROUP BY u.id, u.username
HAVING SUM(gds.points) >= 4500
ORDER BY total_points DESC;
```

## Dashboard Admin

### Statistiche da mostrare
1. Distribuzione punteggi (grafico)
2. Numero qualificati per finale (live counter)
3. Punteggio medio / mediano
4. Top 10 classifica
5. Proiezione vincitore

### Alert automatici
- A 6 sfide (50%): mostra proiezione qualificati
- A 9 sfide (75%): alert a chi è sotto 3,500 punti
- A 11 sfide (92%): alert finale a chi è border-line

---

**Aggiornato:** 31 Ottobre 2025
**Sistema punteggi:** v2.0 finale
