-- ============================================================================
-- SCHEMA COMPLETO DATABASE PIATTAFORMA
-- Tutte le tabelle necessarie per l'applicazione
-- ============================================================================

-- 1. TABELLA USERS (già creata, ma verifichiamo)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. TABELLA PASTI
CREATE TABLE IF NOT EXISTS pasti (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    data DATE NOT NULL,
    tipo_pasto VARCHAR(50) NOT NULL,
    descrizione TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_pasti_user_date ON pasti(user_id, data);

-- 3. TABELLA ALLENAMENTI (legacy, per compatibilità)
CREATE TABLE IF NOT EXISTS allenamenti (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    data DATE NOT NULL,
    esercizio VARCHAR(100) NOT NULL,
    ripetizioni INTEGER,
    peso NUMERIC(5,2),
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_allenamenti_user_date ON allenamenti(user_id, data);

-- 4. TABELLA WORKOUT_SESSIONS (schede workout strutturate)
CREATE TABLE IF NOT EXISTS workout_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    workout_type VARCHAR(1) NOT NULL CHECK (workout_type IN ('A', 'B', 'C')),
    data DATE NOT NULL,
    completato BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_workout_sessions_user ON workout_sessions(user_id, data);

-- 5. TABELLA WORKOUT_EXERCISES (esercizi delle sessioni)
CREATE TABLE IF NOT EXISTS workout_exercises (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES workout_sessions(id) ON DELETE CASCADE,
    nome_esercizio VARCHAR(100) NOT NULL,
    esercizio VARCHAR(100),
    serie_numero INTEGER,
    ripetizioni INTEGER,
    peso NUMERIC(6,2),
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_workout_exercises_session ON workout_exercises(session_id);

-- 6. TABELLA WISHLIST
CREATE TABLE IF NOT EXISTS wishlist (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    titolo VARCHAR(200) NOT NULL,
    descrizione TEXT,
    prezzo NUMERIC(10,2),
    link VARCHAR(500),
    priorita VARCHAR(20) DEFAULT 'media' CHECK (priorita IN ('alta', 'media', 'bassa')),
    acquistato BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_wishlist_user ON wishlist(user_id);

-- 7. TABELLA SETTINGS
CREATE TABLE IF NOT EXISTS settings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    key VARCHAR(50) NOT NULL,
    value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, key)
);

CREATE INDEX IF NOT EXISTS idx_settings_user ON settings(user_id);

-- 8. Inserisci utente admin se non esiste
-- Password: la tua password hashata (devi cambiarla dopo)
INSERT INTO users (username, password, email)
VALUES ('admin', 'scrypt:32768:8:1$VGc3Z0ZmcWZxZm$9e8f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6', 'matteo.zaramella2002@gmail.com')
ON CONFLICT (username) DO NOTHING;

COMMIT;
