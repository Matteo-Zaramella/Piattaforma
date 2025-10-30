#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Applica migration Game Prize V2.0 al database PostgreSQL Render
"""
import os
import sys

def apply_migration():
    """Applica la migration al database PostgreSQL di Render"""

    # Verifica che DATABASE_URL sia impostata
    database_url = os.getenv('DATABASE_URL')

    if not database_url:
        print("❌ ERRORE: Variabile DATABASE_URL non impostata")
        print("\nPer applicare la migration su Render:")
        print("1. Vai su https://dashboard.render.com/d/dpg-d3ogka1r0fns73c7230g-a")
        print("2. Copia la 'External Database URL'")
        print("3. Esegui:")
        print("   set DATABASE_URL=[la-url-copiata]")
        print("   python migrations/apply_to_render.py")
        print("\nOppure esegui direttamente con psql:")
        print("   psql [DATABASE_URL] -f migrations/apply_production_fixes.sql")
        sys.exit(1)

    try:
        import psycopg2
    except ImportError:
        print("❌ ERRORE: psycopg2 non installato")
        print("\nInstalla con:")
        print("   pip install psycopg2-binary")
        sys.exit(1)

    print("🔗 Connessione al database PostgreSQL Render...")

    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()

        print("✅ Connesso!")
        print("\n📄 Leggendo file SQL migration...")

        # Leggi il file SQL
        script_dir = os.path.dirname(os.path.abspath(__file__))
        sql_file = os.path.join(script_dir, 'apply_production_fixes.sql')

        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        print("✅ File SQL caricato")
        print("\n🚀 Esecuzione migration...")
        print("-" * 60)

        # Esegui lo script SQL
        cursor.execute(sql_content)
        conn.commit()

        print("-" * 60)
        print("✅ Migration completata con successo!")

        # Verifica risultati
        print("\n🔍 Verifica risultati:")

        # Conta tabelle create
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name LIKE 'game_%'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        print(f"   ✅ Tabelle Game Prize create: {len(tables)}")
        for table in tables:
            print(f"      - {table[0]}")

        # Conta partecipanti
        cursor.execute("SELECT COUNT(*) FROM game_participants")
        count = cursor.fetchone()[0]
        print(f"\n   ✅ Codici univoci generati: {count}")

        # Conta sfide
        cursor.execute("SELECT COUNT(*) FROM game_challenges")
        count = cursor.fetchone()[0]
        print(f"   ✅ Sfide create: {count}")

        # Verifica date sfide
        cursor.execute("""
            SELECT challenge_number,
                   TO_CHAR(start_date, 'DD/MM/YYYY') as data,
                   TO_CHAR(start_date, 'Day') as giorno
            FROM game_challenges
            ORDER BY challenge_number
        """)
        sfide = cursor.fetchall()
        print(f"\n   📅 Date sfide:")
        for sfida in sfide:
            print(f"      Sfida {sfida[0]:2d}: {sfida[1]} ({sfida[2].strip()})")

        cursor.close()
        conn.close()

        print("\n" + "=" * 60)
        print("🎉 MIGRATION COMPLETATA CON SUCCESSO!")
        print("=" * 60)
        print("\nTutto pronto! Il sistema Game Prize V2.0 è attivo.")

    except Exception as e:
        print(f"\n❌ ERRORE durante la migration:")
        print(f"   {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    apply_migration()
