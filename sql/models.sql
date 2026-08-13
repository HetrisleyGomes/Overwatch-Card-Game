
CREATE TABLE IF NOT EXISTS "user"(
    id SERIAL PRIMARY KEY, 
    nome TEXT NOT NULL,
    email TEXT,
    senha TEXT,
    pontos INTEGER,
    impetos INTEGER,
    xp INTEGER,
    nivel INTEGER,
    ultimo_login TEXT,
    streak INTEGER,
    profile_img TEXT,
    theme text,
    language VARCHAR(5),
    packs_diarios_abertos INTEGER,
    contador_packs_comuns INTEGER,
    packs_comprados_comum INTEGER,
    packs_comprados_raro INTEGER,
    has_already_get_daily_bonus BOOL,
    packs_evento INTEGER,
    );

CREATE TABLE IF NOT EXISTS "user_cards"(
  user_id INTEGER,
  card_id TEXT,
  PRIMARY KEY (user_id, card_id),
  FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS "user_sets"(
  user_id INTEGER,
  set_id TEXT,
  PRIMARY KEY (user_id, set_id),
  FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS "user_deck_cards"(
  user_id INTEGER,
  card_id TEXT,
  PRIMARY KEY (user_id, card_id),
  FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS "user_icons"(
  user_id INTEGER,
  icon_id TEXT,
  PRIMARY KEY (user_id, icon_id),
  FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS "user_info"(
  user_id INTEGER,
  info_id TEXT,
  info_type TEXT,
  PRIMARY KEY (user_id, info_id),
  FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS "user_vault"(
  user_id INTEGER,
  vault_id TEXT,
  card_id TEXT,
  has_purchased BOOL,
  PRIMARY KEY (user_id, card_id),
  FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE
);

