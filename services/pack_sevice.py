from utils.json_utils import read_json
import random

#SORTEIO ======================================================
def sortear_raridade(chances):
    """Sorteia a raridade da carta.
    
    Keyword arguments:
    chances -- Um array com a raridade e a porcentagem de ser escolhida.
    Return: Retorna a raridade escolhida aleatoriamente.
    """
    
    raridades = list(chances.keys())
    pesos = list(chances.values())

    return random.choices(raridades, weights=pesos, k=1)[0]

def abrir_pack(tipo_pack):
    """Sorteia um conjunto de cartas dependendo do tipo de pacote.
    
    Keyword arguments:
    tipo_pack -- O tipo de pacote ("comum" ou "raro").
    Return: Retorna o conjunto de cartas sorteadas.
    """
    
    packs = read_json("./data/packs.json")
    personagens = read_json("./data/characters.json")

    pack = packs[tipo_pack]
    cartas = []

    for i in range(pack["cartas_por_pack"]):
        # 1. sortear raridade
        chances_slot = pack["chance"][i]
        raridade = sortear_raridade(chances_slot)

        # 2. filtrar personagens dessa raridade
        possiveis = [p for p in personagens if p["raridade"] == raridade and p not in cartas]

        # 3. escolher personagem
        carta = random.choice(possiveis)

        cartas.append(carta)

    return cartas

def abrir_pack_evento(ids_eventos):
    personagens = read_json("./data/characters.json")

    personagens_filtrados = [
        p for p in personagens
        if p.get("evento") is None or p.get("evento") in ids_eventos
    ]

    cartas = []
    # 1. sortear raridade
    
    packs = read_json("./data/packs.json")
    pack = packs["especial"]
    raridade = sortear_raridade(pack["chance"][0])

    # 2. filtrar personagens dessa raridade
    possiveis = [p for p in personagens_filtrados if p["raridade"] == raridade]

    # 3. escolher personagem
    carta = random.choice(possiveis)

    cartas.append(carta)

    return cartas