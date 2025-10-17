# Setup Dominio Personalizzato con Cloudflare

## Collegare matteozaramella.com a Piattaforma su Render

### Prerequisiti
- Dominio matteozaramella.com già in Cloudflare
- Accesso a Cloudflare dashboard
- Servizio Piattaforma deployato su Render

---

## Passo 1: Configurare Custom Domain su Render

1. Vai su Render Dashboard: https://dashboard.render.com/web/srv-d3of691r0fns73c5t110
2. Click tab **Settings**
3. Scorri a **Custom Domains**
4. Click **Add Custom Domain**
5. Inserisci il dominio desiderato:
   - Opzione A: `app.matteozaramella.com` (subdomain consigliato)
   - Opzione B: `piattaforma.matteozaramella.com`
   - Opzione C: `matteozaramella.com` (root domain)

6. Render ti mostrerà i record DNS da configurare

---

## Passo 2: Configurare DNS su Cloudflare

### Per Subdomain (es. app.matteozaramella.com)

1. Vai su Cloudflare Dashboard
2. Seleziona dominio **matteozaramella.com**
3. Vai a **DNS** → **Records**
4. Click **Add record**
5. Configura CNAME:
   ```
   Type: CNAME
   Name: app (o piattaforma)
   Target: piattaforma.onrender.com
   Proxy status: DNS only (grigio, non arancione)
   TTL: Auto
   ```
6. Click **Save**

### Per Root Domain (matteozaramella.com)

**Opzione A: CNAME Flattening (Automatico con Cloudflare)**
```
Type: CNAME
Name: @ (root)
Target: piattaforma.onrender.com
Proxy status: DNS only
TTL: Auto
```

**Opzione B: A Record (IP statico)**
Render ti fornirà IP specifici - aggiungi record A:
```
Type: A
Name: @ (root)
Target: [IP fornito da Render]
Proxy status: DNS only
TTL: Auto
```

---

## Passo 3: Verificare Configurazione

1. Torna su Render Dashboard
2. Vai a **Custom Domains**
3. Attendi che lo stato diventi **Verified** (può richiedere fino a 48h, ma di solito 5-10 minuti)
4. Render genererà automaticamente certificato SSL Let's Encrypt

---

## Passo 4: Abilitare Cloudflare Proxy (Opzionale ma Consigliato)

Una volta che il dominio è verificato su Render:

1. Torna su Cloudflare DNS
2. Modifica il record CNAME/A
3. Cambia **Proxy status** da grigio (DNS only) ad **arancione (Proxied)**
4. Questo abilita:
   - CDN globale (sito più veloce)
   - DDoS protection
   - Analytics
   - Caching automatico

---

## Passo 5: Configurare SSL/TLS su Cloudflare

1. Va su Cloudflare → **SSL/TLS**
2. Seleziona modalità: **Full (strict)**
   - Questo garantisce HTTPS end-to-end
   - Render già fornisce certificato SSL
3. Opzionale: Abilita **Always Use HTTPS**
   - Redireziona automaticamente HTTP → HTTPS

---

## Passo 6: Ottimizzazioni Cloudflare (Opzionali)

### Caching
1. **Caching Level**: Standard
2. **Browser Cache TTL**: 4 hours

### Performance
1. **Auto Minify**: Abilita HTML, CSS, JS
2. **Brotli**: Abilita
3. **HTTP/3 (with QUIC)**: Abilita

### Security
1. **Security Level**: Medium
2. **Bot Fight Mode**: Abilita (per piano Free)

---

## Verifica Finale

Una volta completata la configurazione:

1. Apri il browser in incognito
2. Vai a: `https://app.matteozaramella.com` (o il dominio scelto)
3. Verifica:
   - ✅ Sito carica correttamente
   - ✅ Certificato SSL valido (lucchetto verde)
   - ✅ Nessun errore mixed content

---

## Comandi Verifica DNS

```bash
# Verifica CNAME
nslookup app.matteozaramella.com

# Verifica propagazione DNS globale
# Vai su: https://dnschecker.org

# Test SSL
curl -I https://app.matteozaramella.com
```

---

## Configurazioni Avanzate

### Redirect Root → Subdomain

Se usi subdomain (app.matteozaramella.com) ma vuoi che matteozaramella.com reindirizzi:

1. Cloudflare → **Rules** → **Page Rules**
2. Aggiungi regola:
   ```
   URL: matteozaramella.com/*
   Setting: Forwarding URL (301 Permanent Redirect)
   Destination: https://app.matteozaramella.com/$1
   ```

### Multiple Subdomains

Puoi configurare più subdomain per servizi diversi:
- `app.matteozaramella.com` → Piattaforma
- `api.matteozaramella.com` → API backend (futuro)
- `blog.matteozaramella.com` → Blog (futuro)

---

## Troubleshooting

### "ERR_TOO_MANY_REDIRECTS"
- Problema: Loop di redirect
- Soluzione: Cambia SSL/TLS mode da "Flexible" a "Full (strict)"

### "This site can't be reached"
- Problema: DNS non propagato
- Soluzione: Attendi 5-10 minuti, poi svuota cache DNS:
  ```bash
  # Windows
  ipconfig /flushdns
  
  # Mac/Linux
  sudo dscacheutil -flushcache
  ```

### Certificato SSL non valido
- Problema: Render sta ancora generando certificato
- Soluzione: Attendi 5-10 minuti dopo verifica dominio

---

## Costi

- **Cloudflare Free**: $0/mese (include tutto il necessario)
- **Render Custom Domain**: $0 (incluso anche nel piano Free)
- **SSL Certificate**: $0 (Let's Encrypt automatico)

**Totale: $0/mese** 🎉

---

## Prossimi Passi

Dopo aver configurato il dominio:

1. Aggiorna link in documentazione
2. Configura Google Search Console (SEO)
3. Aggiungi Google Analytics (opzionale)
4. Configura email professionale (es. info@matteozaramella.com con Cloudflare Email Routing)

---

Ultimo aggiornamento: 2025-10-17
