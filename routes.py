from flask import blueprints, render_template, request, session, redirect, url_for, g
from services.user_service import verify_date, sum_xp, get_battle_cards
from services.progress_service import registry_cards, save_deck_progress, get_deck
from services.pack_sevice import abrir_pack, abrir_pack_evento
from services.collection_service import verificar_sets, formatar_inventario, listar_sets_usuario, format_carta
from services.eventos_service import check_event_activation, get_eventos_ativos, get_last_log
from services.loja_services import get_promocoes, comprar_pack_prom, get_user_prom_logs
from services.inventory_service import get_img_logos, user_get_inventory, icon_view, get_new_img

from sql.controller.user_controller import UserController

from sql.repositories.user_repository import UserRepository

from server import socketio, app
from config import db_connection_handler

from datetime import datetime
from flask_socketio import join_room, emit
from werkzeug.security import check_password_hash, generate_password_hash

import psycopg2
import random

main = blueprints.Blueprint('main', __name__, static_folder='static', template_folder='templates')

salas = {
    "123": {
        "players": [
            {"id": 1, "ready": True},
            {"id": 2, "ready": True}
        ],
        "status": "full"
    }
}

# Função para conectar ao banco de dados
def get_db_connection():
    if 'db_conn' not in g:
        try:
            conn_string = db_connection_handler.get_connection_string()
            g.db_conn = psycopg2.connect(conn_string)
            print("Conexão ao banco PostgreSQL estabelecida para a requisição.")
        except Exception as e:
            print(f"Erro ao conectar no banco: {e}")
            g.db_conn = None
    return g.db_conn

# Função para fechar a conexão no final de cada requisição
@app.teardown_appcontext
def close_db_connection(e=None):
    db_conn = g.pop('db_conn', None)
    if db_conn is not None:
        db_conn.close()
        print("Conexão com o banco fechada.")

# Rota principal ========================================
@main.route('/')
def home():
    connection = get_db_connection()
    if connection is None:
        return "Erro ao conectar ao banco de dados.", 500

    repo = UserRepository(connection)
    ctll = UserController(repo)

    check_event_activation()
    ev = get_eventos_ativos()
    ev_validator = False
    if ev:
        ev_validator = True

    user, was_change = verify_date(ctll.get_user(session["usuario_id"]), ev_validator)
    if was_change:
        ctll.daily_update(user)
    log = get_last_log()
    prom = get_promocoes()

    return render_template('home.html', user=user, ev=ev, log=log, proms=prom if prom else None)

# Abrir pacote ========================================
# TODO: Transformar tudo isso em uma rota só
@main.route("/abrir-pack", methods=["POST"])
def abrir_pack_route():
    if request.method != "POST":
        return redirect(url_for("main.home"))
    
    # backend
    connection = get_db_connection()
    if connection is None:
        return "Erro ao conectar ao banco de dados.", 500

    repo = UserRepository(connection)
    ctll = UserController(repo)
    user = ctll.get_user(session["usuario_id"])

    # obtem informações do form
    tipo = request.form.get("tipo")
    evento_id = request.form.get("evento_id")

    # Lógica das cartas
    if tipo == "evento":
        cartas = abrir_pack_evento(evento_id)
    else:
        cartas = abrir_pack(tipo)


    user = registry_cards(connection, cartas, tipo, user)
    sets, pontos = verificar_sets(connection, user['id'])
    user['pontos'] += pontos
    ctll.edit_user(id=user['id'], user=user)

    session["ultimo_pack"] = cartas
    session["sets"] = [sets, pontos]
    if tipo == "evento":
        session["ultimo_pack_rarity"] = evento_id
    else:
        session["ultimo_pack_rarity"] = tipo

    return redirect(url_for("main.resultado_pack"))

# Mostrar pacotes =================================
@main.route("/resultado-pack")
def resultado_pack():
    if "ultimo_pack" not in session:
        return redirect(url_for("main.home"))
    
    connection = get_db_connection()
    if connection is None:
        return "Erro ao conectar ao banco de dados.", 500

    repo = UserRepository(connection)
    ctll = UserController(repo)

    user = ctll.get_user(session["usuario_id"])

    cartas = session.pop("ultimo_pack")
    rarity = session.pop("ultimo_pack_rarity")
    pontos = session.pop("pontos_obtidos")
    xp_obtido = session.pop("xp_obtido")
    sets, pontos_sets = session.pop("sets")

    user, level_uped = sum_xp(user, xp_obtido)
    ctll.edit_user(id=user['id'], user=user)
    
    return render_template("resultado.html", cartas = cartas, user = user, tipo_pack=rarity, pontos=pontos, sets=sets, pontos_sets=pontos_sets, xp_obtido=xp_obtido, xp_final=user['xp'], nivel=user['nivel'], level_uped=level_uped)


# Inventario =================================
@main.route("/inventario")
def inventario():
    connection = get_db_connection()
    if connection is None:
        return "Erro ao conectar ao banco de dados.", 500

    repo = UserRepository(connection)
    ctll = UserController(repo)

    user = ctll.get_user(session["usuario_id"])

    cartas = formatar_inventario(connection, user['id'])

    mostrar_todas = request.args.get("all", "0") == "1"
    return render_template('inventario.html', user = user, mostrar_todas = mostrar_todas, cartas=cartas)

# Coleções =========================================
@main.route("/collection")
def collection():
    connection = get_db_connection()
    if connection is None:
        return "Erro ao conectar ao banco de dados.", 500

    repo = UserRepository(connection)
    ctll = UserController(repo)

    user = ctll.get_user(session["usuario_id"])

    sets_usuario  = listar_sets_usuario(connection, user['id'])

    return render_template('collection.html', user = user, sets =sets_usuario)

@main.route("/deck-builder")
def deck_builder():
    connection = get_db_connection()
    if connection is None:
        return "Erro ao conectar ao banco de dados.", 500
    cartas = formatar_inventario(connection, session["usuario_id"])
    deck = get_deck(connection)
    return render_template('deck_builder.html', cartas=cartas, deck=deck)

@main.route("/save-deck", methods=["POST"])
def save_deck():
    connection = get_db_connection()
    if connection is None:
        return "Erro ao conectar ao banco de dados.", 500
    deck_json = request.form.get("deck_data")
    
    save_deck_progress(connection, deck_json)

    return redirect(url_for("main.inventario"))

# LOJINHAAAAAA =======================================
@main.route("/loja")
def loja():
    connection = get_db_connection()
    if connection is None:
        return "Erro ao conectar ao banco de dados.", 500

    repo = UserRepository(connection)
    ctll = UserController(repo)

    user = ctll.get_user(session["usuario_id"])

    ev = get_eventos_ativos()
    imgs = icon_view(connection, user["id"], user["nivel"], ev["id"] if ev else None)

    prom = get_promocoes()
    prom_log = get_user_prom_logs(connection, user["id"])

    return render_template('loja.html', user = user, ev=ev, proms=prom, prom_log=prom_log, imgs=imgs)

@main.route("/comprar-pack", methods=["POST"])
def comprar_pack():
    data = request.get_json()
    tipo = data.get("tipo")
    pacote = data.get("pacote", None)
    buy_with_impetos = data.get("buy_with_impetos")
    id = data.get("id")

    connection = get_db_connection()
    if connection is None:
        return "Erro ao conectar ao banco de dados.", 500

    repo = UserRepository(connection)
    ctll = UserController(repo)

    user = ctll.get_user(session["usuario_id"])

    if not user:
        return {"success": False, "erro": "Usuário não encontrado"}

    preco = 0
    msg = "Compra realizada!"
    # 💰 regra de compra
    if tipo == "comum":
        preco = 100
        user["packs_comprados_comum"] += 1
    elif tipo == "raro":
        preco = 500
        user["packs_comprados_raro"] +=1
    elif tipo == "bonus":
        user["pontos"] += 50
        user["has_already_get_daily_bonus"] = True
        msg = "Bônus resgatado!"
    elif tipo == "especial":
        preco = 300
        user["packs_evento"] += 1
    elif tipo == 'pontos':
        preco = 1
        user["pontos"] += 300
    elif tipo == 'pontos2k':
        preco = 3
        user["pontos"] += 1000
    elif tipo == 'icone':
        imgs = get_img_logos()
        img = next(i for i in imgs if i["id"] == id)
        preco = img["price"]
        get_new_img(connection, user["id"], id)
        msg = "Icone " + img["nome"] + ' adquirido!'
    elif tipo == 'promotion_pack':
        preco, pontos, cartas = comprar_pack_prom(user['id'], pacote, connection)
        user = registry_cards(connection, cartas, "none", user)
        if pontos > 0:
            user["pontos"] += pontos
        msg = "Pack promocional adquirido!"

    if buy_with_impetos:
        user["impetos"] -= preco
    else:
        user["pontos"] -= preco

    ctll.edit_user(user['id'], user)

    return {
        "success": True,
        "pontos": user["pontos"],
        "msg": msg
    }


# Configurações =========================================
@main.route("/settings")
def settings():
    connection = get_db_connection()
    if connection is None:
        return "Erro ao conectar ao banco de dados.", 500

    repo = UserRepository(connection)
    ctll = UserController(repo)

    user = ctll.get_user(session["usuario_id"])

    inv = user_get_inventory(connection, user["id"])

    return render_template('settings.html', user = user, inv= inv)

@main.route("/atualizar-nome", methods=["POST"])
def atualizar_nome():
    connection = get_db_connection()
    if connection is None:
        return "Erro ao conectar ao banco de dados.", 500

    repo = UserRepository(connection)
    ctll = UserController(repo)


    novo_nome = request.form.get("novo_nome")

    ctll.set_nome(session["usuario_id"], novo_nome)

    return redirect(url_for("main.settings"))

@main.route("/atualizar-foto", methods=["POST"])
def atualizar_foto():
    connection = get_db_connection()
    if connection is None:
        return "Erro ao conectar ao banco de dados.", 500

    repo = UserRepository(connection)
    ctll = UserController(repo)

    data = request.get_json()
    img = data.get("imagem")

    ctll.set_foto(session["usuario_id"], img)

    return {"status": "ok"}


# BATALHAS
import uuid
@main.route("/buscar-partida")
def buscar_partida():
    user_id = session["usuario_id"]

    # procurar sala disponível
    for room_id, room in salas.items():
        if len(room["players"]) == 1:
            room["players"].append({"id": user_id, "ready": False})
            room["status"] = "full"
            return redirect(url_for("main.aguardando", room_id=room_id))

    # nenhuma sala → criar nova
    room_id = str(uuid.uuid4())

    salas[room_id] = {
        "players": [
            {"id": user_id, "ready": False}
        ],
        "status": "waiting"
    }
    return redirect(url_for("main.aguardando", room_id=room_id))

@main.route("/aguardando/<room_id>")
def aguardando(room_id):
    connection = get_db_connection()
    if connection is None:
        return "Erro ao conectar ao banco de dados.", 500

    repo = UserRepository(connection)
    ctll = UserController(repo)

    user = ctll.get_user(session["usuario_id"])
    return render_template("waiting.html", room_id=room_id, user=user)

@main.route("/battle/<room_id>")
def battle(room_id):
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
        'discarted': []
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

@socketio.on("join_room")
def handle_join(data):
    room_id = data["room_id"]
    user_id = data["user_id"]

    join_room(room_id)

    room = salas.get(room_id)

    emit("room_update", room, to=room_id)

@socketio.on("player_ready")
def handle_ready(data):
    room_id = data["room_id"]
    user_id = data["user_id"]
    room = salas.get(room_id)
    for p in room["players"]:
        if int(p["id"]) == int(user_id):
            print('veio')
            p["ready"] = True
    emit("room_update", room, to=room_id)

    # se todos prontos → iniciar
    if len(room["players"]) == 2 and all(p["ready"] for p in room["players"]):
        emit("start_game", {"room_id": room_id}, to=room_id)


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

    # cria dict se não existir
    if "selected_cards" not in room:
        room["selected_cards"] = {}

    room["selected_cards"][user_id] = format_carta(card_id)

    print(room["selected_cards"])

    # verifica se os 2 escolheram
    if len(room["selected_cards"]) == 2:
        print(room["game_state"])
        room["game_state"]["phase"] = "battle"

        emit("start_battle", {
            "game_state_phase": room["game_state"]["phase"],
            "selected_cards": room["selected_cards"]
        }, to=room_id)

# LOGOFF =========================================
@main.route("/sair")
def logoff():
    session.pop("usuario_id")
    return redirect(url_for('main.login'))


# LOGIN ==============================================
@main.before_request
def verificar_usuario():
    rotas_livres = ["main.login", "main.registrar", "static", "main.registro"]

    if 'usuario_id' not in session:
        if request.endpoint not in rotas_livres:
            return redirect(url_for('main.login'))

    else:
        connection = get_db_connection()
        if connection is None:
            return "Erro ao conectar ao banco de dados.", 500

        repo = UserRepository(connection)
        ctll = UserController(repo)

        user = ctll.get_user(session["usuario_id"])

        if user is None:
            session.clear()
            return redirect(url_for('main.login'))
        
@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")

        connection = get_db_connection()
        if connection is None:
            return "Erro ao conectar ao banco de dados.", 500

        repo = UserRepository(connection)
        ctll = UserController(repo)

        user = ctll.find_user(email)
        if user is None:
            return render_template("login.html", erro="Usuário não encontrado")
        
        if not check_password_hash(user["senha"], senha):
            return render_template("login.html", erro="Senha incorreta")
        
        if user:
            session["usuario_id"] = user["id"]
            return redirect(url_for("main.home"))
        
    return render_template("login.html")

@main.route("/registrar", methods=["GET"])
def registro():
    return render_template("registro.html")

@main.route("/registrar", methods=["GET", "POST"])
def registrar():
    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        senha = request.form.get("senha")
        confirmar = request.form.get("confirmar_senha")

        connection = get_db_connection()
        if connection is None:
            return "Erro ao conectar ao banco de dados.", 500

        repo = UserRepository(connection)
        ctll = UserController(repo)

        # ❌ validar senha
        if senha != confirmar:
            return render_template("registro.html", erro="As senhas não coincidem")

        if len(senha) < 4:
            return render_template("registro.html", erro="Senha muito curta")

        # ❌ email já existe
        if ctll.check_email(email):
            return render_template("registro.html", erro="Email já cadastrado")
        # 🔐 hash da senha
        senha_hash = generate_password_hash(senha)

        has_event = 0 
        if get_eventos_ativos(): 
            has_event = 1
        
        user = {
            "nome": nome,
            "email": email,
            "senha": senha_hash,
            "ultimo_login": datetime.now().strftime("%Y-%m-%d"),
            "packs_evento": has_event
        }
        
        usuario_id = ctll.create_user(user)
        get_new_img(connection, usuario_id, "f1")
        get_new_img(connection, usuario_id, "f2")
        # 🔓 login automático
        session["usuario_id"] = usuario_id

        return redirect(url_for("main.home"))

    return render_template("registro.html")

@main.route("/ping")
def ping():
    return "ok", 200