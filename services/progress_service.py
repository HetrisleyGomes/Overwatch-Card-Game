from flask import session
import json

from sql.controller.progress_controller import ProgressController
from sql.repositories.progress_repository import ProgressRepository

# REGISTRAR ============================================================
def registry_cards(conn, cartas, rarity, user):
    """Busca pelo registro do usuário no progress.json.
    
    Keyword arguments:
    cartas -- Conjunto de cartas para serem salvas.
    rarity -- Raridade do pacote.
    Return: None.
    """

    repo = ProgressRepository(conn)
    ctll = ProgressController(repo)
    
    pontos = 0
    xp = 0

    # Registra as cartas
    personagens_set = ctll.get_all_cards_id(user['id'])
    for c in cartas:
        cid = c["id"] if c.get("id") else c["carta_id"]
        if cid not in personagens_set:
            personagens_set.append(cid)
            ctll.set_card(user['id'], cid)
        else:
            pontos += rarity_convert(c["raridade"])
        
        xp += get_xp_calc(c['raridade'], pack_rarity=rarity)

    # Faz o controle dos pacotes
    if rarity == "comum":
        if user["packs_diarios_abertos"] > 0:
            if user["contador_packs_comuns"] < 6:
                user["contador_packs_comuns"] += 1
            user["packs_diarios_abertos"] -= 1
        elif user["packs_comprados_comum"] > 0:
            user["packs_comprados_comum"] -= 1
    elif rarity == "raro":
        if user["contador_packs_comuns"] >= 6:
            user["contador_packs_comuns"] = 0
        elif user["packs_comprados_raro"] > 0:
            user["packs_comprados_raro"] -= 1
    elif rarity == "radiante":
        user["packs_comprados_radiante"] -= 1
    elif rarity == "evento":
        user["packs_evento"] -= 1

    if user["nivel"] <= 5:
        pontos = int(pontos*2)
    elif user['nivel'] <=8:
        pontos = int(pontos * 1.5)
    user["pontos"] += pontos
    session["xp_obtido"] = xp
    session["pontos_obtidos"] = pontos

    return user

def rarity_convert(rarity):
    """Converte a raridade das cartas repetidas em um valor de pontos.
    
    Keyword arguments:
    rarity -- Raridade da carta.
    Return: Valor da raridade.
    """

    match rarity:
        case "comum":
            return 1
        case "incomum":
            return 2
        case "epico":
            return 3
        case "lendario":
            return 4
        case "ultra":
            return 5
        case "mitico":
            return 7
        case "especial":
            return 6
        
def get_xp_calc(rarity, pack_rarity):
    value = 0
    match rarity:
        case "comum":
            value = 1
        case "incomum":
            value = 2
        case "epico":
            value = 3
        case "lendario":
            value = 4
        case "ultra":
            value = 5
        case "mitico":
            value = 5
        case _:
            value = 1
    match pack_rarity:
        case "comum":
            return int(value * 1.5)
        case "raro":
            return value
        case "radiante":
            return int(value * 0.8)
        case "evento":
            return int(value * 1.5)
        case "none":
            return 0
 
def save_deck_progress(conn, deck_json):
    deck_ids = json.loads(deck_json)

    repo = ProgressRepository(conn)
    ctll = ProgressController(repo)

    user_id = session["user_id"]

    ctll.set_deck(user_id, deck_ids)

def get_deck(conn):
    repo = ProgressRepository(conn)
    ctll = ProgressController(repo)

    user_id = session["user_id"]
    deck_atual = ctll.get_deck(user_id)
    return deck_atual
    