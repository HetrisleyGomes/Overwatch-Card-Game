from utils.json_utils import read_json, get_events
from utils.date_utils import is_date_active

def get_active_events(lang):
    eventos = get_events()
    ativos = None

    for e in eventos:
        if is_date_active(e["inicio"], e["fim"]):
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

def is_theres_active_events():
    eventos = get_events()
    for e in eventos:
        if is_date_active(e["inicio"], e["fim"]):
            return True
    return False

def get_last_log():
    logs = read_json("./logs.json")
    return logs[len(logs)-1]