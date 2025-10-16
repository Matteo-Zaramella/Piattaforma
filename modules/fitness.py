from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
import sqlite3
from datetime import datetime, timedelta
from modules.workout_templates import get_workout_template, get_all_workout_types

bp = Blueprint('fitness', __name__, url_prefix='/fitness')

def get_db():
    db = sqlite3.connect('piattaforma.db')
    db.row_factory = sqlite3.Row
    return db

@bp.route('/')
def index():
    """Dashboard fitness"""
    db = get_db()
    user_id = session['user_id']

    today = datetime.now().date()
    week_ago = today - timedelta(days=7)

    # Pasti recenti
    recent_meals = db.execute('''
        SELECT * FROM pasti
        WHERE user_id = ?
        ORDER BY data DESC, created_at DESC
        LIMIT 10
    ''', (user_id,)).fetchall()

    # Allenamenti recenti
    recent_workouts = db.execute('''
        SELECT * FROM allenamenti
        WHERE user_id = ?
        ORDER BY data DESC, created_at DESC
        LIMIT 10
    ''', (user_id,)).fetchall()

    # Statistiche settimana
    stats = {
        'workouts_week': db.execute('SELECT COUNT(DISTINCT data) as cnt FROM allenamenti WHERE user_id = ? AND data >= ?', (user_id, week_ago)).fetchone()['cnt'],
        'exercises_week': db.execute('SELECT COUNT(*) as cnt FROM allenamenti WHERE user_id = ? AND data >= ?', (user_id, week_ago)).fetchone()['cnt'],
        'meals_today': db.execute('SELECT COUNT(*) as cnt FROM pasti WHERE user_id = ? AND data = ?', (user_id, today)).fetchone()['cnt']
    }

    db.close()

    return render_template('fitness/index.html',
                         recent_meals=recent_meals,
                         recent_workouts=recent_workouts,
                         stats=stats)

# ===== PASTI =====

@bp.route('/pasti')
def pasti():
    """Lista pasti"""
    db = get_db()
    user_id = session['user_id']

    date_filter = request.args.get('data')

    if date_filter:
        pasti_list = db.execute('SELECT * FROM pasti WHERE user_id = ? AND data = ? ORDER BY created_at ASC', (user_id, date_filter)).fetchall()
    else:
        pasti_list = db.execute('SELECT * FROM pasti WHERE user_id = ? ORDER BY data DESC, created_at DESC LIMIT 50', (user_id,)).fetchall()

    db.close()

    return render_template('fitness/pasti.html', pasti=pasti_list, date_filter=date_filter)

@bp.route('/pasti/add', methods=['GET', 'POST'])
def add_pasto():
    """Aggiungi pasto"""
    if request.method == 'POST':
        db = get_db()
        user_id = session['user_id']

        data = {
            'user_id': user_id,
            'data': request.form.get('data', datetime.now().date().isoformat()),
            'tipo_pasto': request.form['tipo_pasto'],
            'descrizione': request.form['descrizione']
        }

        db.execute('''
            INSERT INTO pasti (user_id, data, tipo_pasto, descrizione)
            VALUES (?, ?, ?, ?)
        ''', (data['user_id'], data['data'], data['tipo_pasto'], data['descrizione']))

        db.commit()
        db.close()

        flash('Pasto aggiunto con successo!', 'success')
        return redirect(url_for('fitness.pasti'))

    return render_template('fitness/add_pasto.html')

@bp.route('/pasti/edit/<int:pasto_id>', methods=['GET', 'POST'])
def edit_pasto(pasto_id):
    """Modifica pasto"""
    db = get_db()
    user_id = session['user_id']

    if request.method == 'POST':
        data = {
            'data': request.form['data'],
            'tipo_pasto': request.form['tipo_pasto'],
            'descrizione': request.form['descrizione']
        }

        db.execute('''
            UPDATE pasti SET data = ?, tipo_pasto = ?, descrizione = ?
            WHERE id = ? AND user_id = ?
        ''', (data['data'], data['tipo_pasto'], data['descrizione'], pasto_id, user_id))

        db.commit()
        db.close()

        flash('Pasto aggiornato con successo!', 'success')
        return redirect(url_for('fitness.pasti'))

    pasto = db.execute('SELECT * FROM pasti WHERE id = ? AND user_id = ?', (pasto_id, user_id)).fetchone()
    db.close()

    if not pasto:
        flash('Pasto non trovato', 'error')
        return redirect(url_for('fitness.pasti'))

    return render_template('fitness/edit_pasto.html', pasto=pasto)

@bp.route('/pasti/delete/<int:pasto_id>', methods=['POST'])
def delete_pasto(pasto_id):
    """Elimina pasto"""
    db = get_db()
    user_id = session['user_id']

    db.execute('DELETE FROM pasti WHERE id = ? AND user_id = ?', (pasto_id, user_id))
    db.commit()
    db.close()

    flash('Pasto eliminato', 'success')
    return redirect(url_for('fitness.pasti'))

# ===== ALLENAMENTI =====

@bp.route('/allenamenti')
def allenamenti():
    """Lista allenamenti"""
    db = get_db()
    user_id = session['user_id']

    date_filter = request.args.get('data')

    if date_filter:
        allenamenti_list = db.execute('SELECT * FROM allenamenti WHERE user_id = ? AND data = ? ORDER BY created_at ASC', (user_id, date_filter)).fetchall()
    else:
        allenamenti_list = db.execute('SELECT * FROM allenamenti WHERE user_id = ? ORDER BY data DESC, created_at DESC LIMIT 100', (user_id,)).fetchall()

    db.close()

    return render_template('fitness/allenamenti.html', allenamenti=allenamenti_list, date_filter=date_filter)

@bp.route('/allenamenti/add', methods=['GET', 'POST'])
def add_allenamento():
    """Aggiungi allenamento"""
    if request.method == 'POST':
        db = get_db()
        user_id = session['user_id']

        data = {
            'user_id': user_id,
            'data': request.form.get('data', datetime.now().date().isoformat()),
            'esercizio': request.form['esercizio'],
            'ripetizioni': int(request.form['ripetizioni']) if request.form.get('ripetizioni') else None,
            'peso': float(request.form['peso']) if request.form.get('peso') else None,
            'note': request.form.get('note', '')
        }

        db.execute('''
            INSERT INTO allenamenti (user_id, data, esercizio, ripetizioni, peso, note)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (data['user_id'], data['data'], data['esercizio'], data['ripetizioni'], data['peso'], data['note']))

        db.commit()
        db.close()

        flash('Allenamento aggiunto con successo!', 'success')
        return redirect(url_for('fitness.allenamenti'))

    return render_template('fitness/add_allenamento.html')

@bp.route('/allenamenti/edit/<int:allenamento_id>', methods=['GET', 'POST'])
def edit_allenamento(allenamento_id):
    """Modifica allenamento"""
    db = get_db()
    user_id = session['user_id']

    if request.method == 'POST':
        data = {
            'data': request.form['data'],
            'esercizio': request.form['esercizio'],
            'ripetizioni': int(request.form['ripetizioni']) if request.form.get('ripetizioni') else None,
            'peso': float(request.form['peso']) if request.form.get('peso') else None,
            'note': request.form.get('note', '')
        }

        db.execute('''
            UPDATE allenamenti SET data = ?, esercizio = ?, ripetizioni = ?, peso = ?, note = ?
            WHERE id = ? AND user_id = ?
        ''', (data['data'], data['esercizio'], data['ripetizioni'], data['peso'], data['note'], allenamento_id, user_id))

        db.commit()
        db.close()

        flash('Allenamento aggiornato con successo!', 'success')
        return redirect(url_for('fitness.allenamenti'))

    allenamento = db.execute('SELECT * FROM allenamenti WHERE id = ? AND user_id = ?', (allenamento_id, user_id)).fetchone()
    db.close()

    if not allenamento:
        flash('Allenamento non trovato', 'error')
        return redirect(url_for('fitness.allenamenti'))

    return render_template('fitness/edit_allenamento.html', allenamento=allenamento)

@bp.route('/allenamenti/delete/<int:allenamento_id>', methods=['POST'])
def delete_allenamento(allenamento_id):
    """Elimina allenamento"""
    db = get_db()
    user_id = session['user_id']

    db.execute('DELETE FROM allenamenti WHERE id = ? AND user_id = ?', (allenamento_id, user_id))
    db.commit()
    db.close()

    flash('Allenamento eliminato', 'success')
    return redirect(url_for('fitness.allenamenti'))

# ===== STATISTICHE =====

@bp.route('/stats')
def stats():
    """Statistiche fitness"""
    db = get_db()
    user_id = session['user_id']

    # Allenamenti per mese
    workouts_by_month = db.execute('''
        SELECT strftime('%Y-%m', data) as month, COUNT(DISTINCT data) as days, COUNT(*) as exercises
        FROM allenamenti
        WHERE user_id = ?
        GROUP BY month
        ORDER BY month DESC
        LIMIT 12
    ''', (user_id,)).fetchall()

    # Esercizi più frequenti
    top_exercises = db.execute('''
        SELECT esercizio, COUNT(*) as count, AVG(peso) as avg_peso, MAX(peso) as max_peso
        FROM allenamenti
        WHERE user_id = ? AND peso IS NOT NULL
        GROUP BY esercizio
        ORDER BY count DESC
        LIMIT 10
    ''', (user_id,)).fetchall()

    # Progressi (ultimi record per esercizio)
    progress = db.execute('''
        SELECT esercizio, MAX(peso) as record_peso, MAX(ripetizioni) as record_rip
        FROM allenamenti
        WHERE user_id = ?
        GROUP BY esercizio
        ORDER BY esercizio
    ''', (user_id,)).fetchall()

    db.close()

    return render_template('fitness/stats.html',
                         workouts_by_month=workouts_by_month,
                         top_exercises=top_exercises,
                         progress=progress)

# ===== WORKOUT STRUTTURATI (SCHEDA ZARAMELLA) =====

@bp.route('/scheda-workout')
def scheda_workout():
    """Pagina selezione workout A/B/C"""
    workout_types = get_all_workout_types()

    # Ultimi workout completati
    db = get_db()
    user_id = session['user_id']

    recent_workouts = db.execute('''
        SELECT * FROM workout_sessions
        WHERE user_id = ?
        ORDER BY data DESC
        LIMIT 10
    ''', (user_id,)).fetchall()

    db.close()

    return render_template('fitness/scheda_workout.html',
                         workout_types=workout_types,
                         recent_workouts=recent_workouts)

@bp.route('/scheda-workout/start/<workout_type>')
def start_workout(workout_type):
    """Inizia un nuovo workout"""
    template = get_workout_template(workout_type)

    if not template:
        flash('Workout non trovato', 'error')
        return redirect(url_for('fitness.scheda_workout'))

    return render_template('fitness/workout_form.html',
                         workout_type=workout_type,
                         template=template,
                         data=datetime.now().date().isoformat())

@bp.route('/scheda-workout/save', methods=['POST'])
def save_workout():
    """Salva il workout completato"""
    db = get_db()
    user_id = session['user_id']

    workout_type = request.form['workout_type']
    data = request.form['data']

    # Crea session workout
    db.execute('''
        INSERT INTO workout_sessions (user_id, data, workout_type, completato)
        VALUES (?, ?, ?, 1)
    ''', (user_id, data, workout_type))

    session_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]

    # Salva ogni esercizio
    template = get_workout_template(workout_type)
    for idx, esercizio in enumerate(template['esercizi']):
        # Skip esercizi senza form (stretching, pause)
        if esercizio.get('skip_form'):
            continue

        nome_esercizio = esercizio['nome']

        # Salva ogni serie
        for serie_num, serie_rip in enumerate(esercizio['serie'], 1):
            peso_key = f'peso_{idx}_{serie_num}'
            rip_key = f'rip_{idx}_{serie_num}'

            peso = request.form.get(peso_key)
            ripetizioni = request.form.get(rip_key)

            # Solo se almeno uno dei due è compilato
            if peso or ripetizioni:
                db.execute('''
                    INSERT INTO workout_exercises (session_id, esercizio, serie_numero, ripetizioni, peso)
                    VALUES (?, ?, ?, ?, ?)
                ''', (session_id, nome_esercizio, serie_num,
                     int(ripetizioni) if ripetizioni else None,
                     float(peso) if peso else None))

    db.commit()
    db.close()

    flash(f'Workout {workout_type} completato con successo!', 'success')
    return redirect(url_for('fitness.scheda_workout'))

@bp.route('/scheda-workout/history')
def workout_history():
    """Storico workout strutturati"""
    db = get_db()
    user_id = session['user_id']

    # Ottieni tutte le sessioni
    sessions = db.execute('''
        SELECT * FROM workout_sessions
        WHERE user_id = ?
        ORDER BY data DESC
    ''', (user_id,)).fetchall()

    db.close()

    return render_template('fitness/workout_history.html', sessions=sessions)

@bp.route('/scheda-workout/detail/<int:session_id>')
def workout_detail(session_id):
    """Dettaglio workout completato"""
    db = get_db()
    user_id = session['user_id']

    # Ottieni sessione
    session_data = db.execute('''
        SELECT * FROM workout_sessions
        WHERE id = ? AND user_id = ?
    ''', (session_id, user_id)).fetchone()

    if not session_data:
        flash('Workout non trovato', 'error')
        db.close()
        return redirect(url_for('fitness.workout_history'))

    # Ottieni esercizi
    exercises = db.execute('''
        SELECT * FROM workout_exercises
        WHERE session_id = ?
        ORDER BY id
    ''', (session_id,)).fetchall()

    db.close()

    # Raggruppa per esercizio
    exercises_grouped = {}
    for ex in exercises:
        if ex['esercizio'] not in exercises_grouped:
            exercises_grouped[ex['esercizio']] = []
        exercises_grouped[ex['esercizio']].append(ex)

    return render_template('fitness/workout_detail.html',
                         session=session_data,
                         exercises_grouped=exercises_grouped)
