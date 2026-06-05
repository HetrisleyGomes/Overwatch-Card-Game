from flask import blueprints, render_template, request, session, redirect, url_for, g
from flask_socketio import join_room, emit

from services.user_service import  get_battle_cards
from services.progress_service import  get_deck
from services.collection_service import format_carta
from routes import get_db_connection

from sql.controller.user_controller import UserController
from sql.repositories.user_repository import UserRepository

from server import socketio
import random

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
import uuid
@combate.route("/buscar-partida")
def buscar_partida():
    connection = get_db_connection()
    if connection is None:
        return "Erro ao conectar ao banco de dados.", 500
    deck = get_deck(connection)
    if len(deck) < 12:
        return redirect(url_for("combate.home"))

    user_id = session["usuario_id"]

    # procurar sala disponível
    for room_id, room in salas.items():
        if len(room["players"]) == 1:
            room["players"].append({"id": user_id, "ready": False})
            room["status"] = "full"
            return redirect(url_for("combate.aguardando", room_id=room_id))

    # nenhuma sala → criar nova
    room_id = str(uuid.uuid4())

    salas[room_id] = {
        "players": [
            {"id": user_id, "ready": False}
        ],
        "status": "waiting"
    }
    return redirect(url_for("combate.aguardando", room_id=room_id))

@combate.route("/aguardando/<room_id>")
def aguardando(room_id):
    connection = get_db_connection()
    if connection is None:
        return "Erro ao conectar ao banco de dados.", 500

    repo = UserRepository(connection)
    ctll = UserController(repo)

    user = ctll.get_user(session["usuario_id"])
    return render_template("waiting.html", room_id=room_id, user=user)

@socketio.on("player_ready")
def handle_ready(data):
    room_id = data["room_id"]
    user_id = data["user_id"]
    room = salas.get(room_id)
    for p in room["players"]:
        if int(p["id"]) == int(user_id):
            p["ready"] = True
    emit("room_update", room, to=room_id)

    # se todos prontos → iniciar
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

@combate.route("/battle/<room_id>")
def battle(room_id):
    room = salas.get(room_id)
    gs = room.get("game_state")
    if gs:
        return redirect(url_for("combate.home"))
    
    connection = get_db_connection()
    if connection is None:
        return "Erro ao conectar ao banco de dados.", 500

    repo = UserRepository(connection)
    ctll = UserController(repo)

    game_state = {
        "room_id": room_id,
        "round": 1,
        "phase": "pre_game",
        'host': salas[room_id]['players'][0]['id']
    }

    jogadores = []

    for user in salas[room_id]['players']:
        id = user['id']
        user = ctll.get_user_battle(id)
        modelo = {
        'id': id,
        'nome': user['nome'],
        'icone': user['profile_img'],
        'hp': 20,
        'hand': [],
        'deck': [],
        'discarded': []
        }

        cartas = get_battle_cards(connection, id)
        for carta_id in cartas:
            carta = format_carta(carta_id)
            modelo["deck"].append(carta)
        jogadores.append(modelo)

    salas[room_id]['game_state'] = game_state.copy()
    salas[room_id]['jogadores'] = jogadores.copy()
    salas[room_id]["selected_cards"] = {}
    return render_template("battle.html", room_id=room_id, game_state=game_state, jogadores=jogadores)

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
        winner = next(
            (p for p in room["jogadores"]
             if p["id"] != user_id),
            None
        )
        if winner:
            emit(
                "enemy_disconnect",
                {"winner_id": winner["id"]},
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

    jogadores = room["jogadores"]
    game_state = room["game_state"]

    for jogador in jogadores:
        random.shuffle(jogador["deck"])

        if "hand" not in jogador:
            jogador["hand"] = []
        
        for i in range(5):
            if jogador["deck"]:
                carta = jogador["deck"].pop()
                jogador["hand"].append(carta)
    game_state["phase"] = "fist_choose"

    emit("game_state", {
        "game_state": game_state,
        "jogadores": jogadores
    }, to=room_id)

@socketio.on("select_card")
def select_card(data):
    room_id = data["room_id"]
    card_id = data["card_id"]
    user_id = session["usuario_id"]
    room = salas[room_id]

    if "selected_cards" not in room:
        room["selected_cards"] = {}

    room["selected_cards"][user_id] = format_carta(card_id)

    if len(room["selected_cards"]) == 2:
        combate_1(room_id,room)

def combate_1(room_id, room):
    jogadores = room["jogadores"]
    selected_cards = room["selected_cards"]
    result = {}
    for jgdr in jogadores:
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
        "escudo": 0,
        "ataque": 0,
        "cura": 0
    }
    match classe:
        case 'Tanque':
            template['escudo'] += 2
            template['ataque'] += 1
        case 'Dano':
            template['ataque'] += 3
        case 'Suporte':
            template["cura"] += 2
    return template

@socketio.on("combate_resolver")
def combate_2(data):
    room_id = data["room_id"]
    room = salas[room_id]
    jogadores = room["jogadores"]
    effects = room["battle_effects"]
    changes = {}

    for jogador in jogadores:
        player_id = jogador["id"]
        vida_inicial = jogador["hp"]
        effect_player = effects.get(player_id, {})
        effect_oponent = next(
            (
                effects[p["id"]]
                for p in jogadores
                if p["id"] != player_id
            ),
            None
        )

        if not effect_oponent:
            continue
        ataque_recebido = effect_oponent.get("ataque", 0)
        escudo = effect_player.get("escudo", 0)
        cura = effect_player.get("cura", 0)
        dano = max(0, ataque_recebido - escudo)

        jogador["hp"] -= dano
        jogador["hp"] += cura

        if jogador["hp"] > 20:
            jogador["hp"] = 20
        if jogador["hp"] < 0:
            jogador["hp"] = 0

        if vida_inicial > jogador["hp"]:
            changes[player_id] = {
                "type": "damaged",
                "value": max(0, dano - cura)
            }
        elif vida_inicial < jogador["hp"]:
            changes[player_id] = {
                "type": "healed",
                "value": max(0, cura - dano)
            }
        else:
            changes[player_id] = {
                "type": "neutral",
                "value": 0
            }

    finalize_battle(room)
    room["game_state"]["phase"] = "battle_resolve"
    emit("battle_phase_two", {
        "game_state": room["game_state"],
        "jogadores": room["jogadores"],
        "changes": changes,
    }, to=room_id)

@socketio.on("end_turn")
def fim_de_turno(data):
    room_id = data["room_id"]
    room = salas[room_id]
    game_state = room["game_state"]
    jogadores = room["jogadores"]

    # =========================
    # VERIFICAR DERROTA POR HP
    # =========================
    losers = [p for p in jogadores if p["hp"] <= 0]
    room["finished"] = True
    if len(losers) == 2:
        emit("empate", {
            "game_state": game_state
        }, to=room_id)
        return
    elif len(losers) == 1:
        loser_id = losers[0]["id"]
        winner = next(
            (p for p in jogadores if p["id"] != loser_id),
            None
        )
        emit("victory", {
            "winner_id": winner["id"]
        }, to=room_id)
        return
    
    if game_state["round"] >= 7:
        player_1 = jogadores[0]
        player_2 = jogadores[1]
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
    # =========================
    # PRÓXIMA RODADA
    # =========================
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
    jogadores = room["jogadores"]

    for jogador in jogadores:
        random.shuffle(jogador["deck"])

        if "hand" not in jogador:
            jogador["hand"] = []

        if jogador["deck"]:
            carta = jogador["deck"].pop()
            jogador["hand"].append(carta)
        
    room["game_state"]["phase"] = "choose"
    emit("game_state", {
        "game_state": room["game_state"],
        "jogadores": jogadores
    }, to=room_id)

def finalize_battle(room):
    jogadores = room["jogadores"]
    selected_cards = room["selected_cards"]

    for jogador in jogadores:
        user_id = jogador["id"]
        selected_card_id = selected_cards.get(user_id)

        if not selected_card_id:
            continue
        card = next(
            (
                c for c in jogador["hand"]
                if c["carta_id"] == selected_card_id['carta_id']
            ),
            None
        )
        if card:
            jogador["hand"].remove(card)
            jogador["discarded"].append(card)
    
    room["selected_cards"] = {}

# Paginas de fim de batalha ==========================
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
        return redirect(url_for("combate.home"))

    result = session.pop("battle_result", None)
    winner_id = session.pop("winner_id", None)
    room_id = session.pop("room_id", None)

    room = salas[room_id]
    jogadores = room["jogadores"]

    user_id = session["usuario_id"]

    num = room.get("players_views", 0)
    room["players_views"] = num+1
    if room["players_views"] == 2:
        del salas[room_id]
    return render_template("result_battle.html", result=result, user_id=user_id, winner_id=winner_id, jogadores=jogadores)
