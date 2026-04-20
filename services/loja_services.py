from utils.json_utils import read_json, write_json

def get_promocoes():
    prom = read_json("./data/promocao.json")
    if prom:
        return prom
    return False

def set_promocoes(prom_data):
    write_json("./data/promocao.json", prom_data)

def comprar_pack_prom(id):
    prom = get_promocoes()
    personagens = read_json("./data/characters.json")
    cartas = []

    for i in prom['itens']:
        carta = next((p for p in personagens if p["id"] == i), None)
        cartas.append(carta)

    all_progress = read_json("./data/progress.json")
    progress = next((u for u in all_progress if u["user_id"] == id), None)

    personagens_set = set(progress["personagens"])

    for c in cartas:
        print(c)
        cid = c["id"]
        if cid not in personagens_set:
            personagens_set.add(cid)
            progress["personagens"].append(cid)

    write_json("./data/progress.json", all_progress)
    prom["has_buy"].append(id)
    set_promocoes(prom)

    return prom['value']