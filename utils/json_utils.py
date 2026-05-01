import json
from functools import lru_cache

def read_json(path):
    """Lê um json.
    
    Keyword arguments:
    path -- Caminho do json.
    Return: Retorna o json lido.
    """
    
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def write_json(path, data):
    """Atualiza um json.
    
    Keyword arguments:
    path -- Caminho do json.
    data -- Informações a serem salvas.
    Return: None.
    """
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


@lru_cache()
def get_characters():
    with open('./data/characters.json', "r", encoding="utf-8") as f:
        return json.load(f)

@lru_cache()
def get_sets():
    with open('./data/sets.json', "r", encoding="utf-8") as f:
        return json.load(f)
    
def get_events():
    with open('./data/events.json', "r", encoding="utf-8") as f:
        return json.load(f)

def get_icons():
    with open('./data/icons.json', "r", encoding="utf-8") as f:
        return json.load(f)
    
def get_packs():
    with open('./data/packs.json', "r", encoding="utf-8") as f:
        return json.load(f)

def get_promocao():
    with open('./data/promocao.json', "r", encoding="utf-8") as f:
        return json.load(f)