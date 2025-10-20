from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from functools import wraps
import sys
import os

# Importa funzioni database dal parent
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db_utils import get_db, execute_query

bp = Blueprint('appointments', __name__, url_prefix='/appointments')

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
    """Visualizza tutti gli appuntamenti"""
    conn = get_db()
    user_id = session['user_id']

    appointments = execute_query(conn, '''
        SELECT id, titolo, descrizione, data_ora, luogo, pubblico, completato, created_at
        FROM appointments
        WHERE user_id = ?
        ORDER BY data_ora ASC
    ''', (user_id,), fetch_all=True)

    conn.close()
    return render_template('appointments/index.html', appointments=appointments)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_appointment():
    """Aggiungi nuovo appuntamento"""
    if request.method == 'POST':
        titolo = request.form['titolo']
        descrizione = request.form.get('descrizione', '')
        data_ora = request.form['data_ora']
        luogo = request.form.get('luogo', '')
        pubblico = 'pubblico' in request.form

        conn = get_db()
        user_id = session['user_id']

        cursor = execute_query(conn, '''
            INSERT INTO appointments (user_id, titolo, descrizione, data_ora, luogo, pubblico)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, titolo, descrizione, data_ora, luogo, pubblico))

        conn.commit()
        cursor.close()
        conn.close()

        flash('Appuntamento aggiunto!', 'success')
        return redirect(url_for('appointments.index'))

    return render_template('appointments/add_appointment.html')

@bp.route('/edit/<int:appointment_id>', methods=['GET', 'POST'])
@login_required
def edit_appointment(appointment_id):
    """Modifica appuntamento esistente"""
    conn = get_db()
    user_id = session['user_id']

    if request.method == 'POST':
        titolo = request.form['titolo']
        descrizione = request.form.get('descrizione', '')
        data_ora = request.form['data_ora']
        luogo = request.form.get('luogo', '')
        pubblico = 'pubblico' in request.form
        completato = 'completato' in request.form

        cursor = execute_query(conn, '''
            UPDATE appointments
            SET titolo = ?, descrizione = ?, data_ora = ?, luogo = ?,
                pubblico = ?, completato = ?
            WHERE id = ? AND user_id = ?
        ''', (titolo, descrizione, data_ora, luogo, pubblico, completato,
              appointment_id, user_id))

        conn.commit()
        cursor.close()
        conn.close()

        flash('Appuntamento aggiornato!', 'success')
        return redirect(url_for('appointments.index'))

    appointment = execute_query(conn, '''
        SELECT id, titolo, descrizione, data_ora, luogo, pubblico, completato
        FROM appointments
        WHERE id = ? AND user_id = ?
    ''', (appointment_id, user_id), fetch_one=True)

    conn.close()

    if not appointment:
        flash('Appuntamento non trovato', 'error')
        return redirect(url_for('appointments.index'))

    return render_template('appointments/edit_appointment.html', appointment=appointment)

@bp.route('/delete/<int:appointment_id>', methods=['POST'])
@login_required
def delete_appointment(appointment_id):
    """Elimina appuntamento"""
    conn = get_db()
    user_id = session['user_id']

    cursor = execute_query(conn, '''
        DELETE FROM appointments
        WHERE id = ? AND user_id = ?
    ''', (appointment_id, user_id))

    conn.commit()
    cursor.close()
    conn.close()

    flash('Appuntamento eliminato', 'success')
    return redirect(url_for('appointments.index'))

@bp.route('/toggle-complete/<int:appointment_id>', methods=['POST'])
@login_required
def toggle_complete(appointment_id):
    """Segna appuntamento come completato/non completato"""
    conn = get_db()
    user_id = session['user_id']

    # Get current status
    appointment = execute_query(conn, '''
        SELECT completato FROM appointments
        WHERE id = ? AND user_id = ?
    ''', (appointment_id, user_id), fetch_one=True)

    if appointment:
        new_status = not appointment['completato']

        cursor = execute_query(conn, '''
            UPDATE appointments
            SET completato = ?
            WHERE id = ? AND user_id = ?
        ''', (new_status, appointment_id, user_id))

        conn.commit()
        cursor.close()

    conn.close()

    flash('Stato appuntamento aggiornato', 'success')
    return redirect(url_for('appointments.index'))
