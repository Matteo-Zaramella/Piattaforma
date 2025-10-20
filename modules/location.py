from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from functools import wraps
import sys
import os

# Importa funzioni database dal parent
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db_utils import get_db, execute_query

bp = Blueprint('location', __name__, url_prefix='/location')

def login_required(f):
    """Decorator per proteggere le route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/')
@login_required
def index():
    """Visualizza e gestisci la posizione attuale"""
    conn = get_db()
    user_id = session['user_id']

    # Carica posizione attiva
    locations = execute_query(conn, '''
        SELECT id, nome_luogo, indirizzo, google_maps_link, orario, note,
               immagine_url, attivo, data_inizio, data_fine, created_at
        FROM current_location
        WHERE user_id = ?
        ORDER BY created_at DESC
    ''', (user_id,), fetch_all=True)

    conn.close()
    return render_template('location/index.html', locations=locations)

@bp.route('/set', methods=['GET', 'POST'])
@login_required
def set_location():
    """Imposta nuova posizione"""
    if request.method == 'POST':
        nome_luogo = request.form['nome_luogo']
        indirizzo = request.form.get('indirizzo', '')
        google_maps_link = request.form.get('google_maps_link', '')
        orario = request.form.get('orario', '')
        note = request.form.get('note', '')
        immagine_url = request.form.get('immagine_url', '')
        data_inizio = request.form.get('data_inizio')
        data_fine = request.form.get('data_fine')

        conn = get_db()
        user_id = session['user_id']

        # Disattiva tutte le posizioni precedenti
        cursor1 = execute_query(conn, '''
            UPDATE current_location
            SET attivo = ?
            WHERE user_id = ?
        ''', (False, user_id))
        conn.commit()
        cursor1.close()

        # Inserisci nuova posizione attiva
        cursor2 = execute_query(conn, '''
            INSERT INTO current_location
            (user_id, nome_luogo, indirizzo, google_maps_link, orario, note,
             immagine_url, attivo, data_inizio, data_fine)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, nome_luogo, indirizzo, google_maps_link, orario, note,
              immagine_url, True, data_inizio if data_inizio else None,
              data_fine if data_fine else None))

        conn.commit()
        cursor2.close()
        conn.close()

        flash('Posizione impostata con successo!', 'success')
        return redirect(url_for('location.index'))

    return render_template('location/set_location.html')

@bp.route('/edit/<int:location_id>', methods=['GET', 'POST'])
@login_required
def edit_location(location_id):
    """Modifica posizione esistente"""
    conn = get_db()
    user_id = session['user_id']

    if request.method == 'POST':
        nome_luogo = request.form['nome_luogo']
        indirizzo = request.form.get('indirizzo', '')
        google_maps_link = request.form.get('google_maps_link', '')
        orario = request.form.get('orario', '')
        note = request.form.get('note', '')
        immagine_url = request.form.get('immagine_url', '')
        attivo = 'attivo' in request.form
        data_inizio = request.form.get('data_inizio')
        data_fine = request.form.get('data_fine')

        # Se questa posizione viene attivata, disattiva le altre
        if attivo:
            cursor1 = execute_query(conn, '''
                UPDATE current_location
                SET attivo = ?
                WHERE user_id = ? AND id != ?
            ''', (False, user_id, location_id))
            conn.commit()
            cursor1.close()

        cursor2 = execute_query(conn, '''
            UPDATE current_location
            SET nome_luogo = ?, indirizzo = ?, google_maps_link = ?,
                orario = ?, note = ?, immagine_url = ?, attivo = ?,
                data_inizio = ?, data_fine = ?
            WHERE id = ? AND user_id = ?
        ''', (nome_luogo, indirizzo, google_maps_link, orario, note, immagine_url,
              attivo, data_inizio if data_inizio else None,
              data_fine if data_fine else None, location_id, user_id))

        conn.commit()
        cursor2.close()
        conn.close()

        flash('Posizione aggiornata!', 'success')
        return redirect(url_for('location.index'))

    location = execute_query(conn, '''
        SELECT id, nome_luogo, indirizzo, google_maps_link, orario, note,
               immagine_url, attivo, data_inizio, data_fine
        FROM current_location
        WHERE id = ? AND user_id = ?
    ''', (location_id, user_id), fetch_one=True)

    conn.close()

    if not location:
        flash('Posizione non trovata', 'error')
        return redirect(url_for('location.index'))

    return render_template('location/edit_location.html', location=location)

@bp.route('/delete/<int:location_id>', methods=['POST'])
@login_required
def delete_location(location_id):
    """Elimina posizione"""
    conn = get_db()
    user_id = session['user_id']

    cursor = execute_query(conn, '''
        DELETE FROM current_location
        WHERE id = ? AND user_id = ?
    ''', (location_id, user_id))

    conn.commit()
    cursor.close()
    conn.close()

    flash('Posizione eliminata', 'success')
    return redirect(url_for('location.index'))

@bp.route('/deactivate-all', methods=['POST'])
@login_required
def deactivate_all():
    """Disattiva tutte le posizioni (non esisto)"""
    conn = get_db()
    user_id = session['user_id']

    cursor = execute_query(conn, '''
        UPDATE current_location
        SET attivo = ?
        WHERE user_id = ?
    ''', (False, user_id))

    conn.commit()
    cursor.close()
    conn.close()

    flash('Tutte le posizioni disattivate', 'success')
    return redirect(url_for('location.index'))
