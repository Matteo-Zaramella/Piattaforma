#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Popola il database con le 13 sfide del Game Prize 2026-2027
Date verificate: tutte sabato tranne la finale (domenica)
"""
import sqlite3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def populate_challenges():
    """Popola le 13 sfide con date corrette"""

    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'piattaforma.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("=== POPOLAMENTO SFIDE GAME PRIZE ===\n")

    # Date verificate (tutte sabato tranne la finale)
    challenges = [
        {
            'number': 1,
            'title': 'Sfida 1 - Gennaio',
            'date': '2026-01-24',  # Sabato
            'description': 'Prima sfida del gioco',
            'points': 500,
            'location': 'Da definire',
            'instructions': 'Le istruzioni verranno rivelate il giorno della sfida'
        },
        {
            'number': 2,
            'title': 'Sfida 2 - Febbraio',
            'date': '2026-02-21',  # Sabato
            'description': 'Seconda sfida del gioco',
            'points': 500,
            'location': 'Da definire',
            'instructions': 'Le istruzioni verranno rivelate il giorno della sfida'
        },
        {
            'number': 3,
            'title': 'Sfida 3 - Marzo',
            'date': '2026-03-21',  # Sabato
            'description': 'Terza sfida del gioco',
            'points': 500,
            'location': 'Da definire',
            'instructions': 'Le istruzioni verranno rivelate il giorno della sfida'
        },
        {
            'number': 4,
            'title': 'Sfida 4 - Aprile',
            'date': '2026-04-25',  # Sabato
            'description': 'Quarta sfida del gioco',
            'points': 500,
            'location': 'Da definire',
            'instructions': 'Le istruzioni verranno rivelate il giorno della sfida'
        },
        {
            'number': 5,
            'title': 'Sfida 5 - Maggio',
            'date': '2026-05-23',  # Sabato
            'description': 'Quinta sfida del gioco',
            'points': 500,
            'location': 'Da definire',
            'instructions': 'Le istruzioni verranno rivelate il giorno della sfida'
        },
        {
            'number': 6,
            'title': 'Sfida 6 - Giugno',
            'date': '2026-06-27',  # Sabato
            'description': 'Sesta sfida del gioco',
            'points': 500,
            'location': 'Da definire',
            'instructions': 'Le istruzioni verranno rivelate il giorno della sfida'
        },
        {
            'number': 7,
            'title': 'Sfida 7 - Luglio',
            'date': '2026-07-25',  # Sabato
            'description': 'Settima sfida del gioco',
            'points': 500,
            'location': 'Da definire',
            'instructions': 'Le istruzioni verranno rivelate il giorno della sfida'
        },
        {
            'number': 8,
            'title': 'Sfida 8 - Agosto',
            'date': '2026-08-22',  # Sabato
            'description': 'Ottava sfida del gioco',
            'points': 500,
            'location': 'Da definire',
            'instructions': 'Le istruzioni verranno rivelate il giorno della sfida'
        },
        {
            'number': 9,
            'title': 'Sfida 9 - Settembre',
            'date': '2026-09-26',  # Sabato
            'description': 'Nona sfida del gioco',
            'points': 500,
            'location': 'Da definire',
            'instructions': 'Le istruzioni verranno rivelate il giorno della sfida'
        },
        {
            'number': 10,
            'title': 'Sfida 10 - Ottobre',
            'date': '2026-10-24',  # Sabato
            'description': 'Decima sfida del gioco',
            'points': 500,
            'location': 'Da definire',
            'instructions': 'Le istruzioni verranno rivelate il giorno della sfida'
        },
        {
            'number': 11,
            'title': 'Sfida 11 - Novembre',
            'date': '2026-11-21',  # Sabato
            'description': 'Undicesima sfida del gioco',
            'points': 500,
            'location': 'Da definire',
            'instructions': 'Le istruzioni verranno rivelate il giorno della sfida'
        },
        {
            'number': 12,
            'title': 'Sfida 12 - Dicembre',
            'date': '2026-12-26',  # Sabato
            'description': 'Dodicesima sfida del gioco',
            'points': 500,
            'location': 'Da definire',
            'instructions': 'Le istruzioni verranno rivelate il giorno della sfida'
        },
        {
            'number': 13,
            'title': 'SFIDA FINALE - Gennaio 2027',
            'date': '2027-01-24',  # Domenica (FINALE)
            'description': 'La sfida finale che determinerà il vincitore!',
            'points': 1000,
            'location': 'Da definire',
            'instructions': 'Le istruzioni verranno rivelate il giorno della sfida finale'
        }
    ]

    # Verifica giorni della settimana
    from datetime import datetime
    print("Verifica date:")
    for ch in challenges:
        dt = datetime.strptime(ch['date'], '%Y-%m-%d')
        day_name = dt.strftime('%A')
        day_name_it = {
            'Monday': 'Lunedì', 'Tuesday': 'Martedì', 'Wednesday': 'Mercoledì',
            'Thursday': 'Giovedì', 'Friday': 'Venerdì', 'Saturday': 'Sabato', 'Sunday': 'Domenica'
        }[day_name]
        print(f"  Sfida {ch['number']:2d}: {ch['date']} ({day_name_it})")

    print("\nInserimento nel database...")

    for challenge in challenges:
        try:
            # Verifica se esiste già
            cursor.execute('SELECT id FROM game_challenges WHERE challenge_number = ?', (challenge['number'],))
            existing = cursor.fetchone()

            # end_date è lo stesso giorno alle 23:59
            end_date = f"{challenge['date']} 23:59:59"

            if existing:
                # Aggiorna
                cursor.execute('''
                    UPDATE game_challenges
                    SET title = ?,
                        description = ?,
                        points = ?,
                        start_date = ?,
                        end_date = ?,
                        location = ?,
                        instructions = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE challenge_number = ?
                ''', (
                    challenge['title'],
                    challenge['description'],
                    challenge['points'],
                    challenge['date'],
                    end_date,
                    challenge['location'],
                    challenge['instructions'],
                    challenge['number']
                ))
                print(f"  [OK] Sfida {challenge['number']} aggiornata: {challenge['title']}")
            else:
                # Inserisci
                cursor.execute('''
                    INSERT INTO game_challenges
                    (challenge_number, title, description, points, start_date, end_date, location, instructions)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    challenge['number'],
                    challenge['title'],
                    challenge['description'],
                    challenge['points'],
                    challenge['date'],
                    end_date,
                    challenge['location'],
                    challenge['instructions']
                ))
                print(f"  [OK] Sfida {challenge['number']} creata: {challenge['title']}")

        except Exception as e:
            print(f"  [ERR] Errore sfida {challenge['number']}: {e}")

    # Inserisci configurazione generale del gioco
    print("\nConfigurazione gioco...")
    try:
        cursor.execute('SELECT id FROM game_prize_config WHERE id = 1')
        if cursor.fetchone():
            cursor.execute('''
                UPDATE game_prize_config
                SET game_name = 'Game Prize 2026-2027',
                    start_date = '2026-01-24',
                    end_date = '2027-01-24',
                    total_challenges = 13,
                    max_participants = 100,
                    description = 'Gioco a premi con 13 sfide mensili. Le sfide sono disponibili dalle 00:00 alle 23:59 del giorno indicato.',
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = 1
            ''')
            print("  [OK] Configurazione aggiornata")
        else:
            cursor.execute('''
                INSERT INTO game_prize_config
                (id, game_name, start_date, end_date, total_challenges, max_participants, description)
                VALUES (1, 'Game Prize 2026-2027', '2026-01-24', '2027-01-24', 13, 100,
                        'Gioco a premi con 13 sfide mensili. Le sfide sono disponibili dalle 00:00 alle 23:59 del giorno indicato.')
            ''')
            print("  [OK] Configurazione creata")
    except Exception as e:
        print(f"  [ERR] Errore configurazione: {e}")

    conn.commit()
    conn.close()

    print("\n=== POPOLAMENTO COMPLETATO ===")
    print("\nProssimi passi:")
    print("1. Aggiungere indizi per ogni sfida tramite admin dashboard")
    print("2. Configurare le soluzioni degli indizi (parole da indovinare)")
    print("3. Testare il flusso completo di registrazione e validazione")

if __name__ == '__main__':
    populate_challenges()
