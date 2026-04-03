from utils.json_utils import read_json, write_json
from services.user_service import delete_events_packs
from datetime import datetime

def check_event_activation():
    eventos = read_json("./data/events.json")
    hoje = datetime.now()
    hoje_md = (hoje.month, hoje.day)

    for e in eventos:
        inicio = datetime.strptime(e["inicio"], "%m-%d")
        fim = datetime.strptime(e["fim"], "%m-%d")

        inicio_md = (inicio.month, inicio.day)
        fim_md = (fim.month, fim.day)
        if inicio_md <= hoje_md <= fim_md:
            ativar_evento(e["id"])
        elif e["ativo"]:
            delete_events_packs()
            desativar_evento(e["id"])

def get_eventos_ativos():
    eventos = read_json("./data/events.json")
    hoje = datetime.now().date()
    hoje_md = (hoje.month, hoje.day)

    ativos = None

    for e in eventos:
        if not e.get("ativo", True):
            continue

        inicio = datetime.strptime(e["inicio"], "%m-%d")
        fim = datetime.strptime(e["fim"], "%m-%d")

        inicio_md = (inicio.month, inicio.day)
        fim_md = (fim.month, fim.day)
        if inicio_md <= hoje_md <= fim_md:
            ativos = e

    return ativos

def ativar_evento(nome_evento):
    personagens = read_json("./data/characters.json")
    eventos = read_json("./data/events.json")

    evento = next((e for e in eventos if e["id"] == nome_evento), None)

    if evento:
        evento["ativo"] = True
        
    for p in personagens:
        if p.get("evento") == nome_evento:
            p["disponivel"] = True

    write_json("./data/events.json", eventos)
    write_json("./data/characters.json", personagens)

def desativar_evento(nome_evento):
    personagens = read_json("./data/characters.json")
    eventos = read_json("./data/events.json")

    evento = next((e for e in eventos if e["id"] == nome_evento), None)

    if evento:
        evento["ativo"] = False

    for p in personagens:
        if p.get("evento") == nome_evento:
            p["disponivel"] = False

    write_json("./data/events.json", eventos)
    write_json("./data/characters.json", personagens)