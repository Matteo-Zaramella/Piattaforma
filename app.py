from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
from datetime import datetime, timedelta
import json
from urllib.parse import urlparse

# Importa driver database appropriati
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

import sqlite3

app = Flask(__name__)
# Production: usa variabile ambiente per secret key, altrimenti genera una casuale
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

# Configurazione timeout sessione: 3 ore (10800 secondi) per workout lunghi
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=3)
app.config['SESSION_REFRESH_EACH_REQUEST'] = True  # Rinfresca il timer ad ogni request

# Configurazione database: usa PostgreSQL se DATABASE_URL è presente, altrimenti SQLite
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    # Render fornisce URL con postgres://, ma psycopg2 richiede postgresql://
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    app.config['DATABASE_URL'] = DATABASE_URL
    app.config['USE_POSTGRES'] = True
else:
    app.config['DATABASE'] = 'piattaforma.db'
    app.config['USE_POSTGRES'] = False

# Registra i blueprints dei moduli
from modules.fitness import bp as fitness_bp
from modules.settings import bp as settings_bp
from modules.wishlist import bp as wishlist_bp
from modules.location import bp as location_bp
from modules.appointments import bp as appointments_bp
from modules.game_prize import bp as game_prize_bp

app.register_blueprint(fitness_bp)
app.register_blueprint(settings_bp)
app.register_blueprint(wishlist_bp)
app.register_blueprint(location_bp)
app.register_blueprint(appointments_bp)
app.register_blueprint(game_prize_bp)

# Password per Dev Tools (solo per Claude/manutenzione)
DEV_TOOLS_PASSWORD = "dev_access_2024"

def get_db():
    """Connessione al database - supporta PostgreSQL e SQLite"""
    if app.config['USE_POSTGRES']:
        if not POSTGRES_AVAILABLE:
            raise RuntimeError("psycopg2 non installato ma DATABASE_URL configurato")
        conn = psycopg2.connect(app.config['DATABASE_URL'])
        return conn
    else:
        conn = sqlite3.connect(app.config['DATABASE'])
        conn.row_factory = sqlite3.Row
        return conn

def dict_factory(cursor, row):
    """Converte righe database in dizionari (per compatibilità)"""
    if app.config['USE_POSTGRES']:
        # PostgreSQL con RealDictCursor già restituisce dizionari
        return row
    else:
        # SQLite: converti Row in dict
        return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

def init_db():
    """Inizializza il database con le tabelle"""
    conn = get_db()
    cursor = conn.cursor()

    # Determina sintassi SQL in base al database
    if app.config['USE_POSTGRES']:
        id_type = "SERIAL PRIMARY KEY"
        text_type = "VARCHAR"
        bool_type = "BOOLEAN"
        timestamp_default = "DEFAULT CURRENT_TIMESTAMP"
    else:
        id_type = "INTEGER PRIMARY KEY AUTOINCREMENT"
        text_type = "TEXT"
        bool_type = "BOOLEAN"
        timestamp_default = "DEFAULT CURRENT_TIMESTAMP"

    # Tabella utenti
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS users (
            id {id_type},
            username {text_type} UNIQUE NOT NULL,
            password {text_type} NOT NULL,
            created_at TIMESTAMP {timestamp_default}
        )
    ''')

    # Tabella matched betting
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS matched_betting (
            id {id_type},
            user_id INTEGER,
            bookmaker_back {text_type} NOT NULL,
            bookmaker_lay {text_type},
            stake_back REAL,
            stake_lay REAL,
            quota_back REAL,
            quota_lay REAL,
            rating {text_type},
            mercato {text_type},
            offerta {text_type},
            evento {text_type} NOT NULL,
            data_evento TIMESTAMP,
            profitto REAL,
            note {text_type},
            created_at TIMESTAMP {timestamp_default},
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Tabella task lavoro
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS task_lavoro (
            id {id_type},
            user_id INTEGER,
            titolo {text_type} NOT NULL,
            descrizione {text_type},
            priorita {text_type} DEFAULT 'media',
            stato {text_type} DEFAULT 'da_fare',
            deadline TIMESTAMP,
            created_at TIMESTAMP {timestamp_default},
            completed_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Tabella task privati
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS task_privati (
            id {id_type},
            user_id INTEGER,
            titolo {text_type} NOT NULL,
            descrizione {text_type},
            priorita {text_type} DEFAULT 'media',
            stato {text_type} DEFAULT 'da_fare',
            deadline TIMESTAMP,
            ricorrente {bool_type} DEFAULT {'FALSE' if app.config['USE_POSTGRES'] else '0'},
            created_at TIMESTAMP {timestamp_default},
            completed_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Tabella pasti
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS pasti (
            id {id_type},
            user_id INTEGER,
            data DATE NOT NULL,
            tipo_pasto {text_type} NOT NULL,
            descrizione {text_type} NOT NULL,
            created_at TIMESTAMP {timestamp_default},
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Tabella allenamenti
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS allenamenti (
            id {id_type},
            user_id INTEGER,
            data DATE NOT NULL,
            esercizio {text_type} NOT NULL,
            ripetizioni INTEGER,
            peso REAL,
            note {text_type},
            created_at TIMESTAMP {timestamp_default},
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Tabella workout strutturati (nuova per scheda allenamento)
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS workout_sessions (
            id {id_type},
            user_id INTEGER,
            data DATE NOT NULL,
            workout_type {text_type} NOT NULL,
            completato {bool_type} DEFAULT {'FALSE' if app.config['USE_POSTGRES'] else '0'},
            created_at TIMESTAMP {timestamp_default},
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Tabella esercizi workout strutturati
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS workout_exercises (
            id {id_type},
            session_id INTEGER,
            esercizio {text_type} NOT NULL,
            serie_numero INTEGER,
            ripetizioni INTEGER,
            peso REAL,
            note {text_type},
            FOREIGN KEY (session_id) REFERENCES workout_sessions (id)
        )
    ''')

    # Tabella preferenze utente
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS user_preferences (
            id {id_type},
            user_id INTEGER UNIQUE NOT NULL,
            dark_mode {bool_type} DEFAULT {'FALSE' if app.config['USE_POSTGRES'] else '0'},
            language {text_type} DEFAULT 'it',
            notifications {bool_type} DEFAULT {'TRUE' if app.config['USE_POSTGRES'] else '1'},
            updated_at TIMESTAMP {timestamp_default},
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Tabella wishlist (Lista di Babbo Natale)
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS wishlist (
            id {id_type},
            user_id INTEGER,
            nome {text_type} NOT NULL,
            descrizione {text_type},
            link {text_type},
            priorita {text_type} DEFAULT 'media',
            pubblico {bool_type} DEFAULT {'TRUE' if app.config['USE_POSTGRES'] else '1'},
            created_at TIMESTAMP {timestamp_default},
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Tabella posizione/dove sono
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS current_location (
            id {id_type},
            user_id INTEGER,
            nome_luogo {text_type} NOT NULL,
            indirizzo {text_type},
            google_maps_link {text_type},
            orario {text_type},
            note {text_type},
            immagine_url {text_type},
            attivo {bool_type} DEFAULT {'TRUE' if app.config['USE_POSTGRES'] else '1'},
            data_inizio TIMESTAMP,
            data_fine TIMESTAMP,
            created_at TIMESTAMP {timestamp_default},
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Tabella appuntamenti/impegni
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS appointments (
            id {id_type},
            user_id INTEGER,
            titolo {text_type} NOT NULL,
            descrizione {text_type},
            data_ora TIMESTAMP NOT NULL,
            luogo {text_type},
            pubblico {bool_type} DEFAULT {'FALSE' if app.config['USE_POSTGRES'] else '0'},
            completato {bool_type} DEFAULT {'FALSE' if app.config['USE_POSTGRES'] else '0'},
            created_at TIMESTAMP {timestamp_default},
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # ============== TABELLE GAME PRIZE ==============

    # Tabella configurazione gioco a premi
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS game_prize_config (
            id {id_type},
            game_name {text_type} DEFAULT 'Premio di Compleanno',
            start_date TIMESTAMP,
            end_date TIMESTAMP,
            total_challenges INTEGER DEFAULT 12,
            max_participants INTEGER DEFAULT 100,
            description {text_type},
            created_at TIMESTAMP {timestamp_default},
            updated_at TIMESTAMP {timestamp_default}
        )
    ''')

    # Tabella sfide del gioco
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS game_challenges (
            id {id_type},
            challenge_number INTEGER NOT NULL,
            title {text_type} NOT NULL,
            description {text_type},
            points INTEGER DEFAULT 100,
            start_date TIMESTAMP,
            end_date TIMESTAMP,
            location {text_type},
            instructions {text_type},
            created_at TIMESTAMP {timestamp_default},
            updated_at TIMESTAMP {timestamp_default}
        )
    ''')

    # Tabella indizi per le sfide
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS game_clues (
            id {id_type},
            challenge_id INTEGER NOT NULL,
            clue_number INTEGER NOT NULL,
            clue_text {text_type} NOT NULL,
            revealed_date TIMESTAMP,
            created_at TIMESTAMP {timestamp_default},
            FOREIGN KEY (challenge_id) REFERENCES game_challenges (id)
        )
    ''')

    # Tabella completamenti sfide da parte degli utenti
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS game_user_completions (
            id {id_type},
            user_id INTEGER NOT NULL,
            challenge_id INTEGER NOT NULL,
            completed_date TIMESTAMP {timestamp_default},
            created_at TIMESTAMP {timestamp_default},
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (challenge_id) REFERENCES game_challenges (id),
            UNIQUE (user_id, challenge_id)
        )
    ''')

    # Tabella punti degli utenti
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS game_user_scores (
            id {id_type},
            user_id INTEGER NOT NULL,
            challenge_id INTEGER NOT NULL,
            points INTEGER NOT NULL,
            awarded_date TIMESTAMP {timestamp_default},
            created_at TIMESTAMP {timestamp_default},
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (challenge_id) REFERENCES game_challenges (id)
        )
    ''')

    # Tabella per tracciare quando è stato rivelato il vincitore
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS game_winner_reveal (
            id {id_type},
            revealed {bool_type} DEFAULT {'FALSE' if app.config['USE_POSTGRES'] else '0'},
            revealed_date TIMESTAMP,
            winner_user_id INTEGER,
            created_at TIMESTAMP {timestamp_default},
            updated_at TIMESTAMP {timestamp_default},
            FOREIGN KEY (winner_user_id) REFERENCES users (id)
        )
    ''')

    conn.commit()
    cursor.close()
    conn.close()

# Inizializza il database all'avvio
# Per PostgreSQL, verifica sempre le tabelle (non c'è file da controllare)
# Per SQLite, crea solo se file non esiste
if app.config['USE_POSTGRES']:
    print("PostgreSQL rilevato, verifico tabelle...")
    try:
        init_db()
        print("Tabelle PostgreSQL verificate/create!")
    except Exception as e:
        print(f"Errore inizializzazione PostgreSQL: {e}")
elif not os.path.exists(app.config['DATABASE']):
    print("Database SQLite non trovato, inizializzazione in corso...")
    init_db()
    print("Database SQLite inizializzato con successo!")

def login_required(f):
    """Decorator per proteggere le route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def dev_tools_required(f):
    """Decorator per proteggere Dev Tools"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'dev_authenticated' not in session:
            return redirect(url_for('dev_login'))
        return f(*args, **kwargs)
    return decorated_function

def execute_query(conn, query, params=None, fetch_one=False, fetch_all=False):
    """Helper per eseguire query con supporto PostgreSQL/SQLite"""
    if app.config['USE_POSTGRES']:
        # PostgreSQL usa %s come placeholder
        query = query.replace('?', '%s')
        cursor = conn.cursor(cursor_factory=RealDictCursor)
    else:
        # SQLite usa ?
        cursor = conn.cursor()

    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)

    if fetch_one:
        result = cursor.fetchone()
        cursor.close()
        return result
    elif fetch_all:
        result = cursor.fetchall()
        cursor.close()
        return result
    else:
        return cursor

@app.context_processor
def inject_game_prize_status():
    """Inietta lo stato del Game Prize in tutti i template"""
    from datetime import datetime
    # Inizio gioco: 25 Gennaio 2026 00:00 (Domenica)
    # Fine gioco: 25 Gennaio 2027 23:59:59 (Lunedì)
    game_reveal_date = datetime(2026, 1, 25, 0, 0, 0)
    game_end_date = datetime(2027, 1, 25, 23, 59, 59)
    now = datetime.now()

    is_game_revealed = now >= game_reveal_date
    is_game_closed = now > game_end_date
    game_admin_authenticated = session.get('game_admin_authenticated', False)

    return dict(
        is_game_prize_revealed=is_game_revealed,
        is_game_prize_closed=is_game_closed,
        game_admin_authenticated=game_admin_authenticated
    )

@app.context_processor
def inject_user_preferences():
    """Inietta le preferenze utente in tutti i template"""
    dark_mode = False
    if 'user_id' in session:
        try:
            conn = get_db()
            prefs = execute_query(conn,
                                 'SELECT dark_mode FROM user_preferences WHERE user_id = ?',
                                 (session['user_id'],),
                                 fetch_one=True)
            if prefs:
                # Converte esplicitamente a boolean (gestisce 0/1 di SQLite)
                dark_mode = bool(int(prefs['dark_mode'])) if prefs['dark_mode'] is not None else False
            conn.close()
        except Exception as e:
            print(f"Errore caricamento preferenze: {e}")
    return dict(dark_mode=dark_mode)

@app.route('/')
def index():
    """Home page pubblica con wishlist, posizione e appuntamenti"""
    conn = get_db()
    try:
        # Carica wishlist pubblica
        wishlist_items = execute_query(conn, '''
            SELECT nome, descrizione, link, priorita
            FROM wishlist
            WHERE pubblico = ?
            ORDER BY
                CASE priorita
                    WHEN 'alta' THEN 1
                    WHEN 'media' THEN 2
                    ELSE 3
                END,
                created_at DESC
        ''', (True if app.config['USE_POSTGRES'] else 1,), fetch_all=True)

        # Carica posizione attiva
        if app.config['USE_POSTGRES']:
            time_check = "CURRENT_TIMESTAMP BETWEEN data_inizio AND data_fine"
        else:
            time_check = "datetime('now') BETWEEN datetime(data_inizio) AND datetime(data_fine)"

        current_location = execute_query(conn, f'''
            SELECT nome_luogo, indirizzo, google_maps_link, orario, note, immagine_url
            FROM current_location
            WHERE attivo = ? AND ({time_check} OR data_fine IS NULL)
            ORDER BY created_at DESC
            LIMIT 1
        ''', (True if app.config['USE_POSTGRES'] else 1,), fetch_one=True)

        # Carica prossimi appuntamenti pubblici
        if app.config['USE_POSTGRES']:
            future_check = "data_ora >= CURRENT_TIMESTAMP"
        else:
            future_check = "datetime(data_ora) >= datetime('now')"

        appointments = execute_query(conn, f'''
            SELECT titolo, descrizione, data_ora, luogo
            FROM appointments
            WHERE pubblico = ? AND {future_check} AND completato = ?
            ORDER BY data_ora ASC
            LIMIT 5
        ''', (True if app.config['USE_POSTGRES'] else 1, False if app.config['USE_POSTGRES'] else 0), fetch_all=True)

        # Carica sfide del Game Prize (solo sfide in corso e passate, non future)
        game_challenges = []
        if app.config['USE_POSTGRES']:
            challenges_check = "start_date <= CURRENT_TIMESTAMP"  # Sfide già iniziate
        else:
            challenges_check = "datetime(start_date) <= datetime('now')"

        game_challenges = execute_query(conn, f'''
            SELECT id, challenge_number, title, description, start_date, end_date
            FROM game_challenges
            WHERE {challenges_check}
            ORDER BY challenge_number ASC
            LIMIT 5
        ''', fetch_all=True)

    except Exception as e:
        print(f"Errore caricamento home: {e}")
        wishlist_items = []
        current_location = None
        appointments = []
        game_challenges = []
    finally:
        conn.close()

    return render_template('home.html',
                         wishlist_items=wishlist_items,
                         current_location=current_location,
                         appointments=appointments,
                         game_challenges=game_challenges)

@app.route('/game-prize-reveal')
def game_prize_reveal():
    """Pagina pubblica con countdown per Game Prize - Visibile a tutti"""
    return render_template('game_prize_countdown.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Pagina di login"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        user = execute_query(conn, 'SELECT * FROM users WHERE username = ?',
                           (username,), fetch_one=True)
        conn.close()

        if user and check_password_hash(user['password'], password):
            session.permanent = True  # Attiva la sessione permanente con timeout di 1 ora
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        else:
            flash('Username o password errati', 'error')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Pagina di registrazione"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db()

        # Verifica se username esiste già
        existing_user = execute_query(conn, 'SELECT id FROM users WHERE username = ?',
                                     (username,), fetch_one=True)
        if existing_user:
            flash('Username già esistente', 'error')
            conn.close()
            return render_template('register.html')

        # Crea nuovo utente
        hashed_password = generate_password_hash(password)
        cursor = execute_query(conn, 'INSERT INTO users (username, password) VALUES (?, ?)',
                              (username, hashed_password))
        conn.commit()
        cursor.close()
        conn.close()

        flash('Registrazione completata! Effettua il login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    """Logout"""
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principale"""
    conn = get_db()
    user_id = session['user_id']

    try:
        # Query compatibile con PostgreSQL e SQLite per data recente
        if app.config['USE_POSTGRES']:
            date_query = "data >= CURRENT_DATE - INTERVAL '7 days'"
        else:
            date_query = 'data >= date("now", "-7 days")'

        # Statistiche rapide (solo fitness)
        if app.config['USE_POSTGRES']:
            today_query = "data = CURRENT_DATE"
        else:
            today_query = 'data = date("now")'

        try:
            allenamenti_result = execute_query(conn,
                                              f'SELECT COUNT(*) as cnt FROM allenamenti WHERE user_id = ? AND {date_query}',
                                              (user_id,), fetch_one=True)
            allenamenti_count = allenamenti_result['cnt'] if allenamenti_result else 0
        except Exception as e:
            print(f"Errore query allenamenti: {e}")
            allenamenti_count = 0

        try:
            pasti_result = execute_query(conn,
                                       f'SELECT COUNT(*) as cnt FROM pasti WHERE user_id = ? AND {today_query}',
                                       (user_id,), fetch_one=True)
            pasti_count = pasti_result['cnt'] if pasti_result else 0
        except Exception as e:
            print(f"Errore query pasti: {e}")
            pasti_count = 0

        stats = {
            'allenamenti_settimana': allenamenti_count,
            'pasti_oggi': pasti_count
        }

    except Exception as e:
        print(f"Errore generale dashboard: {e}")
        stats = {
            'allenamenti_settimana': 0,
            'pasti_oggi': 0
        }
    finally:
        conn.close()

    return render_template('dashboard.html', stats=stats)

@app.route('/dev-login', methods=['GET', 'POST'])
@login_required
def dev_login():
    """Login per Dev Tools"""
    if request.method == 'POST':
        password = request.form['password']
        if password == DEV_TOOLS_PASSWORD:
            session['dev_authenticated'] = True
            return redirect(url_for('dev_tools'))
        else:
            flash('Password errata', 'error')

    return render_template('dev_login.html')

@app.route('/dev-tools')
@login_required
@dev_tools_required
def dev_tools():
    """Pagina Dev Tools"""
    # Lista tutti i file del progetto
    project_files = []
    base_path = os.path.dirname(os.path.abspath(__file__))

    for root, dirs, files in os.walk(base_path):
        # Esclude __pycache__ e .git
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'venv']]
        for file in files:
            if file.endswith(('.py', '.html', '.css', '.js', '.json')):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, base_path)
                project_files.append(rel_path)

    return render_template('dev_tools.html', files=project_files)

@app.route('/dev-tools/view-file')
@login_required
@dev_tools_required
def view_file():
    """Visualizza contenuto di un file"""
    file_path = request.args.get('file')
    base_path = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_path, file_path)

    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return jsonify({'success': True, 'content': content, 'file': file_path})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/dev-tools/save-file', methods=['POST'])
@login_required
@dev_tools_required
def save_file():
    """Salva modifiche a un file"""
    data = request.json
    file_path = data.get('file')
    content = data.get('content')

    base_path = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_path, file_path)

    try:
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/verify-game-password', methods=['POST'])
def verify_game_password():
    """Verifica la password del Game Prize e imposta la sessione"""
    password = request.form.get('game_password', '').strip()
    print(f"[DEBUG] Password ricevuta: '{password}' (lunghezza: {len(password)})")
    print(f"[DEBUG] Confronto con: 'The Game' (lunghezza: {len('The Game')})")

    # Password corretta: "The Game"
    if password == "The Game":
        session['game_admin_authenticated'] = True
        session.modified = True  # Forza il salvataggio della sessione
        print(f"[DEBUG] Password corretta! Sessione impostata.")
        flash('Accesso concesso al Game Prize!', 'success')
        return redirect(url_for('game_prize.admin_welcome'))
    else:
        print(f"[DEBUG] Password non corretta!")
        flash('Password non corretta. Riprova.', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/logout-game-admin')
def logout_game_admin():
    """Disconnette l'admin dal Game Prize"""
    if 'game_admin_authenticated' in session:
        del session['game_admin_authenticated']
    flash('Sei stato disconnesso dal Game Prize.', 'info')
    return redirect(url_for('index'))

@app.route('/api/ping')
@login_required
def api_ping():
    """Endpoint per keep-alive della sessione - risponde solo se l'utente è loggato"""
    return jsonify({
        'status': 'ok',
        'message': 'Session alive',
        'user': session.get('username')
    }), 200

@app.errorhandler(500)
def handle_500_error(error):
    """Gestisce errori interni del server"""
    print(f"Errore 500: {error}")
    return render_template('error.html', error_code=500, error_message="Si è verificato un errore interno del server. Riprova più tardi."), 500

@app.errorhandler(404)
def handle_404_error(error):
    """Gestisce pagine non trovate"""
    return render_template('error.html', error_code=404, error_message="Pagina non trovata."), 404

@app.route('/init-database-tables')
@login_required
def init_database_tables():
    """Endpoint per inizializzare tabelle database (protetto da login)"""
    try:
        init_db()
        flash('Database inizializzato con successo!', 'success')
        return redirect(url_for('dashboard'))
    except Exception as e:
        flash(f'Errore inizializzazione database: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

if __name__ == '__main__':
    # Inizializza database se non esiste (o verifica tabelle PostgreSQL)
    if app.config['USE_POSTGRES']:
        try:
            init_db()
        except Exception as e:
            print(f"Errore inizializzazione PostgreSQL: {e}")
    elif not os.path.exists(app.config['DATABASE']):
        init_db()

    # In production Render usa gunicorn, quindi questa parte è solo per sviluppo locale
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True') == 'True'
    app.run(debug=debug, host='0.0.0.0', port=port)
