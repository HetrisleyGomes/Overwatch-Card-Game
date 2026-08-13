from utils.json_utils import get_themes, get_promocao, get_characters, get_vault_max
from utils.date_utils import is_date_active, calculate_last_days, format_end_date
from sql.controller.progress_controller import ProgressController
from sql.repositories.progress_repository import ProgressRepository
import random

def get_promotion(lang):
    proms = get_promocao()
    prom = []
    for p in proms:
        if is_date_active(p["inicio"], p["fim"]):
            prom_formated = format_promotion(p, lang)
            prom.append(prom_formated)
    if prom:
        return prom
    return None

def get_user_infos(conn, user_id, info):
    repo = ProgressRepository(conn)
    ctll = ProgressController(repo)

    return ctll.get_user_info(user_id, info)

def buy_pack_promotion(user_id, pack_id, conn):
    proms = get_promocao()
    prom = next((p for p in proms if p["id"] == pack_id), None)
    personagens = get_characters()
    cartas = []
    points = 0
    for i in prom['itens']:
        if i == "points":
            points = prom['was_points']
        else:
            carta = next((p for p in personagens if p["id"] == i), None)
            cartas.append(carta)

    icon = next((p.get("icon") for p in proms if p.get("icon")), None)
    repo = ProgressRepository(conn)
    ctll = ProgressController(repo)

    ctll.buy_item(user_id, pack_id, 'promotion')
    return prom['value'], points, cartas, icon

def format_promotion(prom, lang):
    dias_restantes = calculate_last_days(prom["fim"])
    prom_lang = prom["lang"][lang]
    set = {
        "id": prom["id"],
        "nome": prom_lang["nome"],
        "description": prom_lang["description"],
        "value": prom["value"],
        "buy_with_impeto": prom["buy_with_impeto"],
        "inicio": prom["inicio"],
        "fim": prom["fim"],
        "itens": prom["itens"],
        "was_points": prom["was_points"],
        "last_days": dias_restantes <= 3
    }
    return set

def buy_theme(user_id, theme_id, conn):
    themes = get_themes()
    theme = next((p for p in themes if p["id"] == theme_id), None)

    repo = ProgressRepository(conn)
    ctll = ProgressController(repo)

    ctll.buy_item(user_id, theme_id, 'theme')
    return theme['price']

def get_max_vault_infos():
    vaults = get_vault_max()
    vault = False

    for v in vaults:
         if is_date_active(v["inicio"], v["fim"]):
            vault = v["fim"]

    return vault

def get_vault_data_format(vault_data):
    end_date = format_end_date(vault_data)
    dias_restantes = calculate_last_days(vault_data)
    return [end_date, dias_restantes]


def get_vault(conn, user_id, vault_atual):
    repo = ProgressRepository(conn)
    ctll = ProgressController(repo)
    
    return ctll.get_vault_cards_data(user_id, vault_atual)

def generate_vault(conn, user_id, vault_atual):
    repo = ProgressRepository(conn)
    ctll = ProgressController(repo)

    return ctll.generate_new_vault(user_id, vault_atual)

def get_new_vault():
    personagens = get_characters()
    pack = {
        "cartas_por_pack": 5,
        "chance": [
           { "mitico": 100 },
           { "mitico": 100 },
           { "mitico": 75, "legado": 25},
           { "legado": 100 },
           { "legado": 100 },
        ]
    }
    cartas = []

    for i in range(pack["cartas_por_pack"]):
        # sortear raridade
        chances = pack["chance"][i]
        raridades = list(chances.keys())
        pesos = list(chances.values())
        raridade = random.choices(raridades, weights=pesos, k=1)[0]

        # filtrar personagens dessa raridade
        possiveis = [p for p in personagens if p["raridade"] == raridade and p.get("evento") is None and p not in cartas]

        # escolher personagem
        carta = random.choice(possiveis)
        cartas.append(carta['id'])

    return cartas

def buy_vault_item(conn, user_id, carta_id):
    repo = ProgressRepository(conn)
    ctll = ProgressController(repo)
    
    ctll.buy_vault(user_id, carta_id)