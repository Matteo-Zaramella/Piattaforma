-- ============================================================================
-- GAME PRIZE V2.0 - SCHEMA COMPLETO
-- Sistema punteggi progressivi, codici univoci, validazione indizi
-- ============================================================================

-- 1. Tabella partecipanti (codici univoci pre-generati)
CREATE TABLE IF NOT EXISTS game_participants (
    id SERIAL PRIMARY KEY,
    unique_code VARCHAR(20) UNIQUE NOT NULL,  -- Es: GP2026-0001
    email VARCHAR(255) UNIQUE,                 -- NULL finché non si registra
    nome VARCHAR(100),
    cognome VARCHAR(100),
    user_id INTEGER REFERENCES users(id),      -- NULL finché non si registra
    registered_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- 2. Tabella soluzioni indizi (parole corrette)
CREATE TABLE IF NOT EXISTS game_clue_solutions (
    id SERIAL PRIMARY KEY,
    clue_id INTEGER REFERENCES game_clues(id) ON DELETE CASCADE,
    solution_word VARCHAR(255) NOT NULL,       -- Parola corretta (salvata lowercase)
    points_base INTEGER DEFAULT 50,            -- Punti base per il 1°
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Tabella completamenti indizi con posizione
CREATE TABLE IF NOT EXISTS game_clue_completions (
    id SERIAL PRIMARY KEY,
    clue_id INTEGER REFERENCES game_clues(id) ON DELETE CASCADE,
    participant_id INTEGER REFERENCES game_participants(id) ON DELETE CASCADE,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    position INTEGER NOT NULL,                 -- 1°, 2°, 3°...
    points_earned INTEGER NOT NULL,            -- Punti effettivi guadagnati
    submitted_word VARCHAR(255),               -- Parola inserita (per log)
    UNIQUE(clue_id, participant_id)           -- Un partecipante può risolvere un indizio 1 sola volta
);

-- 4. Modifica tabella completamenti sfide (aggiungi posizione)
ALTER TABLE game_user_completions
ADD COLUMN IF NOT EXISTS position INTEGER,
ADD COLUMN IF NOT EXISTS points_earned INTEGER;

-- 5. Tabella punteggi dettagliati (separazione indizi/sfide)
CREATE TABLE IF NOT EXISTS game_detailed_scores (
    id SERIAL PRIMARY KEY,
    participant_id INTEGER REFERENCES game_participants(id) ON DELETE CASCADE,
    points_from_clues INTEGER DEFAULT 0,
    points_from_challenges INTEGER DEFAULT 0,
    total_points INTEGER GENERATED ALWAYS AS (points_from_clues + points_from_challenges) STORED,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Tabella log tentativi (per sicurezza e anti-cheat)
CREATE TABLE IF NOT EXISTS game_attempt_logs (
    id SERIAL PRIMARY KEY,
    participant_id INTEGER REFERENCES game_participants(id) ON DELETE CASCADE,
    clue_id INTEGER REFERENCES game_clues(id) ON DELETE CASCADE,
    challenge_id INTEGER REFERENCES game_challenges(id) ON DELETE CASCADE,
    attempted_word VARCHAR(255),
    is_correct BOOLEAN DEFAULT FALSE,
    attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45)
);

-- 7. Indici per performance
CREATE INDEX IF NOT EXISTS idx_clue_completions_clue ON game_clue_completions(clue_id);
CREATE INDEX IF NOT EXISTS idx_clue_completions_participant ON game_clue_completions(participant_id);
CREATE INDEX IF NOT EXISTS idx_clue_completions_position ON game_clue_completions(position);
CREATE INDEX IF NOT EXISTS idx_user_completions_position ON game_user_completions(position);
CREATE INDEX IF NOT EXISTS idx_attempt_logs_participant ON game_attempt_logs(participant_id);

-- 8. Trigger per aggiornamento automatico punteggi
CREATE OR REPLACE FUNCTION update_participant_scores()
RETURNS TRIGGER AS $$
BEGIN
    -- Aggiorna punteggi dettagliati quando viene completato un indizio o sfida
    INSERT INTO game_detailed_scores (participant_id, points_from_clues, points_from_challenges)
    VALUES (
        NEW.participant_id,
        (SELECT COALESCE(SUM(points_earned), 0) FROM game_clue_completions WHERE participant_id = NEW.participant_id),
        (SELECT COALESCE(SUM(points_earned), 0) FROM game_user_completions WHERE user_id = (SELECT user_id FROM game_participants WHERE id = NEW.participant_id))
    )
    ON CONFLICT (participant_id) DO UPDATE
    SET points_from_clues = EXCLUDED.points_from_clues,
        points_from_challenges = EXCLUDED.points_from_challenges,
        last_updated = CURRENT_TIMESTAMP;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Applica trigger
CREATE TRIGGER trigger_update_clue_scores
AFTER INSERT ON game_clue_completions
FOR EACH ROW
EXECUTE FUNCTION update_participant_scores();

-- 9. Vista classifica completa (per query veloci)
CREATE OR REPLACE VIEW game_leaderboard AS
SELECT
    p.id,
    p.unique_code,
    p.nome,
    p.cognome,
    COALESCE(ds.points_from_clues, 0) as points_clues,
    COALESCE(ds.points_from_challenges, 0) as points_challenges,
    COALESCE(ds.total_points, 0) as total_points,
    COUNT(DISTINCT cc.clue_id) as clues_completed,
    COUNT(DISTINCT uc.challenge_id) as challenges_completed,
    RANK() OVER (ORDER BY COALESCE(ds.total_points, 0) DESC) as rank_position
FROM game_participants p
LEFT JOIN game_detailed_scores ds ON p.id = ds.participant_id
LEFT JOIN game_clue_completions cc ON p.id = cc.participant_id
LEFT JOIN game_user_completions uc ON p.user_id = uc.user_id
WHERE p.is_active = TRUE
GROUP BY p.id, p.unique_code, p.nome, p.cognome, ds.points_from_clues, ds.points_from_challenges, ds.total_points
ORDER BY total_points DESC;

-- 10. Funzione calcolo punti indizi (progressivo)
CREATE OR REPLACE FUNCTION calculate_clue_points(p_position INTEGER)
RETURNS INTEGER AS $$
BEGIN
    RETURN CASE
        WHEN p_position = 1 THEN 50
        WHEN p_position = 2 THEN 40
        WHEN p_position = 3 THEN 30
        WHEN p_position = 4 THEN 20
        WHEN p_position = 5 THEN 10
        WHEN p_position = 6 THEN 5
        ELSE 1
    END;
END;
$$ LANGUAGE plpgsql;

-- 11. Funzione calcolo punti sfide (progressivo)
CREATE OR REPLACE FUNCTION calculate_challenge_points(p_position INTEGER)
RETURNS INTEGER AS $$
BEGIN
    RETURN CASE
        WHEN p_position = 1 THEN 500
        WHEN p_position = 2 THEN 450
        WHEN p_position = 3 THEN 400
        WHEN p_position = 4 THEN 350
        WHEN p_position = 5 THEN 300
        WHEN p_position = 6 THEN 250
        WHEN p_position = 7 THEN 200
        WHEN p_position = 8 THEN 150
        WHEN p_position = 9 THEN 100
        WHEN p_position = 10 THEN 50
        ELSE 5
    END;
END;
$$ LANGUAGE plpgsql;

-- 12. Pre-generazione 100 codici univoci
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

COMMIT;
