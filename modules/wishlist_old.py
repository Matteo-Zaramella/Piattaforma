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
    user_id = session['user_id']

    items = execute_query(conn, '''
        SELECT id, nome, descrizione, link, priorita, pubblico, created_at
        FROM wishlist
        WHERE user_id = ?
        ORDER BY
            CASE priorita
                WHEN 'alta' THEN 1
                WHEN 'media' THEN 2
                ELSE 3
            END,
            created_at DESC
    ''', (user_id,), fetch_all=True)

    conn.close()
    return render_template('wishlist/index.html', items=items)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_item():
    """Aggiungi nuovo item alla wishlist"""
    if request.method == 'POST':
        nome = request.form['nome']
        descrizione = request.form.get('descrizione', '')
        link = request.form.get('link', '')
        priorita = request.form.get('priorita', 'media')
        pubblico = 'pubblico' in request.form

        conn = get_db()
        user_id = session['user_id']

        cursor = execute_query(conn, '''
            INSERT INTO wishlist (user_id, nome, descrizione, link, priorita, pubblico)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, nome, descrizione, link, priorita, pubblico))

        conn.commit()
        cursor.close()
        conn.close()

        flash('Item aggiunto alla wishlist!', 'success')
        return redirect(url_for('wishlist.index'))

    return render_template('wishlist/add_item.html')

@bp.route('/edit/<int:item_id>', methods=['GET', 'POST'])
@login_required
def edit_item(item_id):
    """Modifica item esistente"""
    conn = get_db()
    user_id = session['user_id']

    if request.method == 'POST':
        nome = request.form['nome']
        descrizione = request.form.get('descrizione', '')
        link = request.form.get('link', '')
        priorita = request.form.get('priorita', 'media')
        pubblico = 'pubblico' in request.form

        cursor = execute_query(conn, '''
            UPDATE wishlist
            SET nome = ?, descrizione = ?, link = ?, priorita = ?, pubblico = ?
            WHERE id = ? AND user_id = ?
        ''', (nome, descrizione, link, priorita, pubblico, item_id, user_id))

        conn.commit()
        cursor.close()
        conn.close()

        flash('Item aggiornato!', 'success')
        return redirect(url_for('wishlist.index'))

    item = execute_query(conn, '''
        SELECT id, nome, descrizione, link, priorita, pubblico
        FROM wishlist
        WHERE id = ? AND user_id = ?
    ''', (item_id, user_id), fetch_one=True)

    conn.close()

    if not item:
        flash('Item non trovato', 'error')
        return redirect(url_for('wishlist.index'))

    return render_template('wishlist/edit_item.html', item=item)

@bp.route('/delete/<int:item_id>', methods=['POST'])
@login_required
def delete_item(item_id):
    """Elimina item"""
    conn = get_db()
    user_id = session['user_id']

    cursor = execute_query(conn, '''
        DELETE FROM wishlist
        WHERE id = ? AND user_id = ?
    ''', (item_id, user_id))

    conn.commit()
    cursor.close()
    conn.close()

    flash('Item eliminato', 'success')
    return redirect(url_for('wishlist.index'))
