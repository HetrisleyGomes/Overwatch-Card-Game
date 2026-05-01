from datetime import datetime, timedelta

# Atualizar data ===========================================
def verify_date(user, evento = False):
    """Atualiza os pacotes diários verificando a última data de entrada
    
    Keyword arguments:
    - user: Usuário.
    - event: Caso haja um evento ativo.
    Return: Retorna o próprio usuário, e um aviso de mudança.
    """
    ultimo_login_str = user["ultimo_login"]
    hoje = datetime.now().date()
    ultimo_login = datetime.strptime(ultimo_login_str, "%Y-%m-%d").date()
    has_change = False
    if ultimo_login != hoje:
        user["ultimo_login"] = hoje.strftime("%Y-%m-%d")
        user["packs_diarios_abertos"] = 2
        user["has_already_get_daily_bonus"] = False

        ontem = hoje - timedelta(days=1)
        if ultimo_login == ontem:
            user["streak"] += 1
            user["pontos"] += int(user["streak"])
            if (user["streak"] % 7) == 0:
                get_streak_bonus(user)
        else:
            user["streak"] = 1

        if evento:
            user["packs_evento"] += 1
        else:
            if user["packs_evento"] >= 1:
                packs = user["packs_evento"]
                user["packs_evento"] = 0
                user["pontos"] = packs * 100
        has_change = True
    return user, has_change

def get_streak_bonus(user):
    """Recebe um bônus de login semanal
    Keyword arguments:
    - user: Usuário.
    Return: None, mas altera o usuário adicionando novos pacotes.
    """
    streak = user["streak"]
    semanas = streak / 7
    if semanas < 4:
        user["packs_comprados_comum"] += 4
    elif semanas < 8:
        user["packs_comprados_raro"] += 3
        user["impetos"] += 1
    else:
        user["packs_comprados_raro"] += 6
        user["impetos"] += 2


# XP e Nivel ===========================
def sum_xp(user, xp):
    """Calcula experiência e nivelamento
    Keyword arguments:
    - user: Usuário.
    - xp: Experiência ganha.
    Return: Usuário e um aviso de subida de nível
    """
    has_level_uped = False
    user["xp"] += xp
    
    while True:
        nivel_cap = 100 + (user["nivel"] * 50)

        if user["xp"] >= nivel_cap:
            user["xp"] -= nivel_cap
            user["nivel"] += 1
            user["pontos"] += nivel_cap
            user["impetos"] += 1
            level_up_pack(user, user["nivel"])
            has_level_uped = True
        else:
            break

    return (user, has_level_uped)

def level_up_pack(user, nivel):
    """Recebe um bônus de login semanal
    Keyword arguments:
    - user: Usuário.
    Return: None, mas altera o usuário adicionando novos pacotes.
    """
    if nivel % 2 == 0:
        user["packs_comprados_comum"] += 3
    else:
        user["packs_comprados_comum"] += 1
        user["packs_comprados_raro"] += 1