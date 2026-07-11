from utils.json_utils import write_json, get_promocao, get_characters, get_vault_max
from datetime import datetime
from sql.controller.progress_controller import ProgressController
from sql.repositories.progress_repository import ProgressRepository
import random

def get_promocoes(lang):
    proms = get_promocao()
    hoje = datetime.now().date()
    hoje_md = (hoje.month, hoje.day)
    
    prom = []
    for p in proms:
        inicio = datetime.strptime(p["inicio"], "%m-%d")
        fim = datetime.strptime(p["fim"], "%m-%d")
        inicio_md = (inicio.month, inicio.day)
        fim_md = (fim.month, fim.day)
        if inicio_md <= hoje_md <= fim_md:
            prom_formated = format_promotion(p, lang)
            prom.append(prom_formated)
    if prom:
        return prom
    return None

def get_user_prom_logs(conn, user_id):
    repo = ProgressRepository(conn)
    ctll = ProgressController(repo)

    return ctll.get_user_prom(user_id)


def comprar_pack_prom(id, pack_id, conn):
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

    ctll.buy_big_pack(id, pack_id)
    return prom['value'], points, cartas, icon

def format_promotion(prom, lang):
    hoje = datetime.now().date()

    fim_parsed = datetime.strptime(prom["fim"], "%m-%d")
    fim = fim_parsed.replace(year=hoje.year).date()

    dias_restantes = (fim - hoje).days
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

def get_max_vault_infos():
    vaults = get_vault_max()
    hoje = datetime.now().date()
    hoje_md = (hoje.month, hoje.day)
    
    vault = False

    for v in vaults:
        inicio = datetime.strptime(v["inicio"], "%m-%d")
        fim = datetime.strptime(v["fim"], "%m-%d")
        inicio_md = (inicio.month, inicio.day)
        fim_md = (fim.month, fim.day)
        if inicio_md <= hoje_md <= fim_md:
            vault = v["fim"]

    return vault

def get_vault_data_format(vault_data):
    hoje = datetime.now().date()

    fim_parsed = datetime.strptime(vault_data, "%m-%d")
    fim = fim_parsed.replace(year=hoje.year).date()
    end_date = f"{fim.day}/{fim.month}"
    dias_restantes = (fim - hoje).days
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
        # 1. sortear raridade
        chances = pack["chance"][i]
        raridades = list(chances.keys())
        pesos = list(chances.values())
        raridade = random.choices(raridades, weights=pesos, k=1)[0]

        # 2. filtrar personagens dessa raridade
        possiveis = [p for p in personagens if p["raridade"] == raridade and p.get("evento") is None and p not in cartas]

        # 3. escolher personagem
        carta = random.choice(possiveis)

        cartas.append(carta['id'])

    return cartas

def buy_vault_item(conn, user_id, carta_id):
    repo = ProgressRepository(conn)
    ctll = ProgressController(repo)
    
    ctll.buy_vault(user_id, carta_id)