from utils.json_utils import read_json, write_json
from services.user_service import carregar_usuarios, salvar_usuarios
from flask import session

def verificar_sets():
    """Verifica se um conjunto de cartas foi completado.
    
    Keyword arguments:
    Return: Retorna o nome dos sets completados, e a quantidade de pontos obtidas
    """
    
    progress_list = read_json("./data/progress.json")
    usuarios = carregar_usuarios()
    sets = read_json("./data/sets.json")

    user_id = session["usuario_id"]

    user_progress = next((p for p in progress_list if p["user_id"] == user_id), None)
    user = next((u for u in usuarios if u["id"] == user_id), None)

    if user_progress is None or user is None:
        return
    
    personagens_usuario = user_progress["personagens"]
    sets_completos = user_progress["sets_completos"]
    
    sets_nomes = []
    pontos_sets = 0

    for s in sets:
        set_id = s["id"]

        # já completou → ignora
        if set_id in sets_completos:
            continue

        # verifica se tem todos personagens
        completo = all(
            personagem in personagens_usuario
            for personagem in s["personagens"]
        )

        if completo:
            sets_nomes.append(s["nome"])
            sets_completos.append(set_id)

            recompensa = s.get("recompensa", {})
            pontos_sets += recompensa.get("pontos", 0)
        
    
    user["pontos"] += pontos_sets
    
    write_json("./data/progress.json", progress_list)
    salvar_usuarios(usuarios)

    return sets_nomes, pontos_sets

def formatar_inventario():
    usuarios = carregar_usuarios()

    characters = read_json("./data/characters.json")
    progress_list = read_json("./data/progress.json")

    user_id = session["usuario_id"]

    user_progress = next((p for p in progress_list if p["user_id"] == user_id), None)
    user = next((u for u in usuarios if u["id"] == user_id), None)

    if user_progress is None or user is None:
        return
    
    personagens_usuario = user_progress["personagens"] if user_progress else {}

    cartas_view = []

    for c in characters:
        cid = c["id"]

        possui = cid in personagens_usuario
        quantidade = personagens_usuario.get(cid, 0)

        cartas_view.append({
            "id": cid,
            "base": c["base"],
            "nome": c["nome"],
            "classe": c["classe"],
            "subclasse": c["subclasse"],
            "entrada": c["entrada"],
            "ult_nome": c["ult_nome"],
            "ult": c["ult"],
            "raridade": c["raridade"],
            "img": c["img"],
            "brilha": c["raridade"] == "mitico",
            "possui": possui,
            "quantidade": quantidade
        })

    return cartas_view


def listar_sets_usuario():
    sets = read_json("./data/sets.json")
    progress_list = read_json("./data/progress.json")
    characters = read_json("./data/characters.json")

    user_id = session["usuario_id"]

    user_progress = next(
        (p for p in progress_list if p["user_id"] == user_id),
        None
    )

    if user_progress is None:
        return []

    personagens_usuario = user_progress["personagens"]

    resultado = []
    
    mapa_characters = {c["id"]: c for c in characters}

    for s in sets:
        personagens_set = s["personagens"]

        completo = all(
            personagem in personagens_usuario
            for personagem in personagens_set
        )

        progresso = sum(
            1 for p in personagens_set if p in personagens_usuario
        )

        cartas_detalhadas = []

        for cid in personagens_set:
            c = mapa_characters.get(cid)

            if not c:
                continue

            possui = cid in personagens_usuario

            cartas_detalhadas.append({
            "id": cid,
            "nome": c["nome"],
            "raridade": c["raridade"],
            "img": c["img"],
            "possui": possui,
        })


        set_info = {
            "nome": s["nome"],
            "completo": completo,
            "cartas": cartas_detalhadas,
            "progresso": f"{progresso}/{len(personagens_set)}",
            "progresso_percent": int((progresso/len(personagens_set))*100)
        }

        if completo:
            set_info["recompensa"] = s.get("recompensa", {})

        resultado.append(set_info)

    return resultado