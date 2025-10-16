# Changelog - Implementazione Impostazioni e Modalità Scura

**Data:** Ottobre 2025
**Versione:** 1.1.0

## Nuove Funzionalità

### Sezione Impostazioni Completa

#### 1. Sistema di Preferenze Utente
- ✓ Nuova tabella database `user_preferences`
- ✓ Gestione preferenze per utente
- ✓ Persistenza tra le sessioni
- ✓ Valori di default automatici

#### 2. Modalità Scura
- ✓ Toggle modalità scura/chiara
- ✓ Tema scuro ottimizzato per tutti i componenti:
  - Navbar
  - Card
  - Tabelle
  - Form e input
  - Modali
  - Alert
  - Badge
- ✓ Transizioni fluide tra i temi
- ✓ Applicazione automatica al login
- ✓ Toggle rapido senza ricarica pagina (AJAX)

#### 3. Interfaccia Impostazioni
- ✓ Pagina dedicata `/settings`
- ✓ Sezione Aspetto (Dark Mode, Lingua)
- ✓ Sezione Notifiche
- ✓ Sezione Account
- ✓ Informazioni sistema
- ✓ Scorciatoie rapide

#### 4. API REST
- ✓ `GET /settings/` - Visualizza impostazioni
- ✓ `POST /settings/update` - Salva preferenze
- ✓ `POST /settings/toggle-dark-mode` - Toggle rapido
- ✓ `GET /settings/get-preferences` - API JSON

## File Modificati

### Nuovi File
1. `modules/settings.py` - Modulo gestione impostazioni
2. `templates/settings.html` - Interfaccia utente
3. `add_preferences_table.py` - Script migrazione DB
4. `IMPOSTAZIONI.md` - Documentazione
5. `CHANGELOG_SETTINGS.md` - Questo file

### File Aggiornati
1. `app.py`
   - Aggiunta tabella `user_preferences` in `init_db()`
   - Registrato blueprint `settings`
   - Aggiunto context processor per preferenze

2. `templates/base.html`
   - Aggiunto supporto classe `dark-mode`
   - Aggiunto link Impostazioni nella navbar

3. `static/css/style.css`
   - Aggiunte variabili CSS per temi
   - Implementato tema scuro completo
   - Transizioni fluide

## Schema Database

```sql
-- Nuova tabella
CREATE TABLE user_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    dark_mode BOOLEAN DEFAULT 0,
    language TEXT DEFAULT 'it',
    notifications BOOLEAN DEFAULT 1,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

## Come Utilizzare

### Per Utenti Esistenti
1. Esegui: `python add_preferences_table.py`
2. Riavvia l'applicazione: `python app.py`
3. Accedi a http://localhost:5000/settings

### Per Nuove Installazioni
1. Le preferenze vengono create automaticamente al primo login

### Attivare la Modalità Scura
**Metodo 1 - Persistente:**
1. Vai su Impostazioni
2. Attiva "Modalità Scura"
3. Clicca "Salva Modifiche"

**Metodo 2 - Toggle Rapido:**
1. Vai su Impostazioni
2. Clicca "Toggle Modalità Scura" nelle scorciatoie

## Caratteristiche Tecniche

### Dark Mode CSS
- Variabili CSS personalizzate (`--bg-color`, `--text-color`, ecc.)
- Classe `.dark-mode` sul tag `<body>`
- Transizioni CSS smooth (0.3s ease)
- Compatibilità Bootstrap 5

### Context Processor
- Carica automaticamente `dark_mode` in tutti i template
- Query efficiente (solo campo necessario)
- Nessun impatto su performance

### JavaScript
- Fetch API per toggle rapido
- Feedback visivo immediato
- Nessuna ricarica pagina necessaria

## Testing

L'applicazione è stata testata per:
- ✓ Creazione automatica preferenze
- ✓ Toggle modalità scura
- ✓ Persistenza tra sessioni
- ✓ Compatibilità con tutti i moduli esistenti
- ✓ Migrazione database senza perdita dati

## Compatibilità

- ✓ Windows (testato)
- ✓ Python 3.8+
- ✓ Flask 2.x
- ✓ Bootstrap 5.3
- ✓ Tutti i browser moderni

## Funzionalità Future

### Prossime Versioni
- [ ] Cambio password dall'interfaccia
- [ ] Modifica username
- [ ] Tema personalizzato (scelta colori)
- [ ] Internazionalizzazione (i18n)
- [ ] Notifiche push
- [ ] Preferenze per modulo
- [ ] Esporta/importa impostazioni
- [ ] Modalità ad alto contrasto
- [ ] Font size personalizzabile

## Breaking Changes

Nessuno - Completamente retrocompatibile con versioni precedenti.

## Migrazione

Per aggiornare da versione 1.0.0:
```bash
cd Desktop/Piattaforma
python add_preferences_table.py
```

## Contributors

- Sviluppo: Claude Code
- Design: Bootstrap 5
- Testing: Utente finale

---

**Note:** Questa implementazione è production-ready e non contiene breaking changes.
