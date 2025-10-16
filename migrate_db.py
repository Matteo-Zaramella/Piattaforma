"""
Script per aggiungere le nuove tabelle workout al database esistente
"""
import sqlite3

def migrate_database():
    """Aggiunge le tabelle workout_sessions e workout_exercises"""
    db = sqlite3.connect('piattaforma.db')

    try:
        # Controlla se le tabelle esistono già
        cursor = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='workout_sessions'")
        if cursor.fetchone():
            print("✓ Le tabelle workout esistono già!")
            db.close()
            return

        print("Creazione nuove tabelle workout...")

        # Tabella workout strutturati
        db.execute('''
            CREATE TABLE IF NOT EXISTS workout_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                data DATE NOT NULL,
                workout_type TEXT NOT NULL,
                completato BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        # Tabella esercizi workout strutturati
        db.execute('''
            CREATE TABLE IF NOT EXISTS workout_exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                esercizio TEXT NOT NULL,
                serie_numero INTEGER,
                ripetizioni INTEGER,
                peso REAL,
                note TEXT,
                FOREIGN KEY (session_id) REFERENCES workout_sessions (id)
            )
        ''')

        db.commit()
        print("✓ Tabelle create con successo!")
        print("✓ Migrazione completata!")

    except Exception as e:
        print(f"✗ Errore durante la migrazione: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == '__main__':
    print("=== Migrazione Database - Scheda Workout ===")
    migrate_database()
    print("\nPuoi ora riavviare l'applicazione.")
