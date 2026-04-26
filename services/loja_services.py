from utils.json_utils import read_json, write_json
from datetime import datetime
def get_promocoes():
    proms = read_json("./data/promocao.json")
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

def set_promocoes(prom_data):
    write_json("./data/promocao.json", prom_data)

def comprar_pack_prom(id, pack_id):
    proms = read_json("./data/promocao.json")
    prom = next((p for p in proms if p["id"] == pack_id), None)
    personagens = read_json("./data/characters.json")
    cartas = []
    points = 0
    for i in prom['itens']:
        if i == "points":
            points = prom['was_points']
        else:
            carta = next((p for p in personagens if p["id"] == i), None)
            cartas.append(carta)

    all_progress = read_json("./data/progress.json")
    progress = next((u for u in all_progress if u["user_id"] == id), None)

    personagens_set = set(progress["personagens"])

    for c in cartas:
        cid = c["id"]
        if cid not in personagens_set:
            personagens_set.add(cid)
            progress["personagens"].append(cid)

    write_json("./data/progress.json", all_progress)
    prom["has_buy"].append(id)
    set_promocoes(proms)

    return prom['value'], points

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
        "has_buy": prom["has_buy"],
        "itens": prom["itens"],
        "was_points": prom["was_points"],
        "last_days": dias_restantes <= 3
    }
    return set
# Exemplo de promoção:
#  "nome": "Temporada 2: Apogeu",
#  "description": "Pacote especial com: Sierra, Soldado Churrasqueiro: 76, e Cassidy Salva-vidas!",
#  "value": 1000,
#  "last_days": true,
#  "buy_with_impeto": false,
#  "has_buy": [
#    1
#  ],
#  "itens": [
#    "sierra_comum",
#    "cassidy_salvavidas",
#    "soldado_76_churrasqueiro"
#  ]