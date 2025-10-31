from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
from functools import wraps
from datetime import datetime
import json
import os

bp = Blueprint('game_prize', __name__, url_prefix='/game-prize')

# Determina se usare PostgreSQL o SQLite
USE_POSTGRES = os.getenv('DATABASE_URL') is not None

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

# Decorator per proteggere The Game con password
def game_prize_password_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('game_admin_authenticated', False):
            flash('Accesso negato. The Game è protetto da password.', 'danger')
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
    conn = get_db()
    cursor = conn.cursor()

    try:
        # Carica tutte le sfide con le loro date
        if USE_POSTGRES:
            from psycopg2.extras import RealDictCursor
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            placeholder = '%s'
        else:
            placeholder = '?'

        cursor.execute('''
            SELECT id, challenge_number, title, description, points,
                   start_date, end_date, location, instructions
            FROM game_challenges
            ORDER BY challenge_number ASC
        ''')
        challenges = cursor.fetchall()

        # Per ogni sfida, carica i suoi indizi
        challenges_with_clues = []
        for challenge in challenges:
            if USE_POSTGRES:
                challenge_id = challenge['id']
            else:
                challenge_id = challenge[0]

            cursor.execute(f'''
                SELECT id, challenge_id, clue_number, clue_text, revealed_date
                FROM game_clues
                WHERE challenge_id = {placeholder}
                ORDER BY clue_number ASC
            ''', (challenge_id,))
            clues = cursor.fetchall()

            # Converti in tuple per compatibilità con template
            if USE_POSTGRES:
                challenge_tuple = (challenge['id'], challenge['challenge_number'],
                                 challenge['title'], challenge['description'],
                                 challenge['points'], challenge['start_date'],
                                 challenge['end_date'], challenge['location'],
                                 challenge['instructions'])
                clues_list = [(c['id'], c['challenge_id'], c['clue_number'],
                              c['clue_text'], 0, c['revealed_date'])  # 0 punti placeholder
                             for c in clues]
            else:
                challenge_tuple = challenge
                clues_list = clues

            challenges_with_clues.append({
                'challenge': challenge_tuple,
                'clues': clues_list
            })

        cursor.close()
        conn.close()
        return render_template('game_prize/admin_welcome_new.html',
                             challenges_with_clues=challenges_with_clues)

    except Exception as e:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        print(f"Errore caricamento admin_welcome: {e}")
        import traceback
        traceback.print_exc()
        return render_template('game_prize/admin_welcome_new.html',
                             challenges_with_clues=[])

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
            max_participants = int(request.form.get('max_participants', 100))
            description = request.form.get('description', '')

            # Verifica se config esiste già
            cursor.execute('SELECT id FROM game_prize_config WHERE id = 1')
            if cursor.fetchone():
                cursor.execute('''
                    UPDATE game_prize_config
                    SET game_name = %s, start_date = %s, end_date = %s,
                        total_challenges = %s, max_participants = %s, description = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE id = 1
                ''', (game_name, start_date, end_date, total_challenges, max_participants, description))
            else:
                cursor.execute('''
                    INSERT INTO game_prize_config (game_name, start_date, end_date, total_challenges, max_participants, description)
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', (game_name, start_date, end_date, total_challenges, max_participants, description))

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

        # Per ogni sfida, recupera i suoi indizi
        challenges_with_clues = []
        for challenge in challenges:
            challenge_id = challenge[0]

            # Recupera gli indizi di questa sfida
            cursor.execute('''
                SELECT * FROM game_clues
                WHERE challenge_id = %s
                ORDER BY clue_number ASC
            ''', (challenge_id,))
            clues = cursor.fetchall()

            # Recupera le soluzioni degli indizi
            cursor.execute('''
                SELECT * FROM game_clue_solutions
                WHERE challenge_id = %s
                ORDER BY clue_number ASC
            ''', (challenge_id,))
            solutions = cursor.fetchall()

            challenges_with_clues.append({
                'challenge': challenge,
                'clues': clues,
                'solutions': solutions
            })

        # Statistiche
        cursor.execute('SELECT COUNT(DISTINCT user_id) FROM game_user_completions')
        total_players = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(DISTINCT challenge_id) FROM game_user_completions')
        total_completions = cursor.fetchone()[0]

        context = {
            'config': config,
            'challenges': challenges,
            'challenges_with_clues': challenges_with_clues,
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


# ============== NUOVO GESTORE SFIDE E INDIZI ==============

@bp.route('/admin/challenges-manager')
@login_required
@game_prize_password_required
def challenges_manager():
    """Gestore centralizzato per tutte le 12 sfide e indizi"""
    conn = get_db()
    cursor = conn.cursor()

    try:
        # Ottieni tutte le sfide
        cursor.execute('SELECT * FROM game_challenges ORDER BY challenge_number ASC')
        challenges = cursor.fetchall()
        challenges_count = len(challenges)

        # Conta indizi totali
        cursor.execute('SELECT COUNT(*) FROM game_clues')
        total_clues = cursor.fetchone()[0]

        # Crea un dizionario di sfide per accesso rapido
        challenges_dict = {}
        for challenge in challenges:
            challenges_dict[f'challenge_{challenge[1]}'] = {
                'id': challenge[0],
                'title': challenge[2],
                'description': challenge[3],
                'points': challenge[4],
                'location': challenge[7]
            }

        conn.close()

        return render_template(
            'game_prize/admin_challenges_manager.html',
            challenges_count=challenges_count,
            total_clues=total_clues,
            **challenges_dict
        )

    except Exception as e:
        conn.close()
        flash(f'Errore: {str(e)}', 'danger')
        return redirect(url_for('game_prize.admin_dashboard'))


@bp.route('/admin/save-challenge', methods=['POST'])
@login_required
@game_prize_password_required
def admin_save_challenge():
    """Salva una sfida nel database"""
    conn = get_db()
    cursor = conn.cursor()

    try:
        challenge_number = int(request.form.get('challenge_number'))
        title = request.form.get('title')
        description = request.form.get('description')
        points = int(request.form.get('points', 100))
        location = request.form.get('location', '')
        instructions = request.form.get('instructions', '')
        start_date = request.form.get('challenge_date')

        # Verifica se la sfida esiste già
        cursor.execute('SELECT id FROM game_challenges WHERE challenge_number = %s', (challenge_number,))
        existing = cursor.fetchone()

        if existing:
            # UPDATE
            cursor.execute('''
                UPDATE game_challenges
                SET title = %s, description = %s, points = %s,
                    location = %s, instructions = %s, start_date = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE challenge_number = %s
            ''', (title, description, points, location, instructions, start_date, challenge_number))
            flash(f'Sfida {challenge_number} aggiornata!', 'success')
        else:
            # INSERT
            cursor.execute('''
                INSERT INTO game_challenges
                (challenge_number, title, description, points, location, instructions, start_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (challenge_number, title, description, points, location, instructions, start_date))
            flash(f'Sfida {challenge_number} creata!', 'success')

        conn.commit()
        conn.close()
        return redirect(url_for('game_prize.challenges_manager'))

    except Exception as e:
        conn.rollback()
        conn.close()
        flash(f'Errore nel salvataggio: {str(e)}', 'danger')
        return redirect(url_for('game_prize.challenges_manager'))


@bp.route('/admin/save-clue', methods=['POST'])
@login_required
@game_prize_password_required
def admin_save_clue():
    """Salva un indizio nel database"""
    conn = get_db()
    cursor = conn.cursor()

    try:
        challenge_id = int(request.form.get('challenge_id'))
        clue_number = int(request.form.get('clue_number'))
        clue_text = request.form.get('clue_text')
        revealed_date = request.form.get('clue_date')

        # Verifica se l'indizio esiste già
        cursor.execute(
            'SELECT id FROM game_clues WHERE challenge_id = %s AND clue_number = %s',
            (challenge_id, clue_number)
        )
        existing = cursor.fetchone()

        if existing:
            # UPDATE
            cursor.execute('''
                UPDATE game_clues
                SET clue_text = %s, revealed_date = %s
                WHERE challenge_id = %s AND clue_number = %s
            ''', (clue_text, revealed_date, challenge_id, clue_number))
            flash(f'Indizio {clue_number} aggiornato!', 'success')
        else:
            # INSERT
            cursor.execute('''
                INSERT INTO game_clues (challenge_id, clue_number, clue_text, revealed_date)
                VALUES (%s, %s, %s, %s)
            ''', (challenge_id, clue_number, clue_text, revealed_date))
            flash(f'Indizio {clue_number} creato!', 'success')

        conn.commit()
        conn.close()
        return redirect(url_for('game_prize.challenges_manager'))

    except Exception as e:
        conn.rollback()
        conn.close()
        flash(f'Errore nel salvataggio indizio: {str(e)}', 'danger')
        return redirect(url_for('game_prize.challenges_manager'))


# ============== GAME PRIZE V2.0 - NUOVO SISTEMA ==============

def calculate_clue_points(position):
    """Calcola punti per indizio basato sulla posizione"""
    points_map = {
        1: 50, 2: 40, 3: 30, 4: 20, 5: 10, 6: 5
    }
    return points_map.get(position, 1)  # Dal 7° in poi: 1 punto


def calculate_challenge_points(position):
    """Calcola punti per sfida basato sulla posizione"""
    points_map = {
        1: 500, 2: 450, 3: 400, 4: 350, 5: 300,
        6: 250, 7: 200, 8: 150, 9: 100, 10: 50
    }
    return points_map.get(position, 5)  # Dall'11° in poi: 5 punti


def get_client_ip():
    """Ottiene IP del client (per logging anti-cheat)"""
    if request.environ.get('HTTP_X_FORWARDED_FOR'):
        return request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0]
    return request.environ.get('REMOTE_ADDR', 'unknown')


@bp.route('/api/validate-clue', methods=['POST'])
@login_required
def api_validate_clue():
    """
    Valida la parola inserita per un indizio.

    Richiede:
    - clue_id: ID dell'indizio
    - word: Parola da validare

    Ritorna:
    - success: True/False
    - message: Messaggio descrittivo
    - points: Punti guadagnati (se corretta)
    - position: Posizione nella classifica per questo indizio
    """
    conn = get_db()
    cursor = conn.cursor()
    user_id = session['user_id']

    try:
        clue_id = request.json.get('clue_id')
        submitted_word = request.json.get('word', '').strip()

        if not clue_id or not submitted_word:
            return jsonify({'success': False, 'message': 'Dati mancanti'}), 400

        # Ottieni participant_id per questo user_id
        cursor.execute('SELECT id FROM game_participants WHERE user_id = ?', (user_id,))
        participant = cursor.fetchone()

        if not participant:
            return jsonify({
                'success': False,
                'message': 'Devi registrarti al gioco prima di partecipare'
            }), 403

        participant_id = participant[0]

        # Verifica se l'utente ha già completato questo indizio
        cursor.execute('''
            SELECT id FROM game_clue_completions
            WHERE clue_id = ? AND participant_id = ?
        ''', (clue_id, participant_id))

        if cursor.fetchone():
            return jsonify({
                'success': False,
                'message': 'Hai già risolto questo indizio!'
            }), 400

        # Ottieni la soluzione corretta (case insensitive)
        cursor.execute('''
            SELECT solution_word FROM game_clue_solutions
            WHERE clue_id = ?
        ''', (clue_id,))

        solution = cursor.fetchone()

        if not solution:
            return jsonify({
                'success': False,
                'message': 'Indizio non trovato o soluzione non configurata'
            }), 404

        correct_word = solution[0].lower()
        submitted_lower = submitted_word.lower()

        # Log del tentativo (anti-cheat)
        is_correct = (submitted_lower == correct_word)
        cursor.execute('''
            INSERT INTO game_attempt_logs
            (participant_id, clue_id, attempted_word, is_correct, ip_address)
            VALUES (?, ?, ?, ?, ?)
        ''', (participant_id, clue_id, submitted_word, 1 if is_correct else 0, get_client_ip()))

        if not is_correct:
            conn.commit()
            conn.close()
            return jsonify({
                'success': False,
                'message': 'Parola errata. Riprova!'
            }), 200

        # Parola corretta! Calcola la posizione
        cursor.execute('''
            SELECT COUNT(*) + 1 FROM game_clue_completions
            WHERE clue_id = ?
        ''', (clue_id,))

        position = cursor.fetchone()[0]
        points = calculate_clue_points(position)

        # Registra il completamento
        cursor.execute('''
            INSERT INTO game_clue_completions
            (clue_id, participant_id, position, points_earned, submitted_word)
            VALUES (?, ?, ?, ?, ?)
        ''', (clue_id, participant_id, position, points, submitted_word))

        # Aggiorna i punteggi dettagliati
        cursor.execute('''
            SELECT points_from_clues, points_from_challenges
            FROM game_detailed_scores
            WHERE participant_id = ?
        ''', (participant_id,))

        scores = cursor.fetchone()

        if scores:
            new_clue_points = (scores[0] or 0) + points
            cursor.execute('''
                UPDATE game_detailed_scores
                SET points_from_clues = ?,
                    total_points = ? + ?,
                    last_updated = CURRENT_TIMESTAMP
                WHERE participant_id = ?
            ''', (new_clue_points, new_clue_points, scores[1] or 0, participant_id))
        else:
            cursor.execute('''
                INSERT INTO game_detailed_scores
                (participant_id, points_from_clues, points_from_challenges, total_points)
                VALUES (?, ?, 0, ?)
            ''', (participant_id, points, points))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': f'Corretto! Sei arrivato {position}°',
            'points': points,
            'position': position
        }), 200

    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'success': False, 'message': f'Errore: {str(e)}'}), 500


@bp.route('/api/register-participant', methods=['POST'])
@login_required
def api_register_participant():
    """
    Registra un partecipante al gioco assegnando un codice univoco.

    Richiede:
    - nome: Nome del partecipante
    - cognome: Cognome del partecipante
    - email: Email (opzionale)

    Ritorna:
    - success: True/False
    - unique_code: Codice univoco assegnato
    - message: Messaggio descrittivo
    """
    conn = get_db()
    cursor = conn.cursor()
    user_id = session['user_id']

    try:
        nome = request.json.get('nome', '').strip()
        cognome = request.json.get('cognome', '').strip()
        email = request.json.get('email', '').strip() or None

        if not nome or not cognome:
            return jsonify({
                'success': False,
                'message': 'Nome e cognome sono obbligatori'
            }), 400

        # Verifica se l'utente è già registrato
        cursor.execute('SELECT unique_code FROM game_participants WHERE user_id = ?', (user_id,))
        existing = cursor.fetchone()

        if existing:
            return jsonify({
                'success': True,
                'message': 'Sei già registrato al gioco!',
                'unique_code': existing[0]
            }), 200

        # Trova il primo codice univoco disponibile (non assegnato)
        cursor.execute('''
            SELECT unique_code FROM game_participants
            WHERE user_id IS NULL AND is_active = 1
            ORDER BY unique_code ASC
            LIMIT 1
        ''')

        available = cursor.fetchone()

        if not available:
            return jsonify({
                'success': False,
                'message': 'Nessun codice disponibile. Contatta l\'amministratore.'
            }), 503

        unique_code = available[0]

        # Assegna il codice all'utente
        cursor.execute('''
            UPDATE game_participants
            SET user_id = ?,
                email = ?,
                nome = ?,
                cognome = ?,
                registered_at = CURRENT_TIMESTAMP
            WHERE unique_code = ?
        ''', (user_id, email, nome, cognome, unique_code))

        # Crea anche un record nei punteggi dettagliati
        cursor.execute('''
            INSERT INTO game_detailed_scores (participant_id, points_from_clues, points_from_challenges, total_points)
            SELECT id, 0, 0, 0 FROM game_participants WHERE unique_code = ?
        ''', (unique_code,))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': f'Registrazione completata! Il tuo codice è {unique_code}',
            'unique_code': unique_code
        }), 200

    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'success': False, 'message': f'Errore: {str(e)}'}), 500


@bp.route('/api/add-clue-solution', methods=['POST'])
@login_required
@game_prize_password_required
def api_add_clue_solution():
    """
    ADMIN ONLY - Aggiunge la soluzione (parola corretta) per un indizio.

    Richiede:
    - clue_id: ID dell'indizio
    - solution_word: Parola corretta (salvata lowercase)
    - points_base: Punti base (default 50)
    """
    conn = get_db()
    cursor = conn.cursor()

    try:
        clue_id = request.json.get('clue_id')
        solution_word = request.json.get('solution_word', '').strip().lower()
        points_base = request.json.get('points_base', 50)

        if not clue_id or not solution_word:
            return jsonify({'success': False, 'message': 'Dati mancanti'}), 400

        # Verifica se esiste già una soluzione per questo indizio
        cursor.execute('SELECT id FROM game_clue_solutions WHERE clue_id = ?', (clue_id,))
        existing = cursor.fetchone()

        if existing:
            # Aggiorna
            cursor.execute('''
                UPDATE game_clue_solutions
                SET solution_word = ?, points_base = ?
                WHERE clue_id = ?
            ''', (solution_word, points_base, clue_id))
            message = 'Soluzione aggiornata'
        else:
            # Inserisci
            cursor.execute('''
                INSERT INTO game_clue_solutions (clue_id, solution_word, points_base)
                VALUES (?, ?, ?)
            ''', (clue_id, solution_word, points_base))
            message = 'Soluzione aggiunta'

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': message
        }), 200

    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'success': False, 'message': f'Errore: {str(e)}'}), 500
