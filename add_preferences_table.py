"""
Script per aggiungere la tabella user_preferences al database esistente
Esegui questo script per aggiungere le impostazioni senza perdere i dati esistenti
"""

import sqlite3

def add_preferences_table():
    """Aggiunge la tabella user_preferences se non esiste"""
    db = sqlite3.connect('piattaforma.db')
    cursor = db.cursor()

    # Crea la tabella user_preferences
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            dark_mode BOOLEAN DEFAULT 0,
            language TEXT DEFAULT 'it',
            notifications BOOLEAN DEFAULT 1,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    db.commit()
    print("[OK] Tabella user_preferences creata con successo!")

    # Verifica quanti utenti esistono
    cursor.execute('SELECT COUNT(*) as cnt FROM users')
    user_count = cursor.fetchone()[0]
    print(f"[OK] Trovati {user_count} utenti nel database")

    # Crea preferenze di default per tutti gli utenti esistenti che non le hanno
    cursor.execute('''
        INSERT OR IGNORE INTO user_preferences (user_id, dark_mode, language, notifications)
        SELECT id, 0, 'it', 1
        FROM users
        WHERE id NOT IN (SELECT user_id FROM user_preferences)
    ''')

    rows_added = cursor.rowcount
    db.commit()
    print(f"[OK] Aggiunte preferenze di default per {rows_added} utenti")

    db.close()
    print("\n[OK] Aggiornamento database completato con successo!")
    print("Ora puoi avviare l'applicazione con: python app.py")

if __name__ == '__main__':
    try:
        add_preferences_table()
    except Exception as e:
        print(f"[ERRORE] Errore durante l'aggiornamento: {e}")
