from utils.json_utils import read_json, write_json
from flask import session
from datetime import datetime, timedelta

def criar_usuario(nome, email, senha, has_event):
    """Cria um registro de usuário novo caso não exista.
    
    Keyword arguments:
    nome -- Nome do usuário.
    Return: Retorna o id do usuário criado.
    """
    usuarios = carregar_usuarios()
    data = datetime.now().strftime("%Y-%m-%d")
        
    novo_usuario = {
        "id": len(usuarios) + 1,
        "nome": nome,
        "email": email,
        "senha": senha,
        "pontos": 0,
        "impetos": 0,
        "xp": 0,
        "nivel": 1,
        "ultimo_login": data,
        "streak": 1,
        "profile_img": "logo.png",
        "packs_diarios_abertos": 2,
        "contador_packs_comuns": 0,
        "packs_comprados_comum": 0,
        "packs_comprados_raro": 0,
        "has_already_get_daily_bonus": False,
        "packs_evento": has_event
    }

    criar_inventory(novo_usuario["id"])

    usuarios.append(novo_usuario)

    salvar_usuarios(usuarios)

    return novo_usuario["id"]

def carregar_usuarios():
    """Lê as informações de user.json.
    
    Keyword arguments:
    Return: Informações lidas.
    """
    
    return read_json("./data/user.json")
    
def salvar_usuarios(usuarios):
    """Salva as informações do usuário.
    
    Keyword arguments:
    usuarios -- Todos os usários de user.json.
    Return: None.
    """
    
    write_json("./data/user.json", usuarios)

# Atualizar data ===========================================
def verify_date(usuarios, user, evento = False):
    """Atualiza os pacotes diários verificando a última data de entrada
    
    Keyword arguments:
    user -- Informações do usuário.
    Return: None.
    """
    
    ultimo_login_str = user["ultimo_login"]
    hoje = datetime.now().date()
    ultimo_login = datetime.strptime(ultimo_login_str, "%Y-%m-%d").date()

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

        salvar_usuarios(usuarios)

def get_streak_bonus(user):
    streak = user["streak"]
    semanas = streak / 7
    if semanas < 4:
        user["packs_comprados_comum"] += 4
    elif semanas < 8:
        user["packs_comprados_raro"] += 3
    else:
        user["packs_comprados_raro"] += 6


# XP e Nivel ===========================
def sum_xp(id, xp):
    usuarios = carregar_usuarios()
    user = next((u for u in usuarios if u["id"] == id), None)

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

    salvar_usuarios(usuarios)
    return (user["xp"], user["nivel"], has_level_uped)

def level_up_pack(user, nivel):
    if nivel % 2 == 0:
        user["packs_comprados_comum"] += 3
    else:
        user["packs_comprados_comum"] += 1
        user["packs_comprados_raro"] += 1

# Remove pacotes de evento
def delete_events_packs():
    """Remove os packs de evento acumulados e os converte em pontos.

    Return: None
    """
    
    usuarios = carregar_usuarios()
    user = next((u for u in usuarios if u["id"] == session["usuario_id"]), None)

    packs = user["packs_evento"]
    user["packs_evento"] = 0
    user["pontos"] = packs * 100

    salvar_usuarios(usuarios)


# INVENTÁRIOS ==================================================
def get_img_logos():
    imgs = read_json("./data/icons.json")
    return imgs

def user_get_inventory(user_id):
    icons = read_json("./data/icons.json")
    inventory = read_json("./data/inventory.json")
    user_inv = next((i for i in inventory if i["user_id"] == user_id), None)
    icons_user = []

    for icon in icons:
        possui = icon["id"] in user_inv["icons"]
        icons_user.append({
            **icon,
            "possui": possui
        })
    return icons_user

def icon_view(id, nivel, event):
    icons = read_json("./data/icons.json")
    inventory = read_json("./data/inventory.json")
    user_inv = next((i for i in inventory if i["user_id"] == id), None)
    all_progress = read_json("./data/progress.json")
    progress = next((u for u in all_progress if u["user_id"] == id))

    result = []

    for icon in icons:
        possui = icon["id"] in user_inv["icons"]
        unlock = icon.get("unlock",{"type":"free"})
        disponivel = False

        if unlock["type"] == "free" or unlock["type"] == "purchase":
            disponivel = True
        elif unlock["type"] == "set":
            if unlock["value"] in progress["sets_completos"]:
                disponivel = True
        elif unlock["type"] == "event":
            if event == unlock["value"]:
                disponivel = True
        elif unlock["type"] == "nivel":
            if unlock["value"] <= nivel:
                disponivel = True

        result.append({
            **icon,
            "possui": possui,
            "disponivel": disponivel
        })

    return result

def criar_inventory(id):
    inventory = read_json("./data/inventory.json")
    inv = {
        "user_id": id,
        "icons": [1, 2]
    }
    inventory.append(inv)
    write_json("./data/inventory.json", inventory)

def get_new_img(user_id, img_id):
    inventory = read_json("./data/inventory.json")
    user_inv = next((i for i in inventory if i["user_id"] == user_id), None)
    user_inv["icons"].append(img_id)
    write_json("./data/inventory.json", inventory)

