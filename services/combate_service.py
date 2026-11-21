from services.user_service import  get_battle_cards
from services.collection_service import card_format, get_pve_cards
from utils.json_utils import get_classes_lang, get_combat_tips, get_global_tips

from sql.controller.user_controller import UserController
from sql.repositories.user_repository import UserRepository
from sql.connection import get_db_connection

from flask import session
import random

salas = {
    "123": {
        "players": [
            {"id": 1, "ready": True},
            {"id": 2, "ready": True}
        ],
        "status": "full"
    }
}

def get_user_info():
    connection = get_db_connection()
    if connection is None:
        return "Erro ao conectar ao banco de dados.", 500
    repo = UserRepository(connection)
    ctll = UserController(repo)
    ctll.get_user(session["user_id"])

def initialize_battle(room_id):
    connection = get_db_connection()
    if connection is None:
        return "Erro ao conectar ao banco de dados.", 500
    
    repo = UserRepository(connection)
    ctll = UserController(repo)
    lang = session["lang"]
    terms_lang = get_classes_lang(lang)
    combat_tips = get_combat_tips(lang)

    game_state = {
        "room_id": room_id,
        "round": 1,
        "phase": "pre_game",
        'host': salas[room_id]['players'][0]['id'],
        'dict_lang': terms_lang,
        'combat_tips': combat_tips,
        'mode': salas[room_id]['mode']
    }

    players = []
    
    for user in salas[room_id]['players']:
        user_id = user['id']
        user = ctll.get_user_battle(user_id)
        modelo = {
        'id': user_id,
        'nome': user['nome'],
        'icone': user['profile_img'],
        'hp': 20,
        'hand': [],
        'deck': [],
        'discarded': []
        }

        cartas = get_battle_cards(connection, user_id)
        for carta_id in cartas:
            carta = card_format(carta_id, lang)
            modelo["deck"].append(carta)
        players.append(modelo)

    if salas[room_id]['mode'] == 'pve':
        modelo = {
            "id": "bot",
            "nome": "Treinador",
            'icone': "logo.png",
            "hp": 20,
            "hand": [],
            "deck": [],
            "discarded": []
        }
        cartas = get_pve_cards()
        for carta_id in cartas:
            carta = card_format(carta_id, lang)
            modelo["deck"].append(carta)
        players.append(modelo)
    
    salas[room_id]['game_state'] = game_state.copy()
    salas[room_id]['players'] = players.copy()
    salas[room_id]["selected_cards"] = {}


def check_class_and_subclass(carta):
    print('aquiiii---------------------')
    print(carta)
    # {'carta_id': 'bastion_classic', 'carta_nome': 'Bastion Classic', 'carta_img': 'Bastion_ow.png', 'raridade': 'epico', 'classe': 'Dano', 'subclasse': 'Classic', 'icon_ref': False, 'foil': True}
    classe = carta['classe']
    subclasse = carta['subclasse']
    raridade = carta['raridade']

    template = {
        "golpe veloz": 0,
        "escudo": 0,
        "ataque": 0,
        "habilidade": 0,
        "anti-cura": 0,
        "cura": 0,
        "ataque futuro": 0,
        "revitalizar": 0,
        "descuido": 0,
        "debilitar": 0,
        "armadura": 0
    }

    match classe:
        case 'Tanque':
            template['escudo'] += 3
            template['ataque'] += 1
        case 'Dano':
            template['ataque'] += 2
        case 'Suporte':
            template["cura"] += 1
            template['ataque'] += 1
        case 'Defensor':
            template['escudo'] += 1
            template['ataque'] += 1
        case 'Atacante':
            template["golpe veloz"] += 1
            template['ataque'] += 1

    match raridade:
        case 'ultra':
            template["armadura"] += 2
        case 'mitico':
            template["escudo"] += 2 if classe == 'Tanque' else 1 if template["escudo"] > 0 else 0
            template["ataque"] += 2 if classe == "Dano" else 1 if template["ataque"] > 0 else 0
            template["cura"] += 2 if classe == 'Suporte' else 1 if template["cura"] > 0 else 0

    if carta['icon_ref']:
        match carta['icon_ref']:
            case 'golden.png':
                template['ataque'] += 1
            case 'alter.png':
                if template['cura'] > 0:
                    template['cura'] += 2
                else:
                    template['escudo'] += 1
            case 'jade.png':
                template['revitalizar'] += 1
            case 'hard_light.png':
                template["escudo"] += 1
            case 'losmuertos.png':
                template['habilidade'] += 1




    match subclasse:
        case 'Incursor':
            template["golpe veloz"] += 3
        case 'Combatente':
            template["ataque"] += 3
        case 'Robusto':
            template['ataque'] += 1
            template['armadura'] += 2

        case 'Especialista':
            template["anti-cura"] += 3
        case 'Artilharia':
            template["ataque"] += 1
            template["habilidade"] += 2
        case 'Flanco':
            template["golpe veloz"] += 2
            template["ataque"] += 1
        case 'Reconhecimento':
            template["ataque"] += 2
            template["debilitar"] += 1

        case 'Tático':
            template["anti-cura"] += 2
            template["cura"] += 1
        case 'Socorrista':
            template["cura"] += 3
        case 'Sobrevivente':
            template["cura"] += 2
            template["armadura"] += 1

        case 'Assombrado':
            dano = template["ataque"]
            template["golpe veloz"] += dano + 3
        case 'Bardo':
            template["cura"] += 1
            template["revitalizar"] += 1
            template["debilitar"] += 1
        case 'Campeão':
            template["ataque"] += 1
            template["armadura"] += 2
        case 'Caçador':
            template["anti-cura"] += 3
        case 'Carregada':
            template['habilidade'] += 4
            template["descuido"] += 2
        case 'Classic':
            template["escudo"] += 1
            template["ataque"] += 1
            template['cura'] += 1
        case 'Coração':
            template['escudo'] += 1
            template['cura'] += 2
        case 'Cósmico':
            template['escudo'] += 2
            template['habilidade'] += 1
        case 'Elegante':
            template["escudo"] += 2 if classe == 'Tanque' else 1
            template["habilidade"] += 2 if classe in ["Dano", 'Suporte'] else 1
        case 'Fool':
            for i in range(2):
                a = random.randrange(1,4)
                if a == 1:
                    template["escudo"] += 1
                elif a == 2:
                    template["ataque"] += 1
                else:
                    template['cura'] += 1
        case 'Férias':
            template["ataque"] += 2
            template["revitalizar"] += 1
        case 'Guerreiro':
            template["ataque"] += 1
            template["ataque futuro"] += 2
        case 'Justice':
            template["ataque futuro"] += 3
        case 'Mirror':
            re, ra, rc = template["escudo"], template["ataque"], template['cura']
            template["escudo"] += rc + 2 if rc > 0 else 0
            template["ataque"] += re + 2 if re > 0 else 0
            template['cura'] += ra + 2 if ra > 0 else 0
        case 'Monstro':
            template["escudo"] = 0
            template["ataque"] += 4
            template["descuido"] += 2
        case 'Origem':
            template["escudo"] += 2 if template["escudo"] > 0 else 0
            template["ataque"] += 2 if template["ataque"] > 0 else 0
            template['cura'] += 2 if template["cura"] > 0 else 0
        case 'Perigo':
            template["golpe veloz"] += 2
            template["debilitar"] += 1
        case 'Perverso':
            template["ataque"] += 2
            template["anti-cura"] += 2
            template["descuido"] += 2
        case 'Vazio':
            template["habilidade"]+= 2
            template["anti-cura"]+= 1
        
    return template
