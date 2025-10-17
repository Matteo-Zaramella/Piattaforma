# Configurazione MCP Server di Render per Claude

## Cos'è MCP (Model Context Protocol)?

MCP è un protocollo che permette a Claude di connettersi direttamente ai tuoi servizi cloud (come Render) per gestirli autonomamente.

## Setup MCP Render per Claude Code

### 1. Ottieni API Key di Render

1. Vai su https://dashboard.render.com/account/api-keys
2. Click **Create API Key**
3. Nome: `Claude MCP Access`
4. Scopes: seleziona:
   - `read:services` - Leggere info servizi
   - `write:services` - Modificare servizi  
   - `read:deploys` - Vedere deployments
   - `write:deploys` - Triggerare deploy
   - `read:env-vars` - Leggere variabili ambiente
   - `write:env-vars` - Modificare variabili ambiente
5. Click **Create API Key**
6. **Copia la chiave** (la vedrai solo una volta!)

### 2. Installa MCP Server Render

Apri il terminale e installa il server MCP per Render:

```bash
npm install -g @modelcontextprotocol/server-render
```

### 3. Configura Claude Code

1. Apri le impostazioni di Claude Code
2. Trova la sezione **MCP Servers**
3. Aggiungi la configurazione per Render:

**Su Windows:**
Modifica `%APPDATA%\Claude\claude_desktop_config.json`

**Su macOS/Linux:**  
Modifica `~/.config/Claude/claude_desktop_config.json`

Aggiungi:

```json
{
  "mcpServers": {
    "render": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-render"],
      "env": {
        "RENDER_API_KEY": "TUA_API_KEY_QUI"
      }
    }
  }
}
```

### 4. Riavvia Claude Code

Chiudi completamente Claude Code e riaprilo.

### 5. Verifica Connessione

Chiedi a Claude:

```
Puoi vedere i miei servizi Render?
```

Claude dovrebbe essere in grado di:
- Listare tutti i tuoi servizi Render
- Vedere lo stato dei deploy
- Leggere le variabili d'ambiente  
- Triggerare nuovi deploy
- Modificare configurazioni

## Cosa Può Fare Claude con MCP Render?

Con MCP configurato, Claude può:

✅ **Vedere i servizi**
```
Mostrami tutti i miei servizi Render
```

✅ **Controllare deploy**
```
Qual è lo stato del deploy di piattaforma?
```

✅ **Leggere logs**
```
Mostrami gli ultimi log del servizio piattaforma
```

✅ **Gestire variabili d'ambiente**
```
Aggiungi la variabile DEBUG=True al servizio piattaforma
```

✅ **Triggerare deploy**
```
Fai un nuovo deploy di piattaforma
```

✅ **Diagnosticare problemi**
```
Perché il mio servizio piattaforma non funziona?
```

## Sicurezza

⚠️ **Importante:**
- L'API key ha accesso completo ai tuoi servizi Render
- Non condividere MAI l'API key
- Claude userà l'API solo quando richiesto
- Puoi revocare l'API key in qualsiasi momento

## Alternative: MCP Server Personalizzato

Se preferisci più controllo, puoi creare un MCP server personalizzato che espone solo endpoint specifici della tua app.

## Risoluzione Problemi

### MCP non si connette
1. Verifica che l'API key sia corretta
2. Controlla che `npx` sia installato: `npx --version`
3. Riavvia Claude Code completamente

### Claude non vede i servizi
1. Verifica scopes dell'API key
2. Controlla i logs di Claude Code
3. Prova a rigenerare l'API key

## Prossimi Passi

Una volta configurato MCP, puoi chiedere a Claude di:
- Automatizzare deploy quando fai modifiche
- Monitorare errori e fixarli
- Gestire variabili d'ambiente
- Scalare servizi

