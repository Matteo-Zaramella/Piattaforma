from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
import sqlite3
from datetime import datetime

bp = Blueprint('task_privati', __name__, url_prefix='/task-privati')

def get_db():
    db = sqlite3.connect('piattaforma.db')
    db.row_factory = sqlite3.Row
    return db

@bp.route('/')
def index():
    """Visualizza tutti i task privati"""
    db = get_db()
    user_id = session['user_id']

    filter_stato = request.args.get('stato', 'all')

    query = 'SELECT * FROM task_privati WHERE user_id = ?'
    params = [user_id]

    if filter_stato != 'all':
        query += ' AND stato = ?'
        params.append(filter_stato)

    query += ' ORDER BY CASE WHEN deadline IS NULL THEN 1 ELSE 0 END, deadline ASC, created_at DESC'

    tasks = db.execute(query, params).fetchall()

    # Conta task per stato
    counts = {
        'da_fare': db.execute('SELECT COUNT(*) as cnt FROM task_privati WHERE user_id = ? AND stato = "da_fare"', (user_id,)).fetchone()['cnt'],
        'in_corso': db.execute('SELECT COUNT(*) as cnt FROM task_privati WHERE user_id = ? AND stato = "in_corso"', (user_id,)).fetchone()['cnt'],
        'completato': db.execute('SELECT COUNT(*) as cnt FROM task_privati WHERE user_id = ? AND stato = "completato"', (user_id,)).fetchone()['cnt']
    }

    db.close()

    return render_template('task_privati/index.html', tasks=tasks, counts=counts, filter_stato=filter_stato)

@bp.route('/add', methods=['GET', 'POST'])
def add():
    """Aggiungi nuovo task"""
    if request.method == 'POST':
        db = get_db()
        user_id = session['user_id']

        data = {
            'user_id': user_id,
            'titolo': request.form['titolo'],
            'descrizione': request.form.get('descrizione', ''),
            'priorita': request.form.get('priorita', 'media'),
            'stato': request.form.get('stato', 'da_fare'),
            'deadline': request.form.get('deadline') if request.form.get('deadline') else None,
            'ricorrente': 1 if request.form.get('ricorrente') else 0
        }

        db.execute('''
            INSERT INTO task_privati (user_id, titolo, descrizione, priorita, stato, deadline, ricorrente)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (data['user_id'], data['titolo'], data['descrizione'], data['priorita'], data['stato'], data['deadline'], data['ricorrente']))

        db.commit()
        db.close()

        flash('Task aggiunto con successo!', 'success')
        return redirect(url_for('task_privati.index'))

    return render_template('task_privati/add.html')

@bp.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit(task_id):
    """Modifica task esistente"""
    db = get_db()
    user_id = session['user_id']

    if request.method == 'POST':
        data = {
            'titolo': request.form['titolo'],
            'descrizione': request.form.get('descrizione', ''),
            'priorita': request.form.get('priorita', 'media'),
            'stato': request.form.get('stato', 'da_fare'),
            'deadline': request.form.get('deadline') if request.form.get('deadline') else None,
            'ricorrente': 1 if request.form.get('ricorrente') else 0
        }

        # Se stato cambia a completato, salva timestamp
        completed_at = None
        if data['stato'] == 'completato':
            completed_at = datetime.now().isoformat()

        db.execute('''
            UPDATE task_privati SET
                titolo = ?, descrizione = ?, priorita = ?, stato = ?, deadline = ?, ricorrente = ?, completed_at = ?
            WHERE id = ? AND user_id = ?
        ''', (data['titolo'], data['descrizione'], data['priorita'], data['stato'], data['deadline'], data['ricorrente'], completed_at, task_id, user_id))

        db.commit()
        db.close()

        flash('Task aggiornato con successo!', 'success')
        return redirect(url_for('task_privati.index'))

    # GET - mostra form di modifica
    task = db.execute('SELECT * FROM task_privati WHERE id = ? AND user_id = ?', (task_id, user_id)).fetchone()
    db.close()

    if not task:
        flash('Task non trovato', 'error')
        return redirect(url_for('task_privati.index'))

    return render_template('task_privati/edit.html', task=task)

@bp.route('/delete/<int:task_id>', methods=['POST'])
def delete(task_id):
    """Elimina task"""
    db = get_db()
    user_id = session['user_id']

    db.execute('DELETE FROM task_privati WHERE id = ? AND user_id = ?', (task_id, user_id))
    db.commit()
    db.close()

    flash('Task eliminato', 'success')
    return redirect(url_for('task_privati.index'))

@bp.route('/toggle-status/<int:task_id>', methods=['POST'])
def toggle_status(task_id):
    """Cambia velocemente lo stato del task"""
    db = get_db()
    user_id = session['user_id']

    task = db.execute('SELECT stato FROM task_privati WHERE id = ? AND user_id = ?', (task_id, user_id)).fetchone()

    if task:
        new_stato = 'completato' if task['stato'] != 'completato' else 'da_fare'
        completed_at = datetime.now().isoformat() if new_stato == 'completato' else None

        db.execute('UPDATE task_privati SET stato = ?, completed_at = ? WHERE id = ? AND user_id = ?',
                   (new_stato, completed_at, task_id, user_id))
        db.commit()

    db.close()
    return redirect(url_for('task_privati.index'))
