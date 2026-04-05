from .user_service import carregar_usuarios, salvar_usuarios
from utils.json_utils import read_json, write_json
from flask import session

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
    for c in cartas:
        cid = c["id"]

        if cid not in progress["personagens"]:
            progress["personagens"][cid] = 1
        else:
            progress["personagens"][cid] += 1

        if progress["personagens"][cid] > 1:
            pontos += rarity_convert(c["raridade"])
        
        xp += get_xp_calc(c['raridade'], pack_rarity=rarity)
    
    # Faz o controle dos pacotes
    if rarity == "comum":
        if user["packs_diarios_abertos"] > 0:
            if user["contador_packs_comuns"] < 20:
                user["contador_packs_comuns"] += 1
            user["packs_diarios_abertos"] -= 1
        elif user["packs_comprados_comum"] > 0:
            user["packs_comprados_comum"] -= 1
    elif rarity == "raro":
        if user["contador_packs_comuns"] == 20:
            user["contador_packs_comuns"] = 0
        elif user["packs_comprados_raro"] > 0:
            user["packs_comprados_raro"] -= 1
    elif rarity == "especial":
        user["packs_evento"] -= 1
        pass
    
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
    "personagens": {},
    "sets_completos": []
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
        case "raro":
            return 5
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
        case "raro":
            value = 3
        case "mitico":
            value = 3
        case "especial":
            value = 2
    match pack_rarity:
        case "comum":
            return value
        case "raro":
            return value * 2
        case "especial":
            return value * 2
        
        
    