-- ============================================================================
-- PRODUCTION FIXES - Game Prize V2.0 + Date Corrections
-- Da applicare su PostgreSQL Render
-- ============================================================================

-- 1. Drop e ricrea tabelle Game Prize se esistono (reset completo)
DROP TABLE IF EXISTS game_attempt_logs CASCADE;
DROP TABLE IF EXISTS game_clue_completions CASCADE;
DROP TABLE IF EXISTS game_clue_solutions CASCADE;
DROP TABLE IF EXISTS game_detailed_scores CASCADE;
DROP TABLE IF EXISTS game_participants CASCADE;
DROP TABLE IF EXISTS game_user_completions CASCADE;
DROP TABLE IF EXISTS game_user_scores CASCADE;
DROP TABLE IF EXISTS game_challenges CASCADE;
DROP TABLE IF EXISTS game_clues CASCADE;
DROP TABLE IF EXISTS game_prize_config CASCADE;

-- 2. Crea tabella partecipanti con codici univoci
CREATE TABLE game_participants (
    id SERIAL PRIMARY KEY,
    unique_code VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    nome VARCHAR(100),
    cognome VARCHAR(100),
    user_id INTEGER REFERENCES users(id),
    registered_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- 3. Crea tabella soluzioni indizi
CREATE TABLE game_clue_solutions (
    id SERIAL PRIMARY KEY,
    clue_id INTEGER,
    solution_word VARCHAR(255) NOT NULL,
    points_base INTEGER DEFAULT 50,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Crea tabella completamenti indizi
CREATE TABLE game_clue_completions (
    id SERIAL PRIMARY KEY,
    clue_id INTEGER,
    participant_id INTEGER REFERENCES game_participants(id) ON DELETE CASCADE,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    position INTEGER NOT NULL,
    points_earned INTEGER NOT NULL,
    submitted_word VARCHAR(255),
    UNIQUE(clue_id, participant_id)
);

-- 5. Crea tabella sfide
CREATE TABLE game_challenges (
    id SERIAL PRIMARY KEY,
    challenge_number INTEGER UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    points INTEGER DEFAULT 500,
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    location VARCHAR(255),
    instructions TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Crea tabella indizi
CREATE TABLE game_clues (
    id SERIAL PRIMARY KEY,
    challenge_id INTEGER REFERENCES game_challenges(id) ON DELETE CASCADE,
    clue_number INTEGER NOT NULL,
    clue_text TEXT,
    revealed_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. Crea tabella completamenti sfide utenti
CREATE TABLE game_user_completions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    challenge_id INTEGER REFERENCES game_challenges(id) ON DELETE CASCADE,
    completed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    position INTEGER,
    points_earned INTEGER,
    UNIQUE(user_id, challenge_id)
);

-- 8. Crea tabella punteggi utenti (legacy)
CREATE TABLE game_user_scores (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    challenge_id INTEGER REFERENCES game_challenges(id) ON DELETE CASCADE,
    points INTEGER DEFAULT 0,
    awarded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 9. Crea tabella configurazione gioco
CREATE TABLE game_prize_config (
    id SERIAL PRIMARY KEY,
    game_name VARCHAR(255) DEFAULT 'Game Prize 2026-2027',
    start_date DATE,
    end_date DATE,
    total_challenges INTEGER DEFAULT 13,
    max_participants INTEGER DEFAULT 100,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 10. Crea tabella punteggi dettagliati
CREATE TABLE game_detailed_scores (
    id SERIAL PRIMARY KEY,
    participant_id INTEGER REFERENCES game_participants(id) ON DELETE CASCADE,
    points_from_clues INTEGER DEFAULT 0,
    points_from_challenges INTEGER DEFAULT 0,
    total_points INTEGER GENERATED ALWAYS AS (points_from_clues + points_from_challenges) STORED,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 11. Crea tabella log tentativi (anti-cheat)
CREATE TABLE game_attempt_logs (
    id SERIAL PRIMARY KEY,
    participant_id INTEGER REFERENCES game_participants(id) ON DELETE CASCADE,
    clue_id INTEGER,
    challenge_id INTEGER REFERENCES game_challenges(id) ON DELETE CASCADE,
    attempted_word VARCHAR(255),
    is_correct BOOLEAN DEFAULT FALSE,
    attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45)
);

-- 12. Crea indici per performance
CREATE INDEX idx_clue_completions_clue ON game_clue_completions(clue_id);
CREATE INDEX idx_clue_completions_participant ON game_clue_completions(participant_id);
CREATE INDEX idx_clue_completions_position ON game_clue_completions(position);
CREATE INDEX idx_user_completions_position ON game_user_completions(position);
CREATE INDEX idx_attempt_logs_participant ON game_attempt_logs(participant_id);
CREATE INDEX idx_clue_solutions_clue ON game_clue_solutions(clue_id);

-- 13. Genera 100 codici univoci partecipanti
DO $$
DECLARE
    i INTEGER;
BEGIN
    FOR i IN 1..100 LOOP
        INSERT INTO game_participants (unique_code)
        VALUES ('GP2026-' || LPAD(i::TEXT, 4, '0'))
        ON CONFLICT (unique_code) DO NOTHING;
    END LOOP;
END $$;

-- 14. Inserisci configurazione gioco
INSERT INTO game_prize_config (id, game_name, start_date, end_date, total_challenges, max_participants, description)
VALUES (1, 'Game Prize 2026-2027', '2026-01-24', '2027-01-24', 13, 100,
        'Gioco a premi con 13 sfide mensili. Le sfide sono disponibili dalle 00:00 alle 23:59 del giorno indicato.')
ON CONFLICT (id) DO UPDATE
SET game_name = EXCLUDED.game_name,
    start_date = EXCLUDED.start_date,
    end_date = EXCLUDED.end_date,
    total_challenges = EXCLUDED.total_challenges,
    max_participants = EXCLUDED.max_participants,
    description = EXCLUDED.description,
    updated_at = CURRENT_TIMESTAMP;

-- 15. Inserisci 13 sfide con DATE CORRETTE (12 sabati + 1 domenica)
INSERT INTO game_challenges (challenge_number, title, description, points, start_date, end_date, location, instructions) VALUES
(1, 'Sfida 1 - Gennaio', 'Prima sfida del gioco', 500, '2026-01-24 00:00:00', '2026-01-24 23:59:59', 'Da definire', 'Le istruzioni verranno rivelate il giorno della sfida'),
(2, 'Sfida 2 - Febbraio', 'Seconda sfida del gioco', 500, '2026-02-21 00:00:00', '2026-02-21 23:59:59', 'Da definire', 'Le istruzioni verranno rivelate il giorno della sfida'),
(3, 'Sfida 3 - Marzo', 'Terza sfida del gioco', 500, '2026-03-21 00:00:00', '2026-03-21 23:59:59', 'Da definire', 'Le istruzioni verranno rivelate il giorno della sfida'),
(4, 'Sfida 4 - Aprile', 'Quarta sfida del gioco', 500, '2026-04-25 00:00:00', '2026-04-25 23:59:59', 'Da definire', 'Le istruzioni verranno rivelate il giorno della sfida'),
(5, 'Sfida 5 - Maggio', 'Quinta sfida del gioco', 500, '2026-05-23 00:00:00', '2026-05-23 23:59:59', 'Da definire', 'Le istruzioni verranno rivelate il giorno della sfida'),
(6, 'Sfida 6 - Giugno', 'Sesta sfida del gioco', 500, '2026-06-27 00:00:00', '2026-06-27 23:59:59', 'Da definire', 'Le istruzioni verranno rivelate il giorno della sfida'),
(7, 'Sfida 7 - Luglio', 'Settima sfida del gioco', 500, '2026-07-25 00:00:00', '2026-07-25 23:59:59', 'Da definire', 'Le istruzioni verranno rivelate il giorno della sfida'),
(8, 'Sfida 8 - Agosto', 'Ottava sfida del gioco', 500, '2026-08-22 00:00:00', '2026-08-22 23:59:59', 'Da definire', 'Le istruzioni verranno rivelate il giorno della sfida'),
(9, 'Sfida 9 - Settembre', 'Nona sfida del gioco', 500, '2026-09-26 00:00:00', '2026-09-26 23:59:59', 'Da definire', 'Le istruzioni verranno rivelate il giorno della sfida'),
(10, 'Sfida 10 - Ottobre', 'Decima sfida del gioco', 500, '2026-10-24 00:00:00', '2026-10-24 23:59:59', 'Da definire', 'Le istruzioni verranno rivelate il giorno della sfida'),
(11, 'Sfida 11 - Novembre', 'Undicesima sfida del gioco', 500, '2026-11-21 00:00:00', '2026-11-21 23:59:59', 'Da definire', 'Le istruzioni verranno rivelate il giorno della sfida'),
(12, 'Sfida 12 - Dicembre', 'Dodicesima sfida del gioco', 500, '2026-12-26 00:00:00', '2026-12-26 23:59:59', 'Da definire', 'Le istruzioni verranno rivelate il giorno della sfida'),
(13, 'SFIDA FINALE - Gennaio 2027', 'La sfida finale che determinerà il vincitore!', 1000, '2027-01-24 00:00:00', '2027-01-24 23:59:59', 'Da definire', 'Le istruzioni verranno rivelate il giorno della sfida finale')
ON CONFLICT (challenge_number) DO UPDATE
SET title = EXCLUDED.title,
    description = EXCLUDED.description,
    points = EXCLUDED.points,
    start_date = EXCLUDED.start_date,
    end_date = EXCLUDED.end_date,
    location = EXCLUDED.location,
    instructions = EXCLUDED.instructions,
    updated_at = CURRENT_TIMESTAMP;

COMMIT;

-- ============================================================================
-- VERIFICA DATE (tutte devono essere sabato tranne la 13 che è domenica)
-- ============================================================================
-- Sfida 1:  2026-01-24 (Sabato)
-- Sfida 2:  2026-02-21 (Sabato)
-- Sfida 3:  2026-03-21 (Sabato)
-- Sfida 4:  2026-04-25 (Sabato)
-- Sfida 5:  2026-05-23 (Sabato)
-- Sfida 6:  2026-06-27 (Sabato)
-- Sfida 7:  2026-07-25 (Sabato)
-- Sfida 8:  2026-08-22 (Sabato)
-- Sfida 9:  2026-09-26 (Sabato)
-- Sfida 10: 2026-10-24 (Sabato)
-- Sfida 11: 2026-11-21 (Sabato)
-- Sfida 12: 2026-12-26 (Sabato)
-- Sfida 13: 2027-01-24 (Domenica) - FINALE
-- ============================================================================
