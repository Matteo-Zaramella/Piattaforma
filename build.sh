#!/usr/bin/env bash
# Script di build per Render.com

set -o errexit

# Installa le dipendenze
pip install -r requirements.txt

# Il database SQLite viene creato automaticamente da Flask al primo avvio
# Non serve creare nulla qui
