from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
from functools import wraps
from db_utils import get_db, execute_query

bp = Blueprint('settings', __name__, url_prefix='/settings')

def login_required(f):
    """Decorator per proteggere le route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_user_preferences(user_id):
    """Ottieni le preferenze dell'utente"""
    conn = get_db()
    prefs = execute_query(conn, 'SELECT * FROM user_preferences WHERE user_id = ?', (user_id,), fetch_one=True)

    # Se non esistono preferenze, creale con valori di default
    if not prefs:
        execute_query(conn, '''
            INSERT INTO user_preferences (user_id, dark_mode, language, notifications)
            VALUES (?, 0, 'it', 1)
        ''', (user_id,))
        prefs = execute_query(conn, 'SELECT * FROM user_preferences WHERE user_id = ?', (user_id,), fetch_one=True)

    conn.close()
    return prefs

@bp.route('/')
@login_required
def index():
    """Pagina impostazioni"""
    user_id = session['user_id']
    prefs = get_user_preferences(user_id)

    return render_template('settings.html', preferences=prefs)

@bp.route('/update', methods=['POST'])
@login_required
def update():
    """Aggiorna le preferenze"""
    user_id = session['user_id']

    # Ottieni i dati dal form
    dark_mode = 1 if request.form.get('dark_mode') == 'on' else 0
    language = request.form.get('language', 'it')
    notifications = 1 if request.form.get('notifications') == 'on' else 0

    conn = get_db()
    execute_query(conn, '''
        UPDATE user_preferences
        SET dark_mode = ?, language = ?, notifications = ?, updated_at = CURRENT_TIMESTAMP
        WHERE user_id = ?
    ''', (dark_mode, language, notifications, user_id))
    conn.close()

    flash('Impostazioni salvate con successo!', 'success')
    return redirect(url_for('settings.index'))

@bp.route('/toggle-dark-mode', methods=['POST'])
@login_required
def toggle_dark_mode():
    """Toggle rapido della modalità scura (AJAX)"""
    user_id = session['user_id']

    conn = get_db()
    current = execute_query(conn, 'SELECT dark_mode FROM user_preferences WHERE user_id = ?', (user_id,), fetch_one=True)

    new_value = 0 if current['dark_mode'] else 1

    execute_query(conn, '''
        UPDATE user_preferences
        SET dark_mode = ?, updated_at = CURRENT_TIMESTAMP
        WHERE user_id = ?
    ''', (new_value, user_id))
    conn.close()

    return jsonify({'success': True, 'dark_mode': new_value})

@bp.route('/get-preferences')
@login_required
def get_preferences():
    """API per ottenere le preferenze (usato da JavaScript)"""
    user_id = session['user_id']
    prefs = get_user_preferences(user_id)

    return jsonify({
        'dark_mode': bool(prefs['dark_mode']),
        'language': prefs['language'],
        'notifications': bool(prefs['notifications'])
    })
