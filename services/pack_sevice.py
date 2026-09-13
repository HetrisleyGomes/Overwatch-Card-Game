from utils.json_utils import get_packs, get_characters
from services.collection_service import format_full_card
import random

ORDEM_RARIDADES = [
    "comum",
    "incomum",
    "epico",
    "lendario",
    "ultra",
    "mitico"
]

#SORTEIO ======================================================
def sortear_raridade(chances, raridade_minima=None):
    """Sorteia a raridade da carta.
    
    Keyword arguments:
    chances -- Um array com a raridade e a porcentagem de ser escolhida.
    Return: Retorna a raridade escolhida aleatoriamente.
    """

    if raridade_minima is not None:
        indice_anterior = ORDEM_RARIDADES.index(raridade_minima)

        chances = {
            raridade: chance
            for raridade, chance in chances.items()
            if raridade in ORDEM_RARIDADES[indice_anterior:]
        }

    raridades = list(chances.keys())
    pesos = list(chances.values())

    return random.choices( raridades, weights=pesos, k=1)[0]

def open_pack(tipo_pack, lang):
    """Sorteia um conjunto de cartas dependendo do tipo de pacote.
    
    Keyword arguments:
    tipo_pack -- O tipo de pacote ("comum" ou "raro").
    Return: Retorna o conjunto de cartas sorteadas.
    """
    
    packs = get_packs()
    personagens = get_characters()

    pack = packs[tipo_pack]
    cartas = []
    raridade_minima = None

    for i in range(pack["cartas_por_pack"]):
        # sortear raridade
        chances_slot = pack["chance"][i]
        raridade = sortear_raridade(chances_slot, raridade_minima)
        raridade_minima = raridade

        # filtrar personagens dessa raridade
        possiveis = [p for p in personagens if p["raridade"] == raridade and p.get("evento") is None and p not in cartas]

        # escolher personagem
        carta = random.choice(possiveis)
        formated_carta = format_full_card(carta, lang)
        cartas.append(formated_carta)

    return cartas

def open_event_pack(id_evento, lang):
    personagens = get_characters()
    is_super_halloween = False

    if id_evento != "summergames":
        personagens_filtrados = [
            p for p in personagens
            if p.get("evento") in [id_evento]
        ]
    elif id_evento == "halloween":
        let = random.randrange(0, 100)
        if let <= 95:
            personagens_filtrados = [
                p for p in personagens
                if p.get("subclasse") in ["Perigo", "Perverso"]
            ]
        else:
            is_super_halloween = True
            personagens_filtrados = [
                p for p in personagens
                if p.get("raridade") in ["mitico"]
            ]
            
    else:
        personagens_filtrados = [p for p in personagens if p.get("evento") is None]

    golden = []
    if id_evento in ["aniversary", "overwatch_2"]:
        golden = [
            p for p in personagens
            if p.get("golden_weapon")
        ]

    # sortear raridade
    packs = get_packs()

    pack = packs[id_evento] if not is_super_halloween else packs["halloween_super"]
    cartas = []

    # Caso especial: aniversário
    if id_evento in ["aniversary", "overwatch_2"]:
        carta1 = random.choice(golden)
        carta2 = random.choice(personagens_filtrados)

        carta2["is_evento"] = id_evento

        cartas.extend([format_full_card(carta1, lang), format_full_card(carta2, lang)])

    # Lógica padrão (todos os outros casos)
    else:
        raridade_minima = None

        for i in range(pack["cartas_por_pack"]):
            raridade = sortear_raridade(pack["chance"][i], raridade_minima)

            possiveis = [
                p for p in personagens_filtrados
                if p["raridade"] == raridade
            ]

            carta = random.choice(possiveis)
            carta["is_evento"] = id_evento
            carta_formated = format_full_card(carta, lang)
            cartas.append(carta_formated)

    return cartas