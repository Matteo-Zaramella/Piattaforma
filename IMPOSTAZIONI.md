# Guida alle Impostazioni

## Panoramica

La sezione Impostazioni della Piattaforma ti permette di personalizzare l'esperienza utente secondo le tue preferenze.

## Come Accedere

1. Effettua il login
2. Clicca su "Impostazioni" nella barra di navigazione (icona ingranaggio)
3. Oppure vai direttamente a: http://localhost:5000/settings

## Funzionalità Disponibili

### 1. Modalità Scura

La modalità scura riduce l'affaticamento visivo e il consumo della batteria.

**Come attivarla:**
- Vai su Impostazioni
- Attiva lo switch "Modalità Scura"
- Clicca su "Salva Modifiche"

**Toggle Rapido:**
- Nella pagina Impostazioni, usa il pulsante "Toggle Modalità Scura" per un cambio istantaneo
- Il tema si applica immediatamente senza dover salvare

**Caratteristiche:**
- Sfondo scuro (#1a1a1a)
- Card con sfondo (#2d2d2d)
- Testo chiaro per leggibilità
- Transizioni fluide tra i temi
- Si applica a tutte le pagine dell'applicazione

### 2. Lingua

**Opzioni disponibili:**
- Italiano (predefinito)
- English
- Español

**Nota:** L'internazionalizzazione completa sarà disponibile in una versione futura.

### 3. Notifiche

Abilita o disabilita le notifiche per:
- Scadenze task
- Promemoria
- Eventi fitness

**Nota:** Le notifiche push saranno implementate in futuro.

### 4. Informazioni Account

Visualizza:
- Username attuale
- Versione della piattaforma
- Data ultimo aggiornamento preferenze

## Persistenza delle Impostazioni

Tutte le preferenze sono salvate nel database e vengono:
- Caricate automaticamente ad ogni login
- Applicate a tutte le pagine
- Conservate tra le sessioni

## Scorciatoie Rapide

La pagina Impostazioni include scorciatoie per:
- Toggle rapido Modalità Scura
- Accesso a Dev Tools

## Sviluppo Tecnico

### Struttura Database

```sql
CREATE TABLE user_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    dark_mode BOOLEAN DEFAULT 0,
    language TEXT DEFAULT 'it',
    notifications BOOLEAN DEFAULT 1,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
```

### File Coinvolti

- **Backend:** `modules/settings.py`
- **Template:** `templates/settings.html`
- **CSS:** `static/css/style.css` (sezione Dark Mode)
- **Base Template:** `templates/base.html` (applicazione tema)

### API Endpoints

- `GET /settings/` - Pagina impostazioni
- `POST /settings/update` - Salva preferenze
- `POST /settings/toggle-dark-mode` - Toggle rapido dark mode (AJAX)
- `GET /settings/get-preferences` - Ottieni preferenze (JSON)

## Funzionalità Future

- [ ] Cambio password
- [ ] Modifica username
- [ ] Notifiche push
- [ ] Internazionalizzazione completa
- [ ] Tema personalizzato (scelta colori)
- [ ] Impostazioni privacy
- [ ] Esporta/Importa dati
- [ ] Autenticazione a due fattori

## Risoluzione Problemi

### Le preferenze non si salvano

1. Verifica che il database sia scrivibile
2. Controlla i permessi del file `piattaforma.db`
3. Controlla i log per errori SQL

### La modalità scura non si applica

1. Svuota la cache del browser (Ctrl+F5)
2. Verifica che il CSS `style.css` sia caricato
3. Controlla la console del browser per errori JavaScript

### Aggiornamento Database

Se hai installato la Piattaforma prima dell'introduzione delle impostazioni, esegui:

```bash
python add_preferences_table.py
```

Questo script:
- Crea la tabella `user_preferences` se non esiste
- Aggiunge preferenze di default per tutti gli utenti esistenti
- Mantiene tutti i dati esistenti intatti

## Supporto

Per assistenza tecnica, usa la sezione Dev Tools o consulta la documentazione principale.

---

**Versione:** 1.1.0
**Data:** Ottobre 2025
**Sviluppato con:** Claude Code
