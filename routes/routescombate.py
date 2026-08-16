from flask import blueprints, render_template, request, session, redirect, url_for
from flask_socketio import join_room, emit
from services.user_service import  get_battle_cards
from services.progress_service import  get_deck
from services.collection_service import card_format, get_pve_cards, bot_select_card

from utils.json_utils import get_classes_lang, get_combat_tips, get_global_tips

from sql.controller.user_controller import UserController
from sql.repositories.user_repository import UserRepository
from sql.connection import get_db_connection

from server import socketio
import random, uuid, math

combate = blueprints.Blueprint('combate', __name__, static_folder='static', template_folder='templates')

salas = {
    "123": {
        "players": [
            {"id": 1, "ready": True},
            {"id": 2, "ready": True}
        ],
        "status": "full"
    }
}
socket_to_room = {}
socket_to_user = {}


# BATALHAS ==============================================
@combate.route("/game_room")
def game_room():
    user = session['user_data']
    lang = session['lang']
    global_tips = get_global_tips(lang, "game_room")
    return render_template("/combat/game_room.html", user = user, global_tips=global_tips)



# Buscar Oponentes ==========================================
@combate.route("/buscar-partida")
def buscar_partida():
    connection = get_db_connection()
    if connection is None:
        return "Erro ao conectar ao banco de dados.", 500
    deck = get_deck(connection)
    if len(deck) < 12:
        return redirect(url_for("main.home"))

    user_id = session["user_id"]

    # procurar sala disponível
    for room_id, room in salas.items():
        if len(room["players"]) == 1:
            room["players"].append({"id": user_id, "ready": False})
            room["status"] = "full"
            return redirect(url_for("combate.aguardando", room_id=room_id))

    # nenhuma sala -> criar nova
    room_id = str(uuid.uuid4())

    salas[room_id] = {
        "players": [
            {"id": user_id, "ready": False}
        ],
        "status": "waiting",
        "mode": "pvp"
    }
    return redirect(url_for("combate.aguardando", room_id=room_id))

@combate.route("/aguardando/<room_id>")
def aguardando(room_id):
    connection = get_db_connection()
    if connection is None:
        return "Erro ao conectar ao banco de dados.", 500

    repo = UserRepository(connection)
    ctll = UserController(repo)

    user = ctll.get_user(session["user_id"])
    lang = session['lang']
    global_tips = get_global_tips(lang, "combat")

    return render_template("combat/waiting.html", room_id=room_id, user=user, lang=lang, global_tips=global_tips)

@socketio.on("player_ready")
def handle_ready(data):
    room_id = data["room_id"]
    user_id = data["user_id"]
    room = salas.get(room_id)
    for p in room["players"]:
        if int(p["id"]) == int(user_id):
            p["ready"] = True
    emit("room_update", room, to=room_id)

    if len(room["players"]) == 2 and all(p["ready"] for p in room["players"]):
        emit("start_game", {"room_id": room_id}, to=room_id)


@socketio.on("join_room")
def handle_join(data):
    room_id = data["room_id"]
    user_id = data["user_id"]

    join_room(room_id)
    room = salas.get(room_id)
    
    socket_to_room[request.sid] = room_id
    socket_to_user[request.sid] = user_id

    emit("room_update", room, to=room_id)

@socketio.on("leave_room")
def leave_room_handler(data):
    room_id = data["room_id"]
    user_id = int(data["user_id"])
    room = salas.get(room_id)

    if not room:
        return
    room["players"] = [
        p for p in room["players"]
        if p["id"] != user_id
    ]

    if len(room["players"]) == 0:
        del salas[room_id]
    else:
        room["status"] = "waiting"
        emit("room_update", room, to=room_id)
    sid = request.sid

    socket_to_room.pop(sid, None)
    socket_to_user.pop(sid, None)


# Partida single player
@combate.route("/buscar-partida-single")
def buscar_partida_single():
    connection = get_db_connection()
    if connection is None:
        return "Erro ao conectar ao banco de dados.", 500
    deck = get_deck(connection)
    if len(deck) < 12:
        return redirect(url_for("main.home"))

    user_id = session["user_id"]

    # nenhuma sala -> criar nova
    room_id = str(uuid.uuid4())

    salas[room_id] = {
        "players": [
            {"id": user_id, "ready": False}
        ],
        "status": "full",
        "mode": "pve"
    }
    return redirect(url_for("combate.battle", room_id=room_id))


# Organização da batalha ========================================
@combate.route("/battle/<room_id>")
def battle(room_id):
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
            'icone': "",
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
    return render_template("combat/battle.html", room_id=room_id, game_state=game_state, players=players)

@socketio.on("disconnect")
def handle_disconnect():
    sid = request.sid
    room_id = socket_to_room.get(sid)
    user_id = socket_to_user.get(sid)

    if not room_id or not user_id:
        return
    
    room = salas.get(room_id)
    if room and room.get("finished"):
        return
    
    game_started = room.get("game_state") is not None
    if game_started:
        lang = session['lang']
        win_msg = "Seu adversário não respondeu a tempo ou desconectou!" if lang == "br" else "Your opponent didn't respond in time or disconnected!"
        winner = next(
            (p for p in room["players"]
             if p["id"] != user_id),
            None
        )
        if winner:
            emit(
                "enemy_disconnect",
                {
                    "winner_id": winner["id"],
                    "msg": win_msg
                },
                to=room_id
            )
    else:
        room["players"] = [
            p for p in room["players"]
            if p["id"] != user_id
        ]
        if len(room["players"]) == 0:
            del salas[room_id]
        else:
            room["status"] = "waiting"
            emit(
                "room_update",
                room,
                to=room_id
            )
    socket_to_room.pop(sid, None)
    socket_to_user.pop(sid, None)

@socketio.on("fist_draw")
def fist_draw(data):
    room_id = data["room_id"]
    room = salas[room_id]

    players = room["players"]
    game_state = room["game_state"]

    for player in players:
        random.shuffle(player["deck"])

        if "hand" not in player:
            player["hand"] = []
        
        for i in range(5):
            if player["deck"]:
                carta = player["deck"].pop()
                player["hand"].append(carta)
    game_state["phase"] = "fist_choose"

    emit("game_state", {
        "game_state": game_state,
        "players": players
    }, to=room_id)

@socketio.on("select_card")
def select_card(data):
    room_id = data["room_id"]
    card_id = data["card_id"]
    user_id = session["user_id"]
    room = salas[room_id]
    lang = session["lang"]

    if "selected_cards" not in room:
        room["selected_cards"] = {}

    room["selected_cards"][user_id] = card_format(card_id, lang)
    if salas[room_id]['mode'] == 'pve':
        room["selected_cards"]['bot'] = bot_select_card(salas[room_id]['players'][1]['hand'])

    if len(room["selected_cards"]) == 2:
        combate_1(room_id,room)
        

# COMBATE =========================================================================
def combate_1(room_id, room):
    players = room["players"]
    selected_cards = room["selected_cards"]
    result = {}
    for jgdr in players:
        player_id = jgdr['id']
        template = check_class_and_subclass(selected_cards[player_id]['classe'], selected_cards[player_id]['subclasse'])
        result[player_id] = template

    room["battle_effects"] = result
    room["game_state"]["phase"] = "battle"
    emit("battle_phase_one", {
        "game_state_phase": room["game_state"]["phase"],
        "selected_cards": room["selected_cards"],
        "result_values": result
    }, to=room_id)

def check_class_and_subclass(classe, subclasse):
    template = {
        "golpe veloz": 0,
        "escudo": 0,
        "ataque": 0,
        "anti-cura": 0,
        "cura": 0,
        "ataque futuro": 0,
        "revitalizar": 0,
        "descuido": 0,
        "debilitar": 0
    }
    match classe:
        case 'Tanque':
            template['escudo'] += 2
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


    match subclasse:
        case 'Incursor':
            template["golpe veloz"] += 2
            template["ataque"] += 1
        case 'Combatente':
            template["ataque"] += 3
        case 'Robusto':
            template['escudo'] += 3

        case 'Especialista':
            template['ataque'] += 1
            template["anti-cura"] += 2
        case 'Artilharia':
            template["ataque"] += 3
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
            template["ataque"] += 2
            template["cura"] += 1


        case 'Campeão':
            template["escudo"] += 2
            template["ataque"] += 1
        case 'Caçador':
            template["ataque futuro"] += 1
            template["anti-cura"] += 2
        case 'Classic':
            template["escudo"] += 1
            template["ataque"] += 1
            template['cura'] += 1
        case 'Coração':
            template['escudo'] += 2
            template['revitalizar'] += 1
        case 'Cósmico':
            template['escudo'] += 2
            template['cura'] += 1
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
            template["escudo"] += 1
            template["ataque futuro"] += 2
        case 'Mirror':
            re, rd, rc = template["escudo"], template["ataque"], template['cura']
            template["escudo"] += rc + 2 if rc > 0 else 0
            template["ataque"] += re + 2 if re > 0 else 0
            template['cura'] += rd + 2 if rd > 0 else 0
        case 'Monstro':
            template["escudo"] = 0
            template["ataque"] += 4
            template["descuido"] += 2
        case 'Perigo':
            template["golpe veloz"] += 2
            template["debilitar"] += 1
        case 'Perverso':
            template["ataque"] += 2
            template["anti-cura"] += 2
            template["descuido"] += 2
            template["cura"] = 0
        case 'Origem':
            template["escudo"] += 2 if template["escudo"] > 0 else 0
            template["ataque"] += 2 if template["ataque"] > 0 else 0
            template['cura'] += 2 if template['cura'] > 0 else 0
    return template

@socketio.on("combate_resolver")
def combate_2(data):
    room_id = data["room_id"]
    room = salas[room_id]
    
    changes = resolve_battle(room)
    
    emit("battle_phase_two", {
        "game_state": room["game_state"],
        "players": room["players"],
        "changes": changes,
    }, to=room_id)

def resolve_battle(room):
    if "battle_continue" not in room:
        room["battle_continue"] = {}

    players = room["players"]
    effects = room["battle_effects"]
    continuous = room.get("battle_continue", {})
    changes = {}

    for player in players:
        player_id = player["id"]
        vida_inicial = player["hp"]
        effect_player = effects.get(player_id, {})
        effect_oponent = next(
            (
                effects[p["id"]]
                for p in players
                if p["id"] != player_id
            ),
            None
        )
        effects_continuous = continuous.get(player_id, {})
        future_attack = effects_continuous.get("ataque_futuro", 0)
        revitalize = effects_continuous.get("revitalizar", 0)
        weaken = effects_continuous.get("debilitar", 0)

        if not effect_oponent:
            continue
        # Prioridade 1:
        ataque_veloz_recebido = effect_oponent.get("golpe veloz", 0)
        # Prioridade 2:
        ataque_recebido = effect_oponent.get("ataque", 0) + future_attack
        anticura_recebido = effect_oponent.get("anti-cura", 0)
        # Prioridade 3:
        escudo = effect_player.get("escudo", 0)
        cura = effect_player.get("cura", 0) * 2 if revitalize > 0 else effect_player.get("cura", 0)
        # Prioridade 4:
        ataque_futuro = effect_oponent.get("ataque futuro", 0) 
        revitalizar = effect_player.get("revitalizar", 0)
        descuido = effect_player.get("descuido", 0)
        debilitar = effect_oponent.get("debilitar", 0)

        dano_calc = max(0, ataque_recebido - escudo)
        if weaken > 0:
            dano_calc = math.ceil(dano_calc / 2)
        # Combate resolver:
        dano_final = ataque_veloz_recebido + dano_calc + descuido
        cura_final = max(0, cura - anticura_recebido)

        player["hp"] -= dano_final
        player["hp"] += cura_final

        if player["hp"] > 20:
            player["hp"] = 20
        if player["hp"] < 0:
            player["hp"] = 0

        if vida_inicial > player["hp"]:
            changes[player_id] = {
                "type": "damaged",
                "value": max(0, dano_final - cura_final)
            }
        elif vida_inicial < player["hp"]:
            changes[player_id] = {
                "type": "healed",
                "value": max(0, cura_final - dano_final)
            }
        else:
            changes[player_id] = {
                "type": "neutral",
                "value": 0
            }

        room["battle_continue"][player_id] = {
            "ataque_futuro": ataque_futuro,
            "revitalizar": revitalizar,
            "debilitar": debilitar
        }
        
    finalize_battle(room)
    room["game_state"]["phase"] = "battle_resolve"
    return changes

# END COMBATE ======================================================================
@socketio.on("end_turn")
def fim_de_turno(data):
    room_id = data["room_id"]
    room = salas[room_id]
    game_state = room["game_state"]
    players = room["players"]

    # VERIFICAR DERROTA POR HP
    losers = [p for p in players if p["hp"] <= 0]
    room["finished"] = True
    if len(losers) == 2:
        emit("empate", {
            "game_state": game_state
        }, to=room_id)
        return
    elif len(losers) == 1:
        loser_id = losers[0]["id"]
        winner = next(
            (p for p in players if p["id"] != loser_id),
            None
        )
        emit("victory", {
            "winner_id": winner["id"]
        }, to=room_id)
        return
    
    if game_state["round"] >= 7:
        player_1 = players[0]
        player_2 = players[1]
        # empate
        if player_1["hp"] == player_2["hp"]:
            emit("empate", {
                "game_state": game_state
            }, to=room_id)
        else:
            winner = (
                player_1
                if player_1["hp"] > player_2["hp"]
                else player_2
            )
            emit("victory", {
                "winner_id": winner["id"]
            }, to=room_id)
        return

    # PRÓXIMA RODADA
    room["finished"] = False
    game_state["round"] += 1
    game_state["phase"] = "draw"
    emit("end_turn", {
        "game_state": game_state,
    }, to=room_id)

@socketio.on("draw")
def draw(data):
    room_id = data["room_id"]
    room = salas[room_id]
    players = room["players"]

    for player in players:
        random.shuffle(player["deck"])

        if "hand" not in player:
            player["hand"] = []

        if player["deck"]:
            carta = player["deck"].pop()
            player["hand"].append(carta)
        
    room["game_state"]["phase"] = "choose"
    emit("game_state", {
        "game_state": room["game_state"],
        "players": players
    }, to=room_id)

def finalize_battle(room):
    players = room["players"]
    selected_cards = room["selected_cards"]

    for player in players:
        user_id = player["id"]
        selected_card_id = selected_cards.get(user_id)
        print("selected_card_id ================")
        print(selected_card_id)
        if not selected_card_id:
            continue
        card = next(
            (
                c for c in player["hand"]
                if c["carta_id"] == selected_card_id['carta_id']
            ),
            None
        )
        if card:
            player["hand"].remove(card)
            player["discarded"].append(card)
        print("Player ================")
        print(player)
    
    room["selected_cards"] = {}

@socketio.on("time_out")
def time_out(data):
    room_id = data["room_id"]
    user_id = data["user_id"]

    room = salas.get(room_id)
    if not room:
        return

    room.setdefault("timeouts", {})
    room["timeouts"][user_id] = True


    timeouts = room.get("timeouts", {})
    if len(timeouts) < 2:
        return
    
    selected = room.get("selected_cards", {})
    players = [j["id"] for j in room["players"]]

    p1 = players[0]
    p2 = players[1]

    p1_chose = p1 in selected
    p2_chose = p2 in selected

    if not p1_chose and not p2_chose:
        emit("empate", to=room_id)
    elif not p1_chose:
        emit("victory", {"winner_id": p2}, to=room_id)
    elif not p2_chose:
        emit("victory", {"winner_id": p1}, to=room_id)


# Paginas de fim de batalha =================================================
@combate.route("/set-battle-result", methods=["POST"])
def set_battle_result():
    data = request.get_json()

    session["battle_result"] = data["result"]
    session["winner_id"] = data.get("winner", None)
    session["room_id"] = data["sala"]
    return {"success": True}

@combate.route("/battle/finally")
def battle_victory():
    if not session.get("battle_result"):
        return redirect(url_for("main.home"))

    result = session.pop("battle_result", None)
    winner_id = session.pop("winner_id", None)
    room_id = session.pop("room_id", None)

    room = salas[room_id]
    players = room["players"]

    user_id = session["user_id"]

    num = room.get("players_views", 0)
    room["players_views"] = num+1
    if room["players_views"] == 2:
        del salas[room_id]
    return render_template("combat/result_battle.html", result=result, user_id=user_id, winner_id=winner_id, players=players)
