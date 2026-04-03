from utils.json_utils import read_json, write_json
from flask import session
from datetime import datetime, timedelta

def criar_usuario(nome, has_event):
    """Cria um registro de usuário novo caso não exista.
    
    Keyword arguments:
    nome -- Nome do usuário.
    Return: Retorna o id do usuário criado.
    """
    usuarios = carregar_usuarios()
    data = datetime.now().strftime("%Y-%m-%d")
        
    novo_usuario = {
        "id": len(usuarios) + 1,
        "nome": nome,
        "pontos": 0,
        "ultimo_login": data,
        "img_logo": "logo.png",
        "packs_diarios_abertos": 2,
        "contador_packs_comuns": 0,
        "packs_comprados_comum": 0,
        "packs_comprados_raro": 0,
        "has_already_get_daily_bonus": False,
        "packs_evento": has_event
    }

    usuarios.append(novo_usuario)

    salvar_usuarios(usuarios)

    return novo_usuario["id"]

def carregar_usuarios():
    """Lê as informações de user.json.
    
    Keyword arguments:
    Return: Informações lidas.
    """
    
    return read_json("./data/user.json")
    
def salvar_usuarios(usuarios):
    """Salva as informações do usuário.
    
    Keyword arguments:
    usuarios -- Todos os usários de user.json.
    Return: None.
    """
    
    write_json("./data/user.json", usuarios)

# Atualizar data ===========================================
def verify_date(usuarios, user, evento = False):
    """Atualiza os pacotes diários verificando a última data de entrada
    
    Keyword arguments:
    user -- Informações do usuário.
    Return: None.
    """
    
    ultimo_login_str = user["ultimo_login"]
    hoje = datetime.now().date()
    ultimo_login = datetime.strptime(ultimo_login_str, "%Y-%m-%d").date()

    if ultimo_login != hoje:
        user["ultimo_login"] = hoje.strftime("%Y-%m-%d")
        user["packs_diarios_abertos"] = 2
        user["has_already_get_daily_bonus"] = False
        if evento:
            user["packs_evento"] += 1

        salvar_usuarios(usuarios)

# Remove pacotes de evento
def delete_events_packs():
    """Remove os packs de evento acumulados e os converte em pontos.

    Return: None
    """
    
    usuarios = carregar_usuarios()
    user = next((u for u in usuarios if u["id"] == session["usuario_id"]), None)

    packs = user["packs_evento"]
    user["packs_evento"] = 0
    user["pontos"] = packs * 100

    salvar_usuarios(usuarios)

def get_img_logos():
    imgs = read_json("./data/icons.json")
    return imgs