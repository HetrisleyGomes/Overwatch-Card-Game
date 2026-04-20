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
        possiveis = [p for p in personagens if p["raridade"] == raridade and p.get("evento") is None and p not in cartas]

        # 3. escolher personagem
        carta = random.choice(possiveis)

        cartas.append(carta)

    return cartas

def abrir_pack_evento(id_evento):
    personagens = read_json("./data/characters.json")

    personagens_filtrados = [
        p for p in personagens
        if p.get("evento") in [id_evento]
    ]

    if id_evento == "aniversary":
        golden = [
            p for p in personagens
            if p.get("golden_weapon")
        ]
    
    # 1. sortear raridade
    packs = read_json("./data/packs.json")
    pack = packs[id_evento]
    
    cartas = []

    # 🎁 Caso especial: aniversário
    if id_evento == "aniversary":
        possiveis_golden = [p for p in golden if p["raridade"] == "lendario"]
        possiveis_evento = [p for p in personagens_filtrados if p["raridade"] == "epico"]

        carta1 = random.choice(possiveis_golden)
        carta2 = random.choice(possiveis_evento)

        carta2["is_evento"] = id_evento

        cartas.extend([carta1, carta2])

    # 🎴 Lógica padrão (todos os outros casos)
    else:
        for i in range(pack["cartas_por_pack"]):
            raridade = sortear_raridade(pack["chance"][i])

            possiveis = [
                p for p in personagens_filtrados
                if p["raridade"] == raridade
            ]

            carta = random.choice(possiveis)
            carta["is_evento"] = id_evento

        cartas.append(carta)

    return cartas