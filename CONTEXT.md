# Contesto Progetto - Piattaforma

## Per Claude in Nuove Conversazioni

**LEGGIMI PRIMA DI TUTTO!**

Questo progetto si chiama **Piattaforma** ed è un hub centralizzato per gestione personale.

## Informazioni Chiave

### Ubicazione
- **Path**: `C:\Users\offic\Desktop\Piattaforma`
- **Linguaggio**: Python/Flask
- **Database**: SQLite (`piattaforma.db`)

### Moduli Principali
1. **Matched Betting** (`modules/matched_betting.py`)
   - Traccia scommesse matched betting
   - Campi: bookmaker (back/lay), stake, quote, rating, mercato, offerta, evento, data, profitto
   - Include integrazione Google Calendar (TODO)

2. **Task Lavoro** (`modules/task_lavoro.py`)
   - Gestione task lavorativi
   - Campi: titolo, descrizione, priorità, stato, deadline

3. **Task Privati** (`modules/task_privati.py`)
   - Gestione task personali
   - Come Task Lavoro + flag "ricorrente"

4. **Fitness** (`modules/fitness.py`)
   - **Pasti**: data, tipo_pasto, descrizione (solo menù)
   - **Allenamenti**: data, esercizio, ripetizioni, peso, note

5. **Impostazioni** (`modules/settings.py`) ✨ NUOVO
   - **Modalità Scura**: Toggle tema chiaro/scuro con persistenza
   - **Lingua**: Selezione IT/EN/ES (preparato per i18n)
   - **Notifiche**: Toggle per abilitare/disabilitare
   - **Preferenze Utente**: Tabella `user_preferences` in database
   - **API**: Endpoint per toggle rapido e fetch preferenze

### Caratteristiche Speciali
- **Login/Registrazione**: Password hashate con bcrypt
- **Dev Tools**: Interfaccia per modificare codice
  - Password: `dev_access_2024`
  - Route: `/dev-tools`
- **Single-user**: App personale, non multi-tenant
- **API REST**: Pronta ma non documentata (TODO)

### Tech Stack
- **Backend**: Flask 3.0
- **Frontend**: Bootstrap 5 + Vanilla JS
- **Database**: SQLite
- **Template Engine**: Jinja2

### Struttura File
```
Piattaforma/
├── app.py              # App principale + blueprints
├── modules/            # 4 moduli (blueprints)
├── templates/          # HTML Jinja2
├── static/            # CSS + JS
├── piattaforma.db     # Database SQLite
└── requirements.txt   # Dipendenze
```

### Avvio Applicazione
```bash
cd C:\Users\offic\Desktop\Piattaforma
python app.py
# Oppure: doppio click su start.bat
```

Server: http://localhost:5000

### Password e Credenziali
- **Dev Tools Password**: `dev_access_2024`
- **User account**: Creato dall'utente via registrazione web

### TODO / In Sviluppo
- [ ] Google Calendar integration per promemoria scommesse
- [ ] API REST documentation
- [ ] Export/Import dati (CSV, JSON)
- [ ] Notifiche push
- [ ] Grafici statistiche avanzate

### Note Importanti
- Debug mode sempre ON in sviluppo
- Database SQLite locale (non cloud)
- Auto-reload attivo per modifiche codice
- Responsive design (mobile-friendly)

### Come Aiutare l'Utente

**Se l'utente chiede modifiche/aggiunte:**
1. Leggi il file pertinente (es. `modules/matched_betting.py`)
2. Leggi il template correlato se necessario
3. Implementa la modifica
4. Spiega cosa hai fatto

**Se c'è un errore:**
1. Controlla i log (cerca traceback)
2. Leggi il file con l'errore
3. Correggi
4. Testa se possibile

**Per nuove funzionalità:**
1. Analizza architettura esistente
2. Mantieni coerenza con pattern usati (Blueprint, SQLite, Jinja2)
3. Segui lo stile esistente (Bootstrap 5, card-based UI)
4. Aggiorna README.md se necessario

### Contatti con Utente
- L'utente comunica via Claude Code (ha accesso filesystem)
- Può condividere screenshot salvandoli e dandomi il path
- Può usare Dev Tools nell'app per vedere/copiare codice
- Preferisce soluzioni dirette e funzionali

### Linguaggio
- **Interfaccia**: Italiano
- **Codice**: Inglese (variabili, funzioni)
- **Commenti**: Italiano
- **Documentazione**: Italiano

---

**Ultima Modifica**: Ottobre 2025
**Versione**: 1.1.0
**Creato con**: Claude Code (Sonnet 4.5)

### Deployment
- **Dominio**: matteozaramella.com (Squarespace)
- **Hosting**: Da configurare per Flask/Python app
- **Accesso**: Password-protected per utente e amici selezionati

## Quick Commands per Claude

```python
# Leggere modulo
Read: C:\Users\offic\Desktop\Piattaforma\modules\[modulo].py

# Leggere template
Read: C:\Users\offic\Desktop\Piattaforma\templates\[modulo]\[file].html

# Leggere app principale
Read: C:\Users\offic\Desktop\Piattaforma\app.py

# Verificare struttura
Bash: cd "C:\Users\offic\Desktop\Piattaforma" && ls -la

# Controllare dipendenze
Read: C:\Users\offic\Desktop\Piattaforma\requirements.txt
```

## FAQ Rapide

**Q: Come aggiungo una nuova funzionalità al matched betting?**
A: Leggi `modules/matched_betting.py` e il template corrispondente, implementa seguendo il pattern esistente

**Q: L'app non parte?**
A: Verifica che Flask sia installato: `pip install Flask`

**Q: Dove sono i dati?**
A: Nel database SQLite `piattaforma.db` nella root del progetto

**Q: Come modifico l'interfaccia?**
A: Templates in `templates/`, CSS in `static/css/style.css`

**Q: Password dimenticata?**
A: Elimina `piattaforma.db` e ricrea account (perdi dati!)

---

**Questo file serve per ambientarti velocemente in nuove conversazioni!**
