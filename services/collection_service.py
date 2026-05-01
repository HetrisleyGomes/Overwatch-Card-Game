from utils.json_utils import get_characters, get_sets
from sql.controller.progress_controller import ProgressController
from sql.repositories.progress_repository import ProgressRepository


def verificar_sets(conn, user_id):
    """Verifica se um conjunto de cartas foi completado.
    
    Keyword arguments:
    - conn: Conexão com o banco de dados.
    - user_id: Identificação do usuário.
    Return: Retorna o nome dos sets completados, e a quantidade de pontos obtidas
    """

    repo = ProgressRepository(conn)
    ctll = ProgressController(repo)

    sets = get_sets()
    personagens_usuario = ctll.get_all_cards_id(user_id)
    sets_completos = ctll.get_all_sets(user_id)
    
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
        

    
    return sets_nomes, pontos_sets

def formatar_inventario(conn, user_id):
    """Formata as cartas do usuário em um dicionário.
    
    Keyword arguments:
    - conn: Conexão com o banco de dados.
    - user_id: Identificação do usuário.
    Return: Retorna um dicionário com as cartas.
    """
    repo = ProgressRepository(conn)
    ctll = ProgressController(repo)

    characters = get_characters()

    personagens_usuario = ctll.get_all_cards_id(user_id)

    cartas_view = []

    for c in characters:
        cid = c["id"]

        possui = cid in personagens_usuario
        icon_ref = c.get("icon_ref", False)
        golden_weapon = c.get("golden_weapon", False)
        foil = c.get("foil", False)
        is_event = c.get("evento", False)

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
            "icon_ref": icon_ref,
            "is_evento": is_event,
            "golden_weapon": golden_weapon,
            "foil": foil,
            "possui": possui
        })

    return cartas_view


def listar_sets_usuario(conn, user_id):
    """Formata os sets e as cartas do usuário em um dicionário.
    
    Keyword arguments:
    - conn: Conexão com o banco de dados.
    - user_id: Identificação do usuário.
    Return: Retorna um dicionário com os sets, cada set tem um dicionário de cartas.
    """

    repo = ProgressRepository(conn)
    ctll = ProgressController(repo)

    sets = get_sets()
    characters = get_characters()

    personagens_usuario = ctll.get_all_cards_id(user_id)

    resultado = []
    
    mapa_characters = {c["id"]: c for c in characters}

    for s in sets:
        personagens_set = s["personagens"]
        personagens_set_extra = s.get("other_personagens", [])

        # ToDo: Troca\r isso para conferir a lista de progress invés da quantidade de cartas.
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
            is_event = c.get("evento", False)
            golden_weapon = c.get("golden_weapon", False)
            icon_ref = c.get("icon_ref", False)


            cartas_detalhadas.append({
            "id": cid,
            "nome": c["nome"],
            "raridade": c["raridade"],
            "img": c["img"],
            "icon_ref": icon_ref,
            "evento": is_event,
            "golden_weapon": golden_weapon,
            "possui": possui,
        })
            
        cartas_extras = []
        if personagens_set_extra is not None:
            for cid in personagens_set_extra:
                
                c = mapa_characters.get(cid)

                if not c:
                    continue

                possui = cid in personagens_usuario

                cartas_extras.append({
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
            "cartas_extra": cartas_extras,
            "progresso": f"{progresso}/{len(personagens_set)}",
            "progresso_percent": int((progresso/len(personagens_set))*100)
        }

        if completo:
            set_info["recompensa"] = s.get("recompensa", {})

        resultado.append(set_info)

    return resultado