from .user_service import carregar_usuarios, salvar_usuarios
from utils.json_utils import read_json, write_json
from flask import session
import json

# REGISTRAR ============================================================
def registry_cards(cartas, rarity):
    """Busca pelo registro do usuário no progress.json.
    
    Keyword arguments:
    cartas -- Conjunto de cartas para serem salvas.
    rarity -- Raridade do pacote.
    Return: None.
    """
    
    all_progress = read_json("./data/progress.json")

    usuario_progress = next((u for u in all_progress if u["user_id"] == session['usuario_id']), None)

    if usuario_progress is None:
        usuario_progress = make_new_progress(all_progress)
    
    set_cards(usuario_progress, cartas, rarity)

    write_json("./data/progress.json", all_progress)

def set_cards(progress, cartas, rarity):
    """Salva cada uma das cartas ganhas em seu registro no progress.json, e faz controle dos pacotes e pontos no user.json.
    
    Keyword arguments:
    progress -- Representa o registro do usuário.
    cartas -- Conjunto de cartas para serem salvas.
    rarity -- Raridade do pacote.
    Return: None.
    """
    
    usuarios = carregar_usuarios()
    user = next((u for u in usuarios if u["id"] == session["usuario_id"]), None)
    pontos = 0
    xp = 0

    # Registra as cartas
    personagens_set = set(progress["personagens"])

    for c in cartas:
        cid = c["id"]

        if cid not in personagens_set:
            personagens_set.add(cid)
            progress["personagens"].append(cid)
        else:
            pontos += rarity_convert(c["raridade"])
        
        xp += get_xp_calc(c['raridade'], pack_rarity=rarity)
    
    # Faz o controle dos pacotes
    if rarity == "comum":
        if user["packs_diarios_abertos"] > 0:
            if user["contador_packs_comuns"] < 10:
                user["contador_packs_comuns"] += 1
            user["packs_diarios_abertos"] -= 1
        elif user["packs_comprados_comum"] > 0:
            user["packs_comprados_comum"] -= 1
    elif rarity == "raro":
        if user["contador_packs_comuns"] == 10:
            user["contador_packs_comuns"] = 0
        elif user["packs_comprados_raro"] > 0:
            user["packs_comprados_raro"] -= 1
    elif rarity == "especial":
        user["packs_evento"] -= 1
        pass
    if user["nivel"] <= 5:
        pontos = int(pontos*2)
    elif user['nivel'] <=8:
        pontos = int(pontos * 1.5)
    user["pontos"] += pontos
    session["xp_obtido"] = xp
    session["pontos_obtidos"] = pontos
    salvar_usuarios(usuarios)

def make_new_progress(all_progress):
    """Cria um registro de usuário caso não tenha.
    
    Keyword arguments:
    all_progress -- Representa o json responsável por manter todos os dados.
    Return: Retorna o registro de usuário criado.
    """
    
    novo_progress = {
    "user_id": session["usuario_id"],
    "personagens": [],
    "sets_completos": [],
    "deck": []
    }
    all_progress.append(novo_progress)
    return novo_progress

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
            return 4
        case "lendario":
            return 6
        case "mitico":
            return 10
        case "especial":
            return 10
        
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
        case "mitico":
            value = 5
    match pack_rarity:
        case "comum":
            return int(value * 1.5)
        case "raro":
            return value
        case "especial":
            return int(value * 1.5)

def save_deck_progress(deck_json):
    deck_ids = json.loads(deck_json)
    # buscar usuário
    progress_list = read_json("./data/progress.json")
    user_progress = next((p for p in progress_list if p["user_id"] == session["usuario_id"]), None)

    # garantir que existe lista
    if "deck" not in user_progress:
        user_progress["deck"] = []
    
    user_progress["deck"] = deck_ids
    write_json("./data/progress.json", progress_list)

def get_deck():
    progress_list = read_json("./data/progress.json")
    user_progress = next((p for p in progress_list if p["user_id"] == session["usuario_id"]), None)

    return user_progress["deck"]
    