from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from functools import wraps
import os

bp = Blueprint('wishlist', __name__, url_prefix='/wishlist')

# Determina se usare PostgreSQL o SQLite
USE_POSTGRES = os.getenv('DATABASE_URL') is not None

def get_db():
    """Importa get_db dal modulo principale"""
    from app import get_db as main_get_db
    return main_get_db()

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
    """Visualizza tutti gli item della wishlist"""
    conn = get_db()
    cursor = conn.cursor()
    user_id = session['user_id']

    try:
        if USE_POSTGRES:
            from psycopg2.extras import RealDictCursor
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            placeholder = '%s'
        else:
            placeholder = '?'

        cursor.execute(f'''
            SELECT id, titolo, descrizione, prezzo, link, priorita, acquistato, created_at
            FROM wishlist
            WHERE user_id = {placeholder}
            ORDER BY
                CASE priorita
                    WHEN 'alta' THEN 1
                    WHEN 'media' THEN 2
                    ELSE 3
                END,
                created_at DESC
        ''', (user_id,))
        items = cursor.fetchall()

        cursor.close()
        conn.close()
        return render_template('wishlist/index.html', items=items)

    except Exception as e:
        print(f"Errore wishlist index: {e}")
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        flash(f'Errore caricamento wishlist: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_item():
    """Aggiungi nuovo item alla wishlist"""
    if request.method == 'POST':
        titolo = request.form['titolo']
        descrizione = request.form.get('descrizione', '')
        prezzo = request.form.get('prezzo', 0)
        link = request.form.get('link', '')
        priorita = request.form.get('priorita', 'media')

        conn = get_db()
        cursor = conn.cursor()
        user_id = session['user_id']

        try:
            if USE_POSTGRES:
                placeholder = '%s'
            else:
                placeholder = '?'

            cursor.execute(f'''
                INSERT INTO wishlist (user_id, titolo, descrizione, prezzo, link, priorita, acquistato)
                VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
            ''', (user_id, titolo, descrizione, prezzo, link, priorita, False))

            conn.commit()
            cursor.close()
            conn.close()

            flash('Item aggiunto alla wishlist!', 'success')
            return redirect(url_for('wishlist.index'))

        except Exception as e:
            print(f"Errore wishlist add: {e}")
            conn.rollback()
            cursor.close()
            conn.close()
            flash(f'Errore aggiunta item: {str(e)}', 'danger')
            return redirect(url_for('wishlist.add_item'))

    return render_template('wishlist/add_item.html')

@bp.route('/edit/<int:item_id>', methods=['GET', 'POST'])
@login_required
def edit_item(item_id):
    """Modifica item esistente"""
    conn = get_db()
    cursor = conn.cursor()
    user_id = session['user_id']

    try:
        if USE_POSTGRES:
            from psycopg2.extras import RealDictCursor
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            placeholder = '%s'
        else:
            placeholder = '?'

        if request.method == 'POST':
            titolo = request.form['titolo']
            descrizione = request.form.get('descrizione', '')
            prezzo = request.form.get('prezzo', 0)
            link = request.form.get('link', '')
            priorita = request.form.get('priorita', 'media')

            cursor.execute(f'''
                UPDATE wishlist
                SET titolo = {placeholder}, descrizione = {placeholder}, prezzo = {placeholder},
                    link = {placeholder}, priorita = {placeholder}
                WHERE id = {placeholder} AND user_id = {placeholder}
            ''', (titolo, descrizione, prezzo, link, priorita, item_id, user_id))

            conn.commit()
            cursor.close()
            conn.close()

            flash('Item aggiornato!', 'success')
            return redirect(url_for('wishlist.index'))

        # GET request
        cursor.execute(f'''
            SELECT id, titolo, descrizione, prezzo, link, priorita, acquistato
            FROM wishlist
            WHERE id = {placeholder} AND user_id = {placeholder}
        ''', (item_id, user_id))
        item = cursor.fetchone()

        cursor.close()
        conn.close()

        if not item:
            flash('Item non trovato', 'warning')
            return redirect(url_for('wishlist.index'))

        return render_template('wishlist/edit_item.html', item=item)

    except Exception as e:
        print(f"Errore wishlist edit: {e}")
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        flash(f'Errore modifica item: {str(e)}', 'danger')
        return redirect(url_for('wishlist.index'))

@bp.route('/delete/<int:item_id>')
@login_required
def delete_item(item_id):
    """Elimina item dalla wishlist"""
    conn = get_db()
    cursor = conn.cursor()
    user_id = session['user_id']

    try:
        if USE_POSTGRES:
            placeholder = '%s'
        else:
            placeholder = '?'

        cursor.execute(f'''
            DELETE FROM wishlist
            WHERE id = {placeholder} AND user_id = {placeholder}
        ''', (item_id, user_id))

        conn.commit()
        cursor.close()
        conn.close()

        flash('Item eliminato!', 'success')
        return redirect(url_for('wishlist.index'))

    except Exception as e:
        print(f"Errore wishlist delete: {e}")
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        flash(f'Errore eliminazione item: {str(e)}', 'danger')
        return redirect(url_for('wishlist.index'))

@bp.route('/toggle/<int:item_id>')
@login_required
def toggle_acquistato(item_id):
    """Segna come acquistato/non acquistato"""
    conn = get_db()
    cursor = conn.cursor()
    user_id = session['user_id']

    try:
        if USE_POSTGRES:
            from psycopg2.extras import RealDictCursor
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            placeholder = '%s'
        else:
            placeholder = '?'

        cursor.execute(f'''
            UPDATE wishlist
            SET acquistato = NOT acquistato
            WHERE id = {placeholder} AND user_id = {placeholder}
        ''', (item_id, user_id))

        conn.commit()
        cursor.close()
        conn.close()

        flash('Stato aggiornato!', 'success')
        return redirect(url_for('wishlist.index'))

    except Exception as e:
        print(f"Errore wishlist toggle: {e}")
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        flash(f'Errore aggiornamento: {str(e)}', 'danger')
        return redirect(url_for('wishlist.index'))
