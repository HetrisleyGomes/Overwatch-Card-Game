from flask import blueprints, render_template, request, session, redirect, url_for
from services.user_service import criar_usuario, carregar_usuarios, verify_date, salvar_usuarios, sum_xp,get_img_logos, user_get_inventory, icon_view, get_new_img
from services.progress_service import registry_cards, save_deck_progress, get_deck
from services.pack_sevice import abrir_pack, abrir_pack_evento
from services.collection_service import verificar_sets, formatar_inventario, listar_sets_usuario
from services.eventos_service import check_event_activation, get_eventos_ativos, get_last_log
from services.loja_services import get_promocoes, set_promocoes, comprar_pack_prom
from server import socketio

from flask_socketio import join_room, emit
from werkzeug.security import check_password_hash, generate_password_hash

main = blueprints.Blueprint('main', __name__, static_folder='static', template_folder='templates')

salas = {}  

# Rota principal ========================================
@main.route('/')
def home():
    usuarios = carregar_usuarios()
    user = next((u for u in usuarios if u["id"] == session["usuario_id"]), None)

    check_event_activation()
    ev = get_eventos_ativos()
    ev_validator = False
    if ev:
        ev_validator = True

    verify_date(usuarios, user, ev_validator)

    log = get_last_log()
    prom = get_promocoes()

    return render_template('home.html', user=user, ev=ev, log=log, proms=prom if prom else None)

# Abrir pacote ========================================
@main.route("/abrir-pack-comum", methods=["POST"])
def abrir_pack_route():
    if request.method != "POST":
        return redirect(url_for("main.home"))
    
    cartas = abrir_pack("comum")

    registry_cards(cartas, "comum")

    sets, pontos = verificar_sets()

    session["ultimo_pack"] = cartas
    session["ultimo_pack_rarity"] = "comum"
    session["sets"] = [sets, pontos]

    return redirect(url_for("main.resultado_pack"))

@main.route("/abrir-pack-raro", methods=["POST"])
def abrir_pack_raro_route():
    if request.method != "POST":
        return redirect(url_for("main.home"))
    
    cartas = abrir_pack("raro")

    registry_cards(cartas, "raro")

    sets, pontos = verificar_sets()

    session["ultimo_pack"] = cartas
    session["ultimo_pack_rarity"] = "raro"
    session["sets"] = [sets, pontos]

    return redirect(url_for("main.resultado_pack"))

@main.route("/abrir-pack-evento", methods=["POST"])
def abrir_pack_evento_route():
    if request.method != "POST":
        return redirect(url_for("main.home"))
    evento_id = request.form.get("evento_id")

    cartas = abrir_pack_evento(evento_id)

    registry_cards(cartas, "especial")
    sets, pontos = verificar_sets()
    session["ultimo_pack"] = cartas
    session["ultimo_pack_rarity"] = evento_id
    session["sets"] = [sets, pontos]
    
    return redirect(url_for("main.resultado_pack"))

# Mostrar pacotes =================================
@main.route("/resultado-pack")
def resultado_pack():
    if "ultimo_pack" not in session:
        return redirect(url_for("main.home"))
    
    usuarios = carregar_usuarios()
    user = next((u for u in usuarios if u["id"] == session["usuario_id"]), None)

    cartas = session.pop("ultimo_pack")
    rarity = session.pop("ultimo_pack_rarity")
    pontos = session.pop("pontos_obtidos")
    xp_obtido = session.pop("xp_obtido")
    sets, pontos_sets = session.pop("sets")

    xp_final, nivel, level_uped = sum_xp(user["id"], xp_obtido)

    return render_template("resultado.html", cartas = cartas, user = user, tipo_pack=rarity, pontos=pontos, sets=sets, pontos_sets=pontos_sets, xp_obtido=xp_obtido, xp_final=xp_final, nivel=nivel, level_uped=level_uped)


# Inventario =================================
@main.route("/inventario")
def inventario():
    usuarios = carregar_usuarios()
    user = next((u for u in usuarios if u["id"] == session["usuario_id"]), None)

    cartas = formatar_inventario()

    mostrar_todas = request.args.get("all", "0") == "1"
    return render_template('inventario.html', user = user, mostrar_todas = mostrar_todas, cartas=cartas)

# Coleções =========================================
@main.route("/collection")
def collection():
    usuarios = carregar_usuarios()
    user = next((u for u in usuarios if u["id"] == session["usuario_id"]), None)

    sets_usuario  = listar_sets_usuario()

    return render_template('collection.html', user = user, sets =sets_usuario)

@main.route("/deck-builder")
def deck_builder():
    cartas = formatar_inventario()
    deck = get_deck()
    return render_template('deck_builder.html', cartas=cartas, deck=deck)

@main.route("/save-deck", methods=["POST"])
def save_deck():
    deck_json = request.form.get("deck_data")
    
    save_deck_progress(deck_json)

    return redirect(url_for("main.inventario"))

# LOJINHAAAAAA =======================================
@main.route("/loja")
def loja():
    usuarios = carregar_usuarios()
    user = next((u for u in usuarios if u["id"] == session["usuario_id"]), None)

    ev = get_eventos_ativos()
    imgs = icon_view(user["id"], user["nivel"], ev["id"] if ev else None)

    prom = get_promocoes()

    return render_template('loja.html', user = user, ev=ev, proms=prom, imgs=imgs)

@main.route("/comprar-pack", methods=["POST"])
def comprar_pack():
    data = request.get_json()
    tipo = data.get("tipo")
    pacote = data.get("pacote", None)
    buy_with_impetos = data.get("buy_with_impetos")
    id = data.get("id")

    usuarios = carregar_usuarios()
    user = next((u for u in usuarios if u["id"] == session["usuario_id"]), None)

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
        get_new_img(user["id"], id)
        msg = "Icone " + img["nome"] + ' adquirido!'
    elif tipo == 'promotion_pack':
        preco, pontos = comprar_pack_prom(user['id'], pacote)
        if pontos > 0:
            user["pontos"] += pontos
        msg = "Pack promocional adquirido!"

    if buy_with_impetos:
        user["impetos"] -= preco
    else:
        user["pontos"] -= preco

    salvar_usuarios(usuarios)

    return {
        "success": True,
        "pontos": user["pontos"],
        "msg": msg
    }


# Configurações =========================================
@main.route("/settings")
def settings():
    usuarios = carregar_usuarios()
    user = next((u for u in usuarios if u["id"] == session["usuario_id"]), None)

    inv = user_get_inventory(user["id"])

    return render_template('settings.html', user = user, inv= inv)

@main.route("/atualizar-nome", methods=["POST"])
def atualizar_nome():
    novo_nome = request.form.get("novo_nome")

    usuarios = carregar_usuarios()
    user = next(u for u in usuarios if u["id"] == session["usuario_id"])

    user["nome"] = novo_nome
    salvar_usuarios(usuarios)

    return redirect(url_for("main.settings"))

@main.route("/atualizar-foto", methods=["POST"])
def atualizar_foto():
    data = request.get_json()
    img = data.get("imagem")
    usuarios = carregar_usuarios()
    user = next(u for u in usuarios if u["id"] == session["usuario_id"])

    user["profile_img"] = img
    salvar_usuarios(usuarios)

    return {"status": "ok"}


# BATALHAS
import uuid
@main.route("/buscar-partida")
def buscar_partida():
    user_id = session["usuario_id"]

    # procurar sala disponível
    for room_id, room in salas.items():
        if len(room["players"]) == 1:
            room["players"].append(user_id)
            room["status"] = "full"
            return redirect(url_for("main.battle", room_id=room_id))

    # nenhuma sala → criar nova
    room_id = str(uuid.uuid4())

    salas[room_id] = {
        "players": [user_id],
        "status": "waiting"
    }

    return redirect(url_for("main.aguardando", room_id=room_id))

@main.route("/aguardando/<room_id>")
def aguardando(room_id):
    return render_template("waiting.html", room_id=room_id)

@main.route("/battle/<room_id>")
def battle(room_id):
    return render_template("battle.html", room_id=room_id)

@socketio.on("join")
def on_join(data):
    room_id = data["room"]
    user_id = session["usuario_id"]

    join_room(room_id)

    room = salas.get(room_id)

    if room and len(room["players"]) == 2:
        emit("start_game", {"room": room_id}, room=room_id)

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
        usuarios = carregar_usuarios()
        usuario = next((u for u in usuarios if u["id"] == session['usuario_id']), None)

        if usuario is None:
            session.clear()
            return redirect(url_for('main.login'))
        
@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")

        usuarios = carregar_usuarios()

        usuario = next((u for u in usuarios if u["email"] == email), None)

        if usuario is None:
            return render_template("login.html", erro="Usuário não encontrado")
        
        if not check_password_hash(usuario["senha"], senha):
            return render_template("login.html", erro="Senha incorreta")
        
        if usuario:
            session["usuario_id"] = usuario["id"]
            return redirect(url_for("main.home"))
        
        session["usuario_id"] = usuario["id"]
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

        usuarios = carregar_usuarios()

        # ❌ validar senha
        if senha != confirmar:
            return render_template("registrar.html", erro="As senhas não coincidem")

        if len(senha) < 4:
            return render_template("registrar.html", erro="Senha muito curta")

        # ❌ email já existe
        if any(u["email"] == email for u in usuarios):
            return render_template("registrar.html", erro="Email já cadastrado")
        # 🔐 hash da senha
        senha_hash = generate_password_hash(senha)

        has_event = 0 
        if get_eventos_ativos(): 
            has_event = 1

        usuario_id = criar_usuario(nome, email, senha_hash, has_event)

        # 🔓 login automático
        session["usuario_id"] = usuario_id

        return redirect(url_for("main.home"))

    return render_template("registrar.html")