
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
    packs_diarios_abertos INTEGER,
    contador_packs_comuns INTEGER,
    packs_comprados_comum INTEGER,
    packs_comprados_raro INTEGER,
    has_already_get_daily_bonus BOOL,
    packs_evento INTEGER
    );

CREATE TABLE IF NOT EXISTS "user_cards"(
  user_id INTEGER,
  card_id TEXT,
  FOREIGN KEY (user_id) REFERENCES "user"(id)
);
ALTER TABLE "user_cards" ADD PRIMARY KEY (user_id, card_id);

CREATE TABLE IF NOT EXISTS "user_sets"(
  user_id INTEGER,
  set_id TEXT,
  FOREIGN KEY (user_id) REFERENCES "user"(id)
);
ALTER TABLE "user_sets" ADD PRIMARY KEY (user_id, set_id);

CREATE TABLE IF NOT EXISTS "user_deck_cards"(
  user_id INTEGER,
  card_id TEXT,
  FOREIGN KEY (user_id) REFERENCES "user"(id)
);
ALTER TABLE "user_deck_cards" ADD PRIMARY KEY (user_id, card_id);

CREATE TABLE IF NOT EXISTS "user_icons"(
  user_id INTEGER,
  icon_id TEXT,
  FOREIGN KEY (user_id) REFERENCES "user"(id)
);
ALTER TABLE "user_icons" ADD PRIMARY KEY (user_id, icon_id)