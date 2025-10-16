from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
import sqlite3
from datetime import datetime

bp = Blueprint('matched_betting', __name__, url_prefix='/matched-betting')

def get_db():
    db = sqlite3.connect('piattaforma.db')
    db.row_factory = sqlite3.Row
    return db

@bp.route('/')
def index():
    """Visualizza tutte le scommesse"""
    db = get_db()
    user_id = session['user_id']

    bets = db.execute('''
        SELECT * FROM matched_betting
        WHERE user_id = ?
        ORDER BY data_evento DESC, created_at DESC
    ''', (user_id,)).fetchall()

    # Calcola profitto totale
    total_profit = db.execute('''
        SELECT COALESCE(SUM(profitto), 0) as total
        FROM matched_betting
        WHERE user_id = ?
    ''', (user_id,)).fetchone()['total']

    db.close()

    return render_template('matched_betting/index.html', bets=bets, total_profit=total_profit)

@bp.route('/add', methods=['GET', 'POST'])
def add():
    """Aggiungi nuova scommessa"""
    if request.method == 'POST':
        db = get_db()
        user_id = session['user_id']

        # Raccogli dati dal form
        data = {
            'user_id': user_id,
            'bookmaker_back': request.form['bookmaker_back'],
            'bookmaker_lay': request.form.get('bookmaker_lay', ''),
            'stake_back': float(request.form['stake_back']) if request.form['stake_back'] else None,
            'stake_lay': float(request.form['stake_lay']) if request.form.get('stake_lay') else None,
            'quota_back': float(request.form['quota_back']) if request.form['quota_back'] else None,
            'quota_lay': float(request.form['quota_lay']) if request.form.get('quota_lay') else None,
            'rating': request.form.get('rating', ''),
            'mercato': request.form.get('mercato', ''),
            'offerta': request.form.get('offerta', ''),
            'evento': request.form['evento'],
            'data_evento': request.form.get('data_evento'),
            'profitto': float(request.form['profitto']) if request.form.get('profitto') else 0,
            'note': request.form.get('note', '')
        }

        db.execute('''
            INSERT INTO matched_betting (
                user_id, bookmaker_back, bookmaker_lay, stake_back, stake_lay,
                quota_back, quota_lay, rating, mercato, offerta, evento,
                data_evento, profitto, note
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['user_id'], data['bookmaker_back'], data['bookmaker_lay'],
            data['stake_back'], data['stake_lay'], data['quota_back'], data['quota_lay'],
            data['rating'], data['mercato'], data['offerta'], data['evento'],
            data['data_evento'], data['profitto'], data['note']
        ))

        db.commit()
        bet_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
        db.close()

        # TODO: Integrazione Google Calendar
        # if data['data_evento']:
        #     create_calendar_event(data['evento'], data['data_evento'])

        flash('Scommessa aggiunta con successo!', 'success')
        return redirect(url_for('matched_betting.index'))

    return render_template('matched_betting/add.html')

@bp.route('/edit/<int:bet_id>', methods=['GET', 'POST'])
def edit(bet_id):
    """Modifica scommessa esistente"""
    db = get_db()
    user_id = session['user_id']

    if request.method == 'POST':
        # Aggiorna dati
        data = {
            'bookmaker_back': request.form['bookmaker_back'],
            'bookmaker_lay': request.form.get('bookmaker_lay', ''),
            'stake_back': float(request.form['stake_back']) if request.form['stake_back'] else None,
            'stake_lay': float(request.form['stake_lay']) if request.form.get('stake_lay') else None,
            'quota_back': float(request.form['quota_back']) if request.form['quota_back'] else None,
            'quota_lay': float(request.form['quota_lay']) if request.form.get('quota_lay') else None,
            'rating': request.form.get('rating', ''),
            'mercato': request.form.get('mercato', ''),
            'offerta': request.form.get('offerta', ''),
            'evento': request.form['evento'],
            'data_evento': request.form.get('data_evento'),
            'profitto': float(request.form['profitto']) if request.form.get('profitto') else 0,
            'note': request.form.get('note', '')
        }

        db.execute('''
            UPDATE matched_betting SET
                bookmaker_back = ?, bookmaker_lay = ?, stake_back = ?, stake_lay = ?,
                quota_back = ?, quota_lay = ?, rating = ?, mercato = ?, offerta = ?,
                evento = ?, data_evento = ?, profitto = ?, note = ?
            WHERE id = ? AND user_id = ?
        ''', (
            data['bookmaker_back'], data['bookmaker_lay'], data['stake_back'], data['stake_lay'],
            data['quota_back'], data['quota_lay'], data['rating'], data['mercato'],
            data['offerta'], data['evento'], data['data_evento'], data['profitto'],
            data['note'], bet_id, user_id
        ))

        db.commit()
        db.close()

        flash('Scommessa aggiornata con successo!', 'success')
        return redirect(url_for('matched_betting.index'))

    # GET - mostra form di modifica
    bet = db.execute('SELECT * FROM matched_betting WHERE id = ? AND user_id = ?', (bet_id, user_id)).fetchone()
    db.close()

    if not bet:
        flash('Scommessa non trovata', 'error')
        return redirect(url_for('matched_betting.index'))

    return render_template('matched_betting/edit.html', bet=bet)

@bp.route('/delete/<int:bet_id>', methods=['POST'])
def delete(bet_id):
    """Elimina scommessa"""
    db = get_db()
    user_id = session['user_id']

    db.execute('DELETE FROM matched_betting WHERE id = ? AND user_id = ?', (bet_id, user_id))
    db.commit()
    db.close()

    flash('Scommessa eliminata', 'success')
    return redirect(url_for('matched_betting.index'))

@bp.route('/stats')
def stats():
    """Statistiche matched betting"""
    db = get_db()
    user_id = session['user_id']

    stats = {
        'total_bets': db.execute('SELECT COUNT(*) as cnt FROM matched_betting WHERE user_id = ?', (user_id,)).fetchone()['cnt'],
        'total_profit': db.execute('SELECT COALESCE(SUM(profitto), 0) as total FROM matched_betting WHERE user_id = ?', (user_id,)).fetchone()['total'],
        'avg_profit': db.execute('SELECT COALESCE(AVG(profitto), 0) as avg FROM matched_betting WHERE user_id = ?', (user_id,)).fetchone()['avg'],
        'by_bookmaker': db.execute('''
            SELECT bookmaker_back, COUNT(*) as count, SUM(profitto) as profit
            FROM matched_betting
            WHERE user_id = ?
            GROUP BY bookmaker_back
            ORDER BY profit DESC
        ''', (user_id,)).fetchall(),
        'by_month': db.execute('''
            SELECT strftime('%Y-%m', created_at) as month, COUNT(*) as count, SUM(profitto) as profit
            FROM matched_betting
            WHERE user_id = ?
            GROUP BY month
            ORDER BY month DESC
            LIMIT 12
        ''', (user_id,)).fetchall()
    }

    db.close()

    return render_template('matched_betting/stats.html', stats=stats)
