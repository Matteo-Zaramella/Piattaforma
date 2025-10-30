from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash, current_app, make_response
from datetime import datetime, timedelta
from modules.workout_templates import get_workout_template, get_all_workout_types
import csv
import io

# Importa utilities database dal modulo principale
import sys
import os

# Aggiungi il parent directory al path se necessario
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import db_utils
get_db = db_utils.get_db
execute_query = db_utils.execute_query
USE_POSTGRES = db_utils.USE_POSTGRES

bp = Blueprint('fitness', __name__, url_prefix='/fitness')

@bp.route('/')
def index():
    """Dashboard fitness"""
    conn = get_db()
    user_id = session['user_id']

    today = datetime.now().date()
    week_ago = today - timedelta(days=7)

    # Pasti recenti
    recent_meals = execute_query(conn, '''
        SELECT * FROM pasti
        WHERE user_id = ?
        ORDER BY data DESC, created_at DESC
        LIMIT 10
    ''', (user_id,), fetch_all=True)

    # Allenamenti recenti
    recent_workouts = execute_query(conn, '''
        SELECT * FROM allenamenti
        WHERE user_id = ?
        ORDER BY data DESC, created_at DESC
        LIMIT 10
    ''', (user_id,), fetch_all=True)

    # Statistiche settimana
    stats = {
        'workouts_week': execute_query(conn, 'SELECT COUNT(DISTINCT data) as cnt FROM allenamenti WHERE user_id = ? AND data >= ?', (user_id, week_ago), fetch_one=True)['cnt'],
        'exercises_week': execute_query(conn, 'SELECT COUNT(*) as cnt FROM allenamenti WHERE user_id = ? AND data >= ?', (user_id, week_ago), fetch_one=True)['cnt'],
        'meals_today': execute_query(conn, 'SELECT COUNT(*) as cnt FROM pasti WHERE user_id = ? AND data = ?', (user_id, today), fetch_one=True)['cnt']
    }

    conn.close()

    return render_template('fitness/index.html',
                         recent_meals=recent_meals,
                         recent_workouts=recent_workouts,
                         stats=stats)

# ===== PASTI =====

@bp.route('/pasti')
def pasti():
    """Lista pasti"""
    conn = get_db()
    user_id = session['user_id']

    date_filter = request.args.get('data')

    if date_filter:
        pasti_list = execute_query(conn, 'SELECT * FROM pasti WHERE user_id = ? AND data = ? ORDER BY created_at ASC', (user_id, date_filter), fetch_all=True)
    else:
        pasti_list = execute_query(conn, 'SELECT * FROM pasti WHERE user_id = ? ORDER BY data DESC, created_at DESC LIMIT 50', (user_id,), fetch_all=True)

    conn.close()

    return render_template('fitness/pasti.html', pasti=pasti_list, date_filter=date_filter)

@bp.route('/pasti/add', methods=['GET', 'POST'])
def add_pasto():
    """Aggiungi pasto"""
    if request.method == 'POST':
        conn = get_db()
        user_id = session['user_id']

        data = {
            'user_id': user_id,
            'data': request.form.get('data', datetime.now().date().isoformat()),
            'tipo_pasto': request.form['tipo_pasto'],
            'descrizione': request.form['descrizione']
        }

        execute_query(conn, '''
            INSERT INTO pasti (user_id, data, tipo_pasto, descrizione)
            VALUES (?, ?, ?, ?)
        ''', (data['user_id'], data['data'], data['tipo_pasto'], data['descrizione']))

        conn.commit()
        conn.close()

        flash('Pasto aggiunto con successo!', 'success')
        return redirect(url_for('fitness.pasti'))

    return render_template('fitness/add_pasto.html')

@bp.route('/pasti/edit/<int:pasto_id>', methods=['GET', 'POST'])
def edit_pasto(pasto_id):
    """Modifica pasto"""
    conn = get_db()
    user_id = session['user_id']

    if request.method == 'POST':
        data = {
            'data': request.form['data'],
            'tipo_pasto': request.form['tipo_pasto'],
            'descrizione': request.form['descrizione']
        }

        execute_query(conn, '''
            UPDATE pasti SET data = ?, tipo_pasto = ?, descrizione = ?
            WHERE id = ? AND user_id = ?
        ''', (data['data'], data['tipo_pasto'], data['descrizione'], pasto_id, user_id))

        conn.commit()
        conn.close()

        flash('Pasto aggiornato con successo!', 'success')
        return redirect(url_for('fitness.pasti'))

    pasto = execute_query(conn, 'SELECT * FROM pasti WHERE id = ? AND user_id = ?', (pasto_id, user_id), fetch_one=True)
    conn.close()

    if not pasto:
        flash('Pasto non trovato', 'error')
        return redirect(url_for('fitness.pasti'))

    return render_template('fitness/edit_pasto.html', pasto=pasto)

@bp.route('/pasti/delete/<int:pasto_id>', methods=['POST'])
def delete_pasto(pasto_id):
    """Elimina pasto"""
    conn = get_db()
    user_id = session['user_id']

    execute_query(conn, 'DELETE FROM pasti WHERE id = ? AND user_id = ?', (pasto_id, user_id))
    conn.commit()
    conn.close()

    flash('Pasto eliminato', 'success')
    return redirect(url_for('fitness.pasti'))

@bp.route('/pasti/export')
def export_pasti():
    """Esporta tutti i pasti in formato CSV"""
    conn = get_db()
    user_id = session['user_id']

    # Recupera tutti i pasti dell'utente
    pasti = execute_query(conn, '''
        SELECT data, tipo_pasto, descrizione, created_at
        FROM pasti
        WHERE user_id = ?
        ORDER BY data DESC, created_at ASC
    ''', (user_id,), fetch_all=True)

    conn.close()

    # Crea file CSV in memoria
    output = io.StringIO()
    writer = csv.writer(output)

    # Intestazioni CSV
    writer.writerow(['Data', 'Tipo Pasto', 'Descrizione', 'Data Inserimento'])

    # Dati
    for row in pasti:
        writer.writerow([
            row['data'],
            row['tipo_pasto'],
            row['descrizione'],
            row['created_at']
        ])

    # Prepara la risposta
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = f'attachment; filename=pasti_{datetime.now().strftime("%Y%m%d")}.csv'
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'

    return response

# ===== ALLENAMENTI =====

@bp.route('/allenamenti/nuovo')
def allenamento_choice():
    """Scelta tipo allenamento: libero o scheda"""
    return render_template('fitness/allenamento_choice.html')

@bp.route('/allenamenti')
def allenamenti():
    """Lista allenamenti"""
    conn = get_db()
    user_id = session['user_id']

    date_filter = request.args.get('data')

    if date_filter:
        allenamenti_list = execute_query(conn, 'SELECT * FROM allenamenti WHERE user_id = ? AND data = ? ORDER BY created_at ASC', (user_id, date_filter), fetch_all=True)
    else:
        allenamenti_list = execute_query(conn, 'SELECT * FROM allenamenti WHERE user_id = ? ORDER BY data DESC, created_at DESC LIMIT 100', (user_id,), fetch_all=True)

    conn.close()

    return render_template('fitness/allenamenti.html', allenamenti=allenamenti_list, date_filter=date_filter)

@bp.route('/allenamenti/add', methods=['GET', 'POST'])
def add_allenamento():
    """Aggiungi allenamento"""
    if request.method == 'POST':
        conn = get_db()
        user_id = session['user_id']

        data = {
            'user_id': user_id,
            'data': request.form.get('data', datetime.now().date().isoformat()),
            'esercizio': request.form['esercizio'],
            'ripetizioni': int(request.form['ripetizioni']) if request.form.get('ripetizioni') else None,
            'peso': float(request.form['peso']) if request.form.get('peso') else None,
            'note': request.form.get('note', '')
        }

        execute_query(conn, '''
            INSERT INTO allenamenti (user_id, data, esercizio, ripetizioni, peso, note)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (data['user_id'], data['data'], data['esercizio'], data['ripetizioni'], data['peso'], data['note']))

        conn.commit()
        conn.close()

        flash('Allenamento aggiunto con successo!', 'success')
        return redirect(url_for('fitness.allenamenti'))

    return render_template('fitness/add_allenamento.html')

@bp.route('/allenamenti/edit/<int:allenamento_id>', methods=['GET', 'POST'])
def edit_allenamento(allenamento_id):
    """Modifica allenamento"""
    conn = get_db()
    user_id = session['user_id']

    if request.method == 'POST':
        data = {
            'data': request.form['data'],
            'esercizio': request.form['esercizio'],
            'ripetizioni': int(request.form['ripetizioni']) if request.form.get('ripetizioni') else None,
            'peso': float(request.form['peso']) if request.form.get('peso') else None,
            'note': request.form.get('note', '')
        }

        execute_query(conn, '''
            UPDATE allenamenti SET data = ?, esercizio = ?, ripetizioni = ?, peso = ?, note = ?
            WHERE id = ? AND user_id = ?
        ''', (data['data'], data['esercizio'], data['ripetizioni'], data['peso'], data['note'], allenamento_id, user_id))

        conn.commit()
        conn.close()

        flash('Allenamento aggiornato con successo!', 'success')
        return redirect(url_for('fitness.allenamenti'))

    allenamento = execute_query(conn, 'SELECT * FROM allenamenti WHERE id = ? AND user_id = ?', (allenamento_id, user_id), fetch_one=True)
    conn.close()

    if not allenamento:
        flash('Allenamento non trovato', 'error')
        return redirect(url_for('fitness.allenamenti'))

    return render_template('fitness/edit_allenamento.html', allenamento=allenamento)

@bp.route('/allenamenti/delete/<int:allenamento_id>', methods=['POST'])
def delete_allenamento(allenamento_id):
    """Elimina allenamento"""
    conn = get_db()
    user_id = session['user_id']

    execute_query(conn, 'DELETE FROM allenamenti WHERE id = ? AND user_id = ?', (allenamento_id, user_id))
    conn.commit()
    conn.close()

    flash('Allenamento eliminato', 'success')
    return redirect(url_for('fitness.allenamenti'))

# ===== STATISTICHE =====

@bp.route('/stats')
def stats():
    """Statistiche fitness basate su workout sessions"""
    conn = get_db()
    user_id = session['user_id']

    # Workout per mese (da workout_sessions)
    if USE_POSTGRES:
        workouts_by_month = execute_query(conn, '''
            SELECT TO_CHAR(data, 'YYYY-MM') as month,
                   COUNT(DISTINCT data) as days,
                   COUNT(*) as exercises
            FROM workout_sessions
            WHERE user_id = ?
            GROUP BY TO_CHAR(data, 'YYYY-MM')
            ORDER BY month DESC
            LIMIT 12
        ''', (user_id,), fetch_all=True)
    else:
        workouts_by_month = execute_query(conn, '''
            SELECT strftime('%Y-%m', data) as month,
                   COUNT(DISTINCT data) as days,
                   COUNT(*) as exercises
            FROM workout_sessions
            WHERE user_id = ?
            GROUP BY month
            ORDER BY month DESC
            LIMIT 12
        ''', (user_id,), fetch_all=True)

    # Esercizi più frequenti (da workout_exercises)
    if USE_POSTGRES:
        top_exercises = execute_query(conn, '''
            SELECT we.nome_esercizio as esercizio,
                   COUNT(*) as count,
                   AVG(NULLIF(we.peso_s1, '')::NUMERIC) as avg_peso,
                   MAX(NULLIF(we.peso_s1, '')::NUMERIC) as max_peso
            FROM workout_exercises we
            JOIN workout_sessions ws ON we.session_id = ws.id
            WHERE ws.user_id = ? AND we.peso_s1 IS NOT NULL AND we.peso_s1 != ''
            GROUP BY we.nome_esercizio
            ORDER BY count DESC
            LIMIT 10
        ''', (user_id,), fetch_all=True)
    else:
        top_exercises = execute_query(conn, '''
            SELECT we.nome_esercizio as esercizio,
                   COUNT(*) as count,
                   AVG(CAST(we.peso_s1 AS REAL)) as avg_peso,
                   MAX(CAST(we.peso_s1 AS REAL)) as max_peso
            FROM workout_exercises we
            JOIN workout_sessions ws ON we.session_id = ws.id
            WHERE ws.user_id = ? AND we.peso_s1 IS NOT NULL AND we.peso_s1 != ''
            GROUP BY we.nome_esercizio
            ORDER BY count DESC
            LIMIT 10
        ''', (user_id,), fetch_all=True)

    # Progressi (record per esercizio)
    if USE_POSTGRES:
        progress = execute_query(conn, '''
            SELECT we.nome_esercizio as esercizio,
                   MAX(NULLIF(we.peso_s1, '')::NUMERIC) as record_peso,
                   MAX(NULLIF(we.rip_s1, '')::INTEGER) as record_rip
            FROM workout_exercises we
            JOIN workout_sessions ws ON we.session_id = ws.id
            WHERE ws.user_id = ?
            GROUP BY we.nome_esercizio
            ORDER BY we.nome_esercizio
        ''', (user_id,), fetch_all=True)
    else:
        progress = execute_query(conn, '''
            SELECT we.nome_esercizio as esercizio,
                   MAX(CAST(we.peso_s1 AS REAL)) as record_peso,
                   MAX(CAST(we.rip_s1 AS INTEGER)) as record_rip
            FROM workout_exercises we
            JOIN workout_sessions ws ON we.session_id = ws.id
            WHERE ws.user_id = ?
            GROUP BY we.nome_esercizio
            ORDER BY we.nome_esercizio
        ''', (user_id,), fetch_all=True)

    conn.close()

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
    conn = get_db()
    user_id = session['user_id']

    recent_workouts = execute_query(conn, '''
        SELECT * FROM workout_sessions
        WHERE user_id = ?
        ORDER BY data DESC
        LIMIT 10
    ''', (user_id,), fetch_all=True)

    conn.close()

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
    conn = get_db()
    user_id = session['user_id']

    workout_type = request.form['workout_type']
    data = request.form['data']

    # Crea session workout
    if USE_POSTGRES:
        result = execute_query(conn, '''
            INSERT INTO workout_sessions (user_id, data, workout_type, completato)
            VALUES (?, ?, ?, TRUE)
            RETURNING id
        ''', (user_id, data, workout_type), fetch_one=True)
        session_id = result['id']
    else:
        execute_query(conn, '''
            INSERT INTO workout_sessions (user_id, data, workout_type, completato)
            VALUES (?, ?, ?, 1)
        ''', (user_id, data, workout_type))
        session_id = execute_query(conn, 'SELECT last_insert_rowid()', fetch_one=True)[0]

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
                execute_query(conn, '''
                    INSERT INTO workout_exercises (session_id, esercizio, serie_numero, ripetizioni, peso)
                    VALUES (?, ?, ?, ?, ?)
                ''', (session_id, nome_esercizio, serie_num,
                     int(ripetizioni) if ripetizioni else None,
                     float(peso) if peso else None))

    conn.commit()
    conn.close()

    flash(f'Workout {workout_type} completato con successo!', 'success')
    return redirect(url_for('fitness.scheda_workout'))

@bp.route('/scheda-workout/history')
def workout_history():
    """Storico workout strutturati"""
    conn = get_db()
    user_id = session['user_id']

    # Ottieni tutte le sessioni
    sessions = execute_query(conn, '''
        SELECT * FROM workout_sessions
        WHERE user_id = ?
        ORDER BY data DESC
    ''', (user_id,), fetch_all=True)

    conn.close()

    return render_template('fitness/workout_history.html', sessions=sessions)

@bp.route('/scheda-workout/detail/<int:session_id>')
def workout_detail(session_id):
    """Dettaglio workout completato"""
    conn = get_db()
    user_id = session['user_id']

    # Ottieni sessione
    session_data = execute_query(conn, '''
        SELECT * FROM workout_sessions
        WHERE id = ? AND user_id = ?
    ''', (session_id, user_id), fetch_one=True)

    if not session_data:
        flash('Workout non trovato', 'error')
        conn.close()
        return redirect(url_for('fitness.workout_history'))

    # Ottieni esercizi
    exercises = execute_query(conn, '''
        SELECT * FROM workout_exercises
        WHERE session_id = ?
        ORDER BY id
    ''', (session_id,), fetch_all=True)

    conn.close()

    # Raggruppa per esercizio
    exercises_grouped = {}
    for ex in exercises:
        if ex['esercizio'] not in exercises_grouped:
            exercises_grouped[ex['esercizio']] = []
        exercises_grouped[ex['esercizio']].append(ex)

    return render_template('fitness/workout_detail.html',
                         session=session_data,
                         exercises_grouped=exercises_grouped)

@bp.route('/scheda-workout/delete/<int:session_id>', methods=['POST'])
def delete_workout(session_id):
    """Elimina una sessione di workout"""
    conn = get_db()
    user_id = session['user_id']

    # Verifica che l'utente possiede il workout
    workout = execute_query(conn, '''
        SELECT id FROM workout_sessions
        WHERE id = ? AND user_id = ?
    ''', (session_id, user_id), fetch_one=True)

    if not workout:
        flash('Workout non trovato', 'error')
        conn.close()
        return redirect(url_for('fitness.workout_history'))

    # Elimina gli esercizi associati
    execute_query(conn, '''
        DELETE FROM workout_exercises
        WHERE session_id = ?
    ''', (session_id,))

    # Elimina la sessione
    execute_query(conn, '''
        DELETE FROM workout_sessions
        WHERE id = ? AND user_id = ?
    ''', (session_id, user_id))

    conn.commit()
    conn.close()

    flash('Workout eliminato', 'success')
    return redirect(url_for('fitness.workout_history'))

@bp.route('/allenamenti/export')
def export_allenamenti():
    """Esporta tutti gli allenamenti in formato CSV"""
    conn = get_db()
    user_id = session['user_id']

    # Recupera tutti gli allenamenti dell'utente
    allenamenti = execute_query(conn, '''
        SELECT data, esercizio, ripetizioni, peso, note, created_at
        FROM allenamenti
        WHERE user_id = ?
        ORDER BY data DESC, created_at ASC
    ''', (user_id,), fetch_all=True)

    conn.close()

    # Crea file CSV in memoria
    output = io.StringIO()
    writer = csv.writer(output)

    # Intestazioni CSV
    writer.writerow(['Data', 'Esercizio', 'Ripetizioni', 'Peso (kg)', 'Note', 'Data Inserimento'])

    # Dati
    for row in allenamenti:
        writer.writerow([
            row['data'],
            row['esercizio'],
            row['ripetizioni'] or '',
            row['peso'] or '',
            row['note'] or '',
            row['created_at']
        ])

    # Prepara la risposta
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = f'attachment; filename=allenamenti_{datetime.now().strftime("%Y%m%d")}.csv'
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'

    return response

@bp.route('/workout/export')
def export_workout_sessions():
    """Esporta le sessioni di workout strutturati in formato CSV"""
    conn = get_db()
    user_id = session['user_id']

    # Recupera tutte le sessioni workout con i relativi esercizi
    workout_sessions = execute_query(conn, '''
        SELECT ws.id, ws.data, ws.workout_type, ws.completato, ws.created_at
        FROM workout_sessions ws
        WHERE ws.user_id = ?
        ORDER BY ws.data DESC
    ''', (user_id,), fetch_all=True)

    # Crea file CSV in memoria
    output = io.StringIO()
    writer = csv.writer(output)

    # Intestazioni CSV
    writer.writerow(['Data', 'Tipo Workout', 'Completato', 'Esercizio', 'Serie', 'Ripetizioni', 'Peso (kg)', 'Note'])

    # Per ogni sessione, recupera gli esercizi
    for ws in workout_sessions:
        exercises = execute_query(conn, '''
            SELECT esercizio, serie_numero, ripetizioni, peso, note
            FROM workout_exercises
            WHERE session_id = ?
            ORDER BY serie_numero ASC
        ''', (ws['id'],), fetch_all=True)

        if exercises:
            for i, ex in enumerate(exercises):
                writer.writerow([
                    ws['data'] if i == 0 else '',
                    ws['workout_type'] if i == 0 else '',
                    'Sì' if ws['completato'] else 'No' if i == 0 else '',
                    ex['esercizio'],
                    ex['serie_numero'],
                    ex['ripetizioni'] or '',
                    ex['peso'] or '',
                    ex['note'] or ''
                ])
        else:
            # Sessione senza esercizi
            writer.writerow([
                ws['data'],
                ws['workout_type'],
                'Sì' if ws['completato'] else 'No',
                '',
                '',
                '',
                '',
                ''
            ])

    conn.close()

    # Prepara la risposta
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = f'attachment; filename=workout_sessions_{datetime.now().strftime("%Y%m%d")}.csv'
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'

    return response
