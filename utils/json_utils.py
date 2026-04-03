import json

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