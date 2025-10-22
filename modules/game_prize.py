from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
from functools import wraps
from datetime import datetime
import json

bp = Blueprint('game_prize', __name__, url_prefix='/game-prize')

# Decorator per verificare login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Devi essere loggato', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Decorator per verificare admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Devi essere loggato', 'warning')
            return redirect(url_for('login'))

        # TODO: aggiungere verifica se utente è admin (da implementare in phase 2)
        return f(*args, **kwargs)
    return decorated_function

# Decorator per proteggere Game Prize con password
def game_prize_password_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('game_admin_authenticated', False):
            flash('Accesso negato. Il Game Prize è protetto da password.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def get_db():
    """Importa get_db dal modulo principale"""
    from app import get_db as main_get_db
    return main_get_db()

# ============== ROUTES PUBBLICHE ==============

@bp.route('/admin/welcome')
@login_required
@game_prize_password_required
def admin_welcome():
    """Pagina di benvenuto per l'admin con guida setup"""
    return render_template('game_prize/admin_welcome.html')

@bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principale del gioco a premi"""
    conn = get_db()
    cursor = conn.cursor()
    user_id = session['user_id']

    try:
        # Ottieni informazioni del gioco
        cursor.execute('''
            SELECT * FROM game_prize_config
            WHERE id = 1
        ''')
        game_config = cursor.fetchone()

        # Ottieni tutte le sfide
        cursor.execute('''
            SELECT * FROM game_challenges
            ORDER BY challenge_number ASC
        ''')
        challenges = cursor.fetchall()

        # Ottieni il punteggio dell'utente
        cursor.execute('''
            SELECT SUM(points) as total_points
            FROM game_user_scores
            WHERE user_id = %s
        ''', (user_id,))
        score_result = cursor.fetchone()
        user_total_points = score_result[0] if score_result and score_result[0] else 0

        # Ottieni le sfide completate dall'utente
        cursor.execute('''
            SELECT challenge_id FROM game_user_completions
            WHERE user_id = %s
        ''', (user_id,))
        completed_challenges = [row[0] for row in cursor.fetchall()]

        # Conta quante sfide sono state completate (per determinare se rivelare il vincitore)
        total_challenges = len(challenges)
        completed_count = len(completed_challenges)

        # Determina se è il momento di rivelare il vincitore (50% = 6 sfide su 12)
        reveal_winner = completed_count >= (total_challenges // 2)

        context = {
            'game_config': game_config,
            'challenges': challenges,
            'user_total_points': user_total_points,
            'completed_challenges': completed_challenges,
            'reveal_winner': reveal_winner,
            'completed_count': completed_count,
            'total_challenges': total_challenges
        }

        conn.close()
        return render_template('game_prize/dashboard.html', **context)

    except Exception as e:
        conn.close()
        flash(f'Errore nel caricamento dashboard: {str(e)}', 'danger')
        return redirect(url_for('index'))

@bp.route('/challenge/<int:challenge_id>')
@login_required
def view_challenge(challenge_id):
    """Visualizza i dettagli di una sfida"""
    conn = get_db()
    cursor = conn.cursor()
    user_id = session['user_id']

    try:
        # Ottieni i dettagli della sfida
        cursor.execute('''
            SELECT * FROM game_challenges
            WHERE id = %s
        ''', (challenge_id,))
        challenge = cursor.fetchone()

        if not challenge:
            flash('Sfida non trovata', 'warning')
            return redirect(url_for('game_prize.dashboard'))

        # Verifica se l'utente ha completato questa sfida
        cursor.execute('''
            SELECT * FROM game_user_completions
            WHERE user_id = %s AND challenge_id = %s
        ''', (user_id, challenge_id))
        user_completion = cursor.fetchone()

        # Ottieni gli indizi per questa sfida
        cursor.execute('''
            SELECT * FROM game_clues
            WHERE challenge_id = %s
            ORDER BY clue_number ASC
        ''', (challenge_id,))
        clues = cursor.fetchall()

        context = {
            'challenge': challenge,
            'user_completion': user_completion,
            'clues': clues
        }

        conn.close()
        return render_template('game_prize/challenge_detail.html', **context)

    except Exception as e:
        conn.close()
        flash(f'Errore nel caricamento sfida: {str(e)}', 'danger')
        return redirect(url_for('game_prize.dashboard'))

@bp.route('/clues/<int:challenge_id>')
@login_required
def get_clues(challenge_id):
    """API endpoint per ottenere gli indizi di una sfida (JSON)"""
    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            SELECT id, clue_number, clue_text, revealed_date
            FROM game_clues
            WHERE challenge_id = %s
            ORDER BY clue_number ASC
        ''', (challenge_id,))

        clues = cursor.fetchall()
        clues_list = []

        for clue in clues:
            clues_list.append({
                'id': clue[0],
                'clue_number': clue[1],
                'text': clue[2],
                'revealed_date': clue[3]
            })

        conn.close()
        return jsonify(clues_list)

    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@bp.route('/leaderboard')
@login_required
def leaderboard():
    """Visualizza la classifica dei giocatori"""
    conn = get_db()
    cursor = conn.cursor()
    user_id = session['user_id']

    try:
        # Ottieni il config per sapere se rivelare il vincitore
        cursor.execute('''
            SELECT total_challenges FROM game_prize_config
            WHERE id = 1
        ''')
        config = cursor.fetchone()
        total_challenges = config[0] if config else 12

        # Ottieni la classifica (somma punti per utente)
        cursor.execute('''
            SELECT u.id, u.username, COALESCE(SUM(gus.points), 0) as total_points,
                   COUNT(DISTINCT guc.challenge_id) as completed_challenges
            FROM users u
            LEFT JOIN game_user_scores gus ON u.id = gus.user_id
            LEFT JOIN game_user_completions guc ON u.id = guc.user_id
            GROUP BY u.id, u.username
            ORDER BY total_points DESC
        ''')

        leaderboard_data = cursor.fetchall()

        # Converti in lista di dizionari
        leaderboard = []
        for idx, row in enumerate(leaderboard_data, 1):
            leaderboard.append({
                'position': idx,
                'user_id': row[0],
                'username': row[1],
                'total_points': row[2],
                'completed_challenges': row[3],
                'is_current_user': row[0] == user_id
            })

        # Conta sfide completate per determinare reveal
        cursor.execute('''
            SELECT COUNT(DISTINCT challenge_id) FROM game_user_completions
        ''')
        total_completed = cursor.fetchone()[0]

        reveal_winner = total_completed >= (total_challenges // 2)

        context = {
            'leaderboard': leaderboard,
            'user_position': next((lb['position'] for lb in leaderboard if lb['is_current_user']), None),
            'reveal_winner': reveal_winner,
            'completed_challenges': total_completed,
            'total_challenges': total_challenges
        }

        conn.close()
        return render_template('game_prize/leaderboard.html', **context)

    except Exception as e:
        conn.close()
        flash(f'Errore nel caricamento classifica: {str(e)}', 'danger')
        return redirect(url_for('game_prize.dashboard'))

@bp.route('/complete-challenge/<int:challenge_id>', methods=['POST'])
@login_required
def complete_challenge(challenge_id):
    """Marca una sfida come completata e aggiunge punti"""
    conn = get_db()
    cursor = conn.cursor()
    user_id = session['user_id']

    try:
        # Ottieni la sfida
        cursor.execute('''
            SELECT points FROM game_challenges
            WHERE id = %s
        ''', (challenge_id,))
        challenge = cursor.fetchone()

        if not challenge:
            return jsonify({'error': 'Sfida non trovata'}), 404

        points = challenge[0]

        # Verifica se già completata
        cursor.execute('''
            SELECT id FROM game_user_completions
            WHERE user_id = %s AND challenge_id = %s
        ''', (user_id, challenge_id))

        if cursor.fetchone():
            return jsonify({'error': 'Sfida già completata'}), 400

        # Aggiungi il completamento
        cursor.execute('''
            INSERT INTO game_user_completions (user_id, challenge_id, completed_date)
            VALUES (%s, %s, CURRENT_TIMESTAMP)
        ''', (user_id, challenge_id))

        # Aggiungi i punti
        cursor.execute('''
            INSERT INTO game_user_scores (user_id, challenge_id, points)
            VALUES (%s, %s, %s)
        ''', (user_id, challenge_id, points))

        conn.commit()
        conn.close()

        return jsonify({'success': True, 'points': points, 'message': f'Hai guadagnato {points} punti!'})

    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'error': str(e)}), 500

# ============== ROUTES ADMIN ==============

@bp.route('/admin/setup', methods=['GET', 'POST'])
@login_required
@game_prize_password_required
def admin_setup():
    """Setup iniziale del gioco (da proteggere con password admin)"""
    # TODO: Implementare protezione password

    if request.method == 'POST':
        conn = get_db()
        cursor = conn.cursor()

        try:
            game_name = request.form.get('game_name', 'Premio di Compleanno')
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            total_challenges = int(request.form.get('total_challenges', 12))
            description = request.form.get('description', '')

            # Verifica se config esiste già
            cursor.execute('SELECT id FROM game_prize_config WHERE id = 1')
            if cursor.fetchone():
                cursor.execute('''
                    UPDATE game_prize_config
                    SET game_name = %s, start_date = %s, end_date = %s,
                        total_challenges = %s, description = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE id = 1
                ''', (game_name, start_date, end_date, total_challenges, description))
            else:
                cursor.execute('''
                    INSERT INTO game_prize_config (game_name, start_date, end_date, total_challenges, description)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (game_name, start_date, end_date, total_challenges, description))

            conn.commit()
            conn.close()

            flash('Configurazione gioco salvata con successo', 'success')
            return redirect(url_for('game_prize.admin_dashboard'))

        except Exception as e:
            conn.rollback()
            conn.close()
            flash(f'Errore nella configurazione: {str(e)}', 'danger')

    # GET request: mostra il form
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM game_prize_config WHERE id = 1')
    config = cursor.fetchone()
    conn.close()

    return render_template('game_prize/admin_setup.html', config=config)

@bp.route('/admin/dashboard')
@login_required
@game_prize_password_required
def admin_dashboard():
    """Dashboard amministrativo del gioco"""

    conn = get_db()
    cursor = conn.cursor()

    try:
        # Ottieni config
        cursor.execute('SELECT * FROM game_prize_config WHERE id = 1')
        config = cursor.fetchone()

        # Ottieni tutte le sfide
        cursor.execute('SELECT * FROM game_challenges ORDER BY challenge_number ASC')
        challenges = cursor.fetchall()

        # Statistiche
        cursor.execute('SELECT COUNT(DISTINCT user_id) FROM game_user_completions')
        total_players = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(DISTINCT challenge_id) FROM game_user_completions')
        total_completions = cursor.fetchone()[0]

        context = {
            'config': config,
            'challenges': challenges,
            'total_players': total_players,
            'total_completions': total_completions
        }

        conn.close()
        return render_template('game_prize/admin_dashboard.html', **context)

    except Exception as e:
        conn.close()
        flash(f'Errore: {str(e)}', 'danger')
        return redirect(url_for('index'))

@bp.route('/admin/challenge/add', methods=['GET', 'POST'])
@login_required
@game_prize_password_required
def admin_add_challenge():
    """Aggiungi una nuova sfida"""

    if request.method == 'POST':
        conn = get_db()
        cursor = conn.cursor()

        try:
            challenge_number = int(request.form.get('challenge_number'))
            title = request.form.get('title')
            description = request.form.get('description')
            points = int(request.form.get('points', 100))
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            location = request.form.get('location', '')
            instructions = request.form.get('instructions', '')

            cursor.execute('''
                INSERT INTO game_challenges
                (challenge_number, title, description, points, start_date, end_date, location, instructions)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''', (challenge_number, title, description, points, start_date, end_date, location, instructions))

            conn.commit()
            conn.close()

            flash(f'Sfida "{title}" aggiunta con successo', 'success')
            return redirect(url_for('game_prize.admin_dashboard'))

        except Exception as e:
            conn.rollback()
            conn.close()
            flash(f'Errore nell\'aggiunta sfida: {str(e)}', 'danger')

    return render_template('game_prize/admin_add_challenge.html')

@bp.route('/admin/challenge/<int:challenge_id>/edit', methods=['GET', 'POST'])
@login_required
@game_prize_password_required
def admin_edit_challenge(challenge_id):
    """Modifica una sfida"""

    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        try:
            title = request.form.get('title')
            description = request.form.get('description')
            points = int(request.form.get('points', 100))
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            location = request.form.get('location', '')
            instructions = request.form.get('instructions', '')

            cursor.execute('''
                UPDATE game_challenges
                SET title = %s, description = %s, points = %s, start_date = %s,
                    end_date = %s, location = %s, instructions = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            ''', (title, description, points, start_date, end_date, location, instructions, challenge_id))

            conn.commit()
            conn.close()

            flash(f'Sfida "{title}" modificata con successo', 'success')
            return redirect(url_for('game_prize.admin_dashboard'))

        except Exception as e:
            conn.rollback()
            conn.close()
            flash(f'Errore nella modifica sfida: {str(e)}', 'danger')

    # GET request
    cursor.execute('SELECT * FROM game_challenges WHERE id = %s', (challenge_id,))
    challenge = cursor.fetchone()
    conn.close()

    if not challenge:
        flash('Sfida non trovata', 'warning')
        return redirect(url_for('game_prize.admin_dashboard'))

    return render_template('game_prize/admin_edit_challenge.html', challenge=challenge)

@bp.route('/admin/clue/add/<int:challenge_id>', methods=['GET', 'POST'])
@login_required
@game_prize_password_required
def admin_add_clue(challenge_id):
    """Aggiungi un indizio a una sfida"""

    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        try:
            clue_number = int(request.form.get('clue_number'))
            clue_text = request.form.get('clue_text')
            revealed_date = request.form.get('revealed_date')

            cursor.execute('''
                INSERT INTO game_clues (challenge_id, clue_number, clue_text, revealed_date)
                VALUES (%s, %s, %s, %s)
            ''', (challenge_id, clue_number, clue_text, revealed_date))

            conn.commit()
            conn.close()

            flash('Indizio aggiunto con successo', 'success')
            return redirect(url_for('game_prize.admin_edit_challenge', challenge_id=challenge_id))

        except Exception as e:
            conn.rollback()
            conn.close()
            flash(f'Errore nell\'aggiunta indizio: {str(e)}', 'danger')

    # GET request
    cursor.execute('SELECT * FROM game_challenges WHERE id = %s', (challenge_id,))
    challenge = cursor.fetchone()
    conn.close()

    if not challenge:
        flash('Sfida non trovata', 'warning')
        return redirect(url_for('game_prize.admin_dashboard'))

    return render_template('game_prize/admin_add_clue.html', challenge=challenge)
