from utils.json_utils import write_json, get_promocao, get_characters
from datetime import datetime
from sql.controller.progress_controller import ProgressController
from sql.repositories.progress_repository import ProgressRepository

def get_promocoes():
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
            prom_formated = format_promotion(p)
            prom.append(prom_formated)
    if prom:
        return prom
    return False

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

    imgs = next((p for p in proms if p.get("icon")), None)
    repo = ProgressRepository(conn)
    ctll = ProgressController(repo)

    ctll.buy_big_pack(id, pack_id)
    return prom['value'], points, cartas, imgs

def format_promotion(prom):
    hoje = datetime.now().date()

    fim_parsed = datetime.strptime(prom["fim"], "%m-%d")
    fim = fim_parsed.replace(year=hoje.year).date()

    dias_restantes = (fim - hoje).days

    set = {
        "id": prom["id"],
        "nome": prom["nome"],
        "description": prom["description"],
        "value": prom["value"],
        "buy_with_impeto": prom["buy_with_impeto"],
        "inicio": prom["inicio"],
        "fim": prom["fim"],
        "itens": prom["itens"],
        "was_points": prom["was_points"],
        "last_days": dias_restantes <= 3
    }
    return set