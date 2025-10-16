from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3
import os
from datetime import datetime, timedelta
import json

app = Flask(__name__)
# Production: usa variabile ambiente per secret key, altrimenti genera una casuale
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))
app.config['DATABASE'] = 'piattaforma.db'

# Registra i blueprints dei moduli
from modules.matched_betting import bp as matched_betting_bp
from modules.task_lavoro import bp as task_lavoro_bp
from modules.task_privati import bp as task_privati_bp
from modules.fitness import bp as fitness_bp
from modules.settings import bp as settings_bp

app.register_blueprint(matched_betting_bp)
app.register_blueprint(task_lavoro_bp)
app.register_blueprint(task_privati_bp)
app.register_blueprint(fitness_bp)
app.register_blueprint(settings_bp)

# Password per Dev Tools (solo per Claude/manutenzione)
DEV_TOOLS_PASSWORD = "dev_access_2024"

def get_db():
    """Connessione al database"""
    db = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    return db

def init_db():
    """Inizializza il database con le tabelle"""
    db = get_db()

    # Tabella utenti
    db.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Tabella matched betting
    db.execute('''
        CREATE TABLE IF NOT EXISTS matched_betting (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            bookmaker_back TEXT NOT NULL,
            bookmaker_lay TEXT,
            stake_back REAL,
            stake_lay REAL,
            quota_back REAL,
            quota_lay REAL,
            rating TEXT,
            mercato TEXT,
            offerta TEXT,
            evento TEXT NOT NULL,
            data_evento TIMESTAMP,
            profitto REAL,
            note TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Tabella task lavoro
    db.execute('''
        CREATE TABLE IF NOT EXISTS task_lavoro (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            titolo TEXT NOT NULL,
            descrizione TEXT,
            priorita TEXT DEFAULT 'media',
            stato TEXT DEFAULT 'da_fare',
            deadline TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Tabella task privati
    db.execute('''
        CREATE TABLE IF NOT EXISTS task_privati (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            titolo TEXT NOT NULL,
            descrizione TEXT,
            priorita TEXT DEFAULT 'media',
            stato TEXT DEFAULT 'da_fare',
            deadline TIMESTAMP,
            ricorrente BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Tabella pasti
    db.execute('''
        CREATE TABLE IF NOT EXISTS pasti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            data DATE NOT NULL,
            tipo_pasto TEXT NOT NULL,
            descrizione TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Tabella allenamenti
    db.execute('''
        CREATE TABLE IF NOT EXISTS allenamenti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            data DATE NOT NULL,
            esercizio TEXT NOT NULL,
            ripetizioni INTEGER,
            peso REAL,
            note TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Tabella workout strutturati (nuova per scheda allenamento)
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

    # Tabella preferenze utente
    db.execute('''
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
    db.close()

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

@app.context_processor
def inject_user_preferences():
    """Inietta le preferenze utente in tutti i template"""
    dark_mode = False
    if 'user_id' in session:
        db = get_db()
        prefs = db.execute('SELECT dark_mode FROM user_preferences WHERE user_id = ?',
                          (session['user_id'],)).fetchone()
        if prefs:
            dark_mode = bool(prefs['dark_mode'])
        db.close()
    return dict(dark_mode=dark_mode)

@app.route('/')
def index():
    """Redirect alla dashboard se loggato, altrimenti al login"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Pagina di login"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        db.close()

        if user and check_password_hash(user['password'], password):
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

        db = get_db()

        # Verifica se username esiste già
        existing_user = db.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
        if existing_user:
            flash('Username già esistente', 'error')
            db.close()
            return render_template('register.html')

        # Crea nuovo utente
        hashed_password = generate_password_hash(password)
        db.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
        db.commit()
        db.close()

        flash('Registrazione completata! Effettua il login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    """Logout"""
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principale"""
    db = get_db()
    user_id = session['user_id']

    # Statistiche rapide
    stats = {
        'betting_count': db.execute('SELECT COUNT(*) as cnt FROM matched_betting WHERE user_id = ?', (user_id,)).fetchone()['cnt'],
        'task_lavoro_pending': db.execute('SELECT COUNT(*) as cnt FROM task_lavoro WHERE user_id = ? AND stato != "completato"', (user_id,)).fetchone()['cnt'],
        'task_privati_pending': db.execute('SELECT COUNT(*) as cnt FROM task_privati WHERE user_id = ? AND stato != "completato"', (user_id,)).fetchone()['cnt'],
        'allenamenti_settimana': db.execute('SELECT COUNT(*) as cnt FROM allenamenti WHERE user_id = ? AND data >= date("now", "-7 days")', (user_id,)).fetchone()['cnt']
    }

    db.close()

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

if __name__ == '__main__':
    # Inizializza database se non esiste
    if not os.path.exists(app.config['DATABASE']):
        init_db()

    # In production Render usa gunicorn, quindi questa parte è solo per sviluppo locale
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True') == 'True'
    app.run(debug=debug, host='0.0.0.0', port=port)
