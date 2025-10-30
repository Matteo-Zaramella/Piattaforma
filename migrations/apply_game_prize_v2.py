#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Applica migration Game Prize V2.0 al database SQLite locale
"""
import sqlite3
import sys
import os

# Aggiungi il path del progetto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def apply_migration():
    """Applica la migration al database SQLite"""

    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'piattaforma.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("=== GAME PRIZE V2.0 MIGRATION ===\n")

    # 1. Tabella partecipanti con codici univoci
    print("1. Creando tabella game_participants...")
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_participants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                unique_code TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE,
                nome TEXT,
                cognome TEXT,
                user_id INTEGER,
                registered_at TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                is_active INTEGER DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        print("   OK - Tabella game_participants creata")
    except Exception as e:
        print(f"   Errore: {e}")

    # 2. Tabella soluzioni indizi
    print("\n2. Creando tabella game_clue_solutions...")
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_clue_solutions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                clue_id INTEGER,
                solution_word TEXT NOT NULL,
                points_base INTEGER DEFAULT 50,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (clue_id) REFERENCES game_clues(id) ON DELETE CASCADE
            )
        ''')
        print("   OK - Tabella game_clue_solutions creata")
    except Exception as e:
        print(f"   Errore: {e}")

    # 3. Tabella completamenti indizi
    print("\n3. Creando tabella game_clue_completions...")
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_clue_completions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                clue_id INTEGER,
                participant_id INTEGER,
                completed_at TEXT DEFAULT CURRENT_TIMESTAMP,
                position INTEGER NOT NULL,
                points_earned INTEGER NOT NULL,
                submitted_word TEXT,
                FOREIGN KEY (clue_id) REFERENCES game_clues(id) ON DELETE CASCADE,
                FOREIGN KEY (participant_id) REFERENCES game_participants(id) ON DELETE CASCADE,
                UNIQUE(clue_id, participant_id)
            )
        ''')
        print("   OK - Tabella game_clue_completions creata")
    except Exception as e:
        print(f"   Errore: {e}")

    # 4. Crea tabelle legacy se non esistono
    print("\n4. Creando tabelle legacy (retrocompatibilità)...")

    # game_user_completions (sfide completate dagli utenti)
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_user_completions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                challenge_id INTEGER,
                completed_date TEXT DEFAULT CURRENT_TIMESTAMP,
                position INTEGER,
                points_earned INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (challenge_id) REFERENCES game_challenges(id) ON DELETE CASCADE,
                UNIQUE(user_id, challenge_id)
            )
        ''')
        print("   OK - Tabella game_user_completions creata")
    except Exception as e:
        print(f"   Errore: {e}")

    # game_challenges (definizione sfide)
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_challenges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                challenge_number INTEGER UNIQUE NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                points INTEGER DEFAULT 100,
                start_date TEXT,
                end_date TEXT,
                location TEXT,
                instructions TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("   OK - Tabella game_challenges creata")
    except Exception as e:
        print(f"   Errore: {e}")

    # game_clues (indizi per sfide)
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_clues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                challenge_id INTEGER,
                clue_number INTEGER NOT NULL,
                clue_text TEXT,
                revealed_date TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (challenge_id) REFERENCES game_challenges(id) ON DELETE CASCADE
            )
        ''')
        print("   OK - Tabella game_clues creata")
    except Exception as e:
        print(f"   Errore: {e}")

    # game_user_scores (punteggi utenti - legacy)
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_user_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                challenge_id INTEGER,
                points INTEGER DEFAULT 0,
                awarded_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (challenge_id) REFERENCES game_challenges(id) ON DELETE CASCADE
            )
        ''')
        print("   OK - Tabella game_user_scores creata")
    except Exception as e:
        print(f"   Errore: {e}")

    # game_prize_config (configurazione generale gioco)
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_prize_config (
                id INTEGER PRIMARY KEY,
                game_name TEXT DEFAULT 'Premio di Compleanno',
                start_date TEXT,
                end_date TEXT,
                total_challenges INTEGER DEFAULT 12,
                max_participants INTEGER DEFAULT 100,
                description TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("   OK - Tabella game_prize_config creata")
    except Exception as e:
        print(f"   Errore: {e}")

    # 5. Tabella punteggi dettagliati
    print("\n5. Creando tabella game_detailed_scores...")
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_detailed_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                participant_id INTEGER,
                points_from_clues INTEGER DEFAULT 0,
                points_from_challenges INTEGER DEFAULT 0,
                total_points INTEGER DEFAULT 0,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (participant_id) REFERENCES game_participants(id) ON DELETE CASCADE
            )
        ''')
        print("   OK - Tabella game_detailed_scores creata")
    except Exception as e:
        print(f"   Errore: {e}")

    # 6. Tabella log tentativi
    print("\n6. Creando tabella game_attempt_logs...")
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_attempt_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                participant_id INTEGER,
                clue_id INTEGER,
                challenge_id INTEGER,
                attempted_word TEXT,
                is_correct INTEGER DEFAULT 0,
                attempted_at TEXT DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT,
                FOREIGN KEY (participant_id) REFERENCES game_participants(id) ON DELETE CASCADE,
                FOREIGN KEY (clue_id) REFERENCES game_clues(id) ON DELETE CASCADE,
                FOREIGN KEY (challenge_id) REFERENCES game_challenges(id) ON DELETE CASCADE
            )
        ''')
        print("   OK - Tabella game_attempt_logs creata")
    except Exception as e:
        print(f"   Errore: {e}")

    # 7. Indici
    print("\n7. Creando indici...")
    indices = [
        ('idx_clue_completions_clue', 'game_clue_completions', 'clue_id'),
        ('idx_clue_completions_participant', 'game_clue_completions', 'participant_id'),
        ('idx_clue_completions_position', 'game_clue_completions', 'position'),
        ('idx_user_completions_position', 'game_user_completions', 'position'),
        ('idx_attempt_logs_participant', 'game_attempt_logs', 'participant_id'),
    ]

    for idx_name, table, column in indices:
        try:
            cursor.execute(f'CREATE INDEX IF NOT EXISTS {idx_name} ON {table}({column})')
            print(f"   OK - Indice {idx_name} creato")
        except Exception as e:
            print(f"   Info: {e}")

    # 8. Pre-generazione 100 codici univoci
    print("\n8. Generando 100 codici univoci GP2026-XXXX...")
    try:
        for i in range(1, 101):
            code = f"GP2026-{i:04d}"
            cursor.execute('''
                INSERT OR IGNORE INTO game_participants (unique_code) VALUES (?)
            ''', (code,))

        # Conta quanti ne sono stati inseriti
        cursor.execute('SELECT COUNT(*) FROM game_participants')
        count = cursor.fetchone()[0]
        print(f"   OK - {count} codici univoci generati")
    except Exception as e:
        print(f"   Errore: {e}")

    # Commit e chiudi
    conn.commit()
    conn.close()

    print("\n=== MIGRATION COMPLETATA ===")
    print("\nProssimi passi:")
    print("1. Implementare endpoint /api/validate-clue")
    print("2. Implementare endpoint /api/register-participant")
    print("3. Creare interfacce admin")
    print("4. Aggiornare date sfide")

if __name__ == '__main__':
    apply_migration()
