from utils.json_utils import read_json, write_json, get_events, get_characters
from datetime import datetime

def check_event_activation():
    eventos = get_events()
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
            desativar_evento(e["id"])

def get_eventos_ativos(lang):
    eventos = get_events()
    ativos = None

    for e in eventos:
        if not e.get("ativo", True):
            continue

        if e['ativo']:
            e_lang= e["lang"][lang]
            ativos = {
                "id": e["id"],
                "inicio": e["inicio"],
                "fim": e["fim"],
                "nome": e_lang["nome"],
                "description": e_lang["description"],
                "pack_description": e_lang["pack_description"]
            }

    return ativos

def ativar_evento(nome_evento):
    eventos = get_events()
    evento = next((e for e in eventos if e["id"] == nome_evento), None)

    if evento:
        evento["ativo"] = True

    write_json("./data/events.json", eventos)


def desativar_evento(nome_evento):
    eventos = get_events()
    evento = next((e for e in eventos if e["id"] == nome_evento), None)

    if evento:
        evento["ativo"] = False

    write_json("./data/events.json", eventos)

def has_eventos_ativos():
    eventos = get_events()

    for e in eventos:
        if e.get("ativo", True):
            return True
            
    return False

def get_last_log():
    logs = read_json("./logs.json")
    return logs[len(logs)-1]