from flask import blueprints, render_template, request, session, redirect, url_for, g, send_from_directory
from services.user_service import verify_date, sum_xp
from services.progress_service import registry_cards, save_deck_progress, get_deck
from services.pack_sevice import open_pack, open_event_pack
from services.collection_service import check_sets, format_inventory, list_user_sets, card_format
from services.events_service import get_active_events, get_last_log, is_theres_active_events
from services.store_services import get_promotion, buy_pack_promotion, get_user_infos, get_max_vault_infos, get_vault, generate_vault, buy_vault_item, get_vault_data_format, buy_theme
from services.inventory_service import get_img_logos, user_get_inventory, icon_view, get_new_img, themes_view
from services.translates import get_lang

from utils.json_utils import get_classes_lang, get_combat_tips, get_global_tips

from sql.controller.user_controller import UserController
from sql.repositories.user_repository import UserRepository
from sql.connection import get_db_connection

from server import app

from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from math import floor

main = blueprints.Blueprint('main', __name__, static_folder='static', template_folder='templates')

# Função de tradução
@app.context_processor
def inject_translations():
    lang = session.get("lang", "br")
    return {
        "_": lambda key: get_lang(lang).get(key, key)
    }


# Rota principal ========================================
@main.route('/')
def home():
    connection = get_db_connection()
    if connection is None:
        return "Erro ao conectar ao banco de dados.", 500

    repo = UserRepository(connection)
    ctll = UserController(repo)
    lang = session["lang"]

    # Event infos:
    ev_validator = False
    ev = get_active_events(lang)
    if ev:
        ev_validator = True

    # User infos:
    if "user_data" not in session:
        user_data, was_change = verify_date(ctll.get_user(session["user_id"]), ev_validator)
        if was_change:
            ctll.daily_update(user_data)
        session['user_data'] = user_data

    user = session['user_data']

    # Display infos:
    semana = floor(user['streak'] / 7)
    log = get_last_log()
    prom = get_promotion(lang)
    vault = get_max_vault_infos()
    vault_data = None
    if vault:
        vault_data = get_vault_data_format(vault)
    
    global_tips = get_global_tips(lang)

    return render_template('home.html', user=user, semana=semana, ev=ev, log=log, proms=prom, vault=vault, vault_data=vault_data, lang=lang, global_tips=global_tips)

# Abrir pacote ========================================
@main.route("/abrir-pack", methods=["POST"])
def open_pack_route():
    if request.method != "POST":
        return redirect(url_for("main.home"))
    
    # backend
    connection = get_db_connection()
    if connection is None:
        return "Erro ao conectar ao banco de dados.", 500

    lang = session['lang']
    user = session['user_data']

    # obtem informações do form
    type = request.form.get("tipo")
    event_id = request.form.get("evento_id")

    # Lógica das cartas
    if type == "evento":
        cartas = open_event_pack(event_id, lang)
    else:
        cartas = open_pack(type, lang)

    user = registry_cards(connection, cartas, type, user)
    sets, points = check_sets(connection, user['id'], lang)
    user['pontos'] += points
    update_user(connection, user)

    session["ultimo_pack"] = cartas
    session["sets"] = [sets, points]
    if type == "evento":
        session["ultimo_pack_rarity"] = event_id
    else:
        session["ultimo_pack_rarity"] = type

    return redirect(url_for("main.result_pack"))

# Mostrar pacotes =================================
@main.route("/resultado-pack")
def result_pack():
    if "ultimo_pack" not in session:
        return redirect(url_for("main.home"))
    
    connection = get_db_connection()
    if connection is None:
        return "Erro ao conectar ao banco de dados.", 500

    user = session['user_data']

    cards = session.pop("ultimo_pack")
    rarity = session.pop("ultimo_pack_rarity")
    points = session.pop("pontos_obtidos")
    xp_gained = session.pop("xp_obtido")
    sets, sets_points = session.pop("sets")

    user, level_uped = sum_xp(user, xp_gained)
    update_user(connection, user)
    
    return render_template("resultado.html", cartas = cards, user = user, tipo_pack=rarity, pontos=points, sets=sets, pontos_sets=sets_points, xp_obtido=xp_gained, xp_final=user['xp'], nivel=user['nivel'], level_uped=level_uped)


# Inventario =================================
@main.route("/inventory")
def inventory():
    connection = get_db_connection()
    if connection is None:
        return "Erro ao conectar ao banco de dados.", 500

    user = session['user_data']
    lang = session['lang']
    cards = format_inventory(connection, user['id'], lang)

    show_all = request.args.get("all", "0") == "1"
    global_tips = get_global_tips(lang, "inventory")
    classes_tips = get_classes_lang(lang)
    combate_tips = get_combat_tips(lang)
    
    return render_template('inventario.html', user = user, mostrar_todas = show_all, cartas=cards, global_tips=global_tips, classes_tips= classes_tips, combate_tips= combate_tips)

# Coleções =========================================
@main.route("/collection")
def collection():
    connection = get_db_connection()
    if connection is None:
        return "Erro ao conectar ao banco de dados.", 500

    user = session['user_data']
    lang = session["lang"]
    sets_usuario  = list_user_sets(connection, user['id'], lang)
    global_tips = get_global_tips(lang, "collections")

    return render_template('collection.html', user = user, sets =sets_usuario, global_tips=global_tips)

@main.route("/deck-builder")
def deck_builder():
    connection = get_db_connection()
    if connection is None:
        return "Erro ao conectar ao banco de dados.", 500
    
    lang = session["lang"]
    cards = format_inventory(connection, session["user_id"],lang)
    deck = get_deck(connection)

    return render_template('deck_builder.html', cartas=cards, deck=deck)

@main.route("/save-deck", methods=["POST"])
def save_deck():
    connection = get_db_connection()
    if connection is None:
        return "Erro ao conectar ao banco de dados.", 500
    
    deck_json = request.form.get("deck_data")
    save_deck_progress(connection, deck_json)

    return redirect(url_for("main.inventory"))

# LOJINHAAAAAA =======================================
@main.route("/store")
def store():
    connection = get_db_connection()
    if connection is None:
        return "Erro ao conectar ao banco de dados.", 500

    user = session['user_data']
    lang = session["lang"]

    event = get_active_events(lang)
    imgs = icon_view(connection, user["id"], user["nivel"], event["id"] if event else None, lang)

    themes_log = get_user_infos(connection, user["id"], 'theme')
    themes = themes_view(lang, themes_log)

    prom = get_promotion(lang)
    prom_log = get_user_infos(connection, user["id"], 'promotion')

    max_is_here = True if get_max_vault_infos() else False
    global_tips = get_global_tips(lang, "store")

    return render_template('loja.html', user = user, ev=event, proms=prom, prom_log=prom_log, imgs=imgs, themes=themes, themes_log=themes_log, max_is_here= max_is_here, global_tips=global_tips)

@main.route("/comprar-pack", methods=["POST"])
def buy_store_item():
    data = request.get_json()
    type = data.get("tipo")
    pack = data.get("pacote", None)
    buy_with_impetos = data.get("buy_with_impetos")
    id_item = data.get("id")

    connection = get_db_connection()
    if connection is None:
        return "Erro ao conectar ao banco de dados.", 500

    user = session['user_data']
    lang = session["lang"]

    if not user:
        return {"success": False, "erro": "Usuário não encontrado"}

    price = 0
    msg = "Compra realizada!"
    # 💰 regra de compra
    if type == "comum":
        price = 100
        user["packs_comprados_comum"] += 1
    elif type == "raro":
        price = 500
        user["packs_comprados_raro"] +=1
    elif type == "bonus":
        user["pontos"] += 50
        user["has_already_get_daily_bonus"] = True
        msg = "Bônus resgatado!"
    elif type == "especial":
        price = 300
        user["packs_evento"] += 1
    elif type == 'pontos':
        price = 1
        user["pontos"] += 300
    elif type == 'pontos2k':
        price = 3
        user["pontos"] += 1000
    elif type == 'icone':
        imgs = get_img_logos()
        img = next(i for i in imgs if i["id"] == id_item)
        price = img["price"]
        get_new_img(connection, user["id"], id_item)
        msg = "Icone " + img["lang"][lang]["nome"] + ' adquirido!'
    elif type == 'promotion_pack':
        price, pontos, cartas, icons = buy_pack_promotion(user['id'], pack, connection)
        user = registry_cards(connection, cartas, "none", user)
        if icons:
            for icon_id in icons:
                get_new_img(connection, user["id"], icon_id)
        if pontos > 0:
            user["pontos"] += pontos
        msg = "Pack promocional adquirido!"
    elif type == 'theme':
        price = buy_theme(user['id'], id_item, connection)

    if buy_with_impetos:
        user["impetos"] -= price
    else:
        user["pontos"] -= price

    update_user(connection, user)

    return {
        "success": True,
        "pontos": user["pontos"],
        "msg": msg
    }

@main.route("/maximilien-vault")
def maximilien():
    connection = get_db_connection()
    if connection is None:
       return "Erro ao conectar ao banco de dados.", 500

    user = session['user_data']
    lang = session['lang']

    cards = []
    current_vault = get_max_vault_infos()
    cards_raw = get_vault(connection, user['id'], current_vault)

    if cards_raw is None:
        return "Erro ao carregar o cofre do Maximilien.", 500

    if len(cards_raw) == 0:
        cards_raw = generate_vault(connection, user['id'], current_vault)

    for card in cards_raw:
        data = card_format(card[0], lang)
        data['has_purshased'] = card[1]
        cards.append(data)

    vault_data = get_vault_data_format(current_vault)
    global_tips = get_global_tips(lang, 'vault')
    return render_template('vault.html', user = user, cartas=cards, vault_data=vault_data, lang=lang, global_tips=global_tips)


@main.route("/comprar-carta-vault", methods=["POST"])
def buy_vault_card():
    data = request.get_json()
    card_id = data.get("id")
    connection = get_db_connection()
    if connection is None:
        return "Erro ao conectar ao banco de dados.", 500

    user = session["user_data"]
    lang = session['lang']

    if not user:
        return {"success": False, "erro": "Usuário não encontrado"}

    price = 1000
    msg = "Agradeço a sua compra!"

    user = registry_cards(connection, [card_format(card_id, lang)], "none", user)
    buy_vault_item(connection, user['id'], card_id)
    user["pontos"] -= price
    update_user(connection, user)

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

    user = session["user_data"]
    
    inventory = user_get_inventory(connection, user["id"])
    lang = session["lang"]
    global_tips = get_global_tips(lang, "settings")

    return render_template('settings.html', user = user, inv=inventory, lang=lang, global_tips=global_tips)

@main.route("/atualizar-nome", methods=["POST"])
def update_name():
    connection = get_db_connection()
    if connection is None:
        return "Erro ao conectar ao banco de dados.", 500

    repo = UserRepository(connection)
    ctll = UserController(repo)

    new_name = request.form.get("novo_nome")
    ctll.set_nome(session["user_id"], new_name)
    update_session_user(ctll)

    return redirect(url_for("main.settings"))

@main.route("/atualizar-lang", methods=["POST"])
def update_lang():
    connection = get_db_connection()
    if connection is None:
        return "Erro ao conectar ao banco de dados.", 500

    repo = UserRepository(connection)
    ctll = UserController(repo)

    new_lang = request.form.get("lang")
    session["lang"] = new_lang
    ctll.set_lang(session["user_id"], new_lang)
    update_session_user(ctll)

    return redirect(url_for("main.settings"))

@main.route("/atualizar-foto", methods=["POST"])
def update_profile_icon():
    connection = get_db_connection()
    if connection is None:
        return "Erro ao conectar ao banco de dados.", 500

    repo = UserRepository(connection)
    ctll = UserController(repo)

    data = request.get_json()
    new_img = data.get("imagem")

    ctll.set_foto(session["user_id"], new_img)
    update_session_user(ctll)

    return {"status": "ok"}

@main.route("/atualizar-tema", methods=["POST"])
def update_theme():
    connection = get_db_connection()
    if connection is None:
        return "Erro ao conectar ao banco de dados.", 500

    repo = UserRepository(connection)
    ctll = UserController(repo)

    data = request.get_json()
    new_theme = data.get("tema")

    ctll.set_tema(session["user_id"], new_theme)
    update_session_user(ctll)

    return {"status": "ok"}

# EXCLUIR CONTA =======================================
@main.route("/excluir-perfil", methods=["POST"])
def delete_account():
    connection = get_db_connection()
    if connection is None:
        return "Erro ao conectar ao banco de dados.", 500

    repo = UserRepository(connection)
    ctll = UserController(repo)

    user = session["user_data"]
    ctll.delete_user(user['id'])

    session.pop("user_id")
    session.pop('user_data')
    return redirect(url_for('main.login'))

# LOGOFF =========================================
@main.route("/sair")
def logoff():
    session.pop("user_id")
    session.pop('user_data')
    return redirect(url_for('main.login'))


# LOGIN ==============================================
@main.before_request
def verify_user():
    open_routes = ["main.login", "main.sign_in", "static", "main.register", "main.ping", "main.robots"]

    if 'user_id' not in session:
        if request.endpoint not in open_routes:
            return redirect(url_for('main.login'))
        
@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = str(request.form.get("senha"))

        connection = get_db_connection()
        if connection is None:
            return "Erro ao conectar ao banco de dados.", 500

        repo = UserRepository(connection)
        ctll = UserController(repo)

        user = ctll.find_user(email)
        if user is None or user == "'NoneType' object is not iterable":
            return render_template("login.html", erro="Usuário não encontrado")
        
        if not check_password_hash(user["senha"], password):
            return render_template("login.html", erro="Senha incorreta")
        
        if user:
            session["user_id"] = user["id"]
            session["lang"] = user["language"]
            return redirect(url_for("main.home"))
        
    return render_template("login.html")

@main.route("/registrar", methods=["GET"])
def sign_in():
    return render_template("registro.html")

@main.route("/registrar", methods=["POST"])
def register():
    if request.method == "POST":
        name = request.form.get("nome")
        email = request.form.get("email")
        password = request.form.get("senha")
        lang = request.form.get("lang")
        password_confirm = request.form.get("confirmar_senha")

        connection = get_db_connection()
        if connection is None:
            return "Erro ao conectar ao banco de dados.", 500

        repo = UserRepository(connection)
        ctll = UserController(repo)

        # validar senha
        if password != password_confirm:
            return render_template("registro.html", erro="As senhas não coincidem")

        if len(password) < 4:
            return render_template("registro.html", erro="Senha muito curta")

        # email já existe
        if ctll.check_email(email):
            return render_template("registro.html", erro="Email já cadastrado")
        # hash da senha
        password_hash = generate_password_hash(password)

        has_event = 0 
        if is_theres_active_events(): 
            has_event = 1
        
        user = {
            "nome": name,
            "email": email,
            "senha": password_hash,
            "lang": lang,
            "ultimo_login": datetime.now().strftime("%Y-%m-%d"),
            "packs_evento": has_event
        }
        
        user_id = ctll.create_user(user)
        get_new_img(connection, user_id, "f1")
        get_new_img(connection, user_id, "f2")
        buy_theme(user_id, 'default', connection)
        # login automático
        session["user_id"] = user_id
        session["lang"] = lang

        return redirect(url_for("main.home"))

    return render_template("registro.html")

@main.route("/ping")
def ping():
    return "ok", 200

@main.route("/robots.txt")
def robots():
    return send_from_directory(app.static_folder, "robots.txt")

def update_session_user(ctll):
    user = ctll.get_user(session["user_id"])
    session['user_data'] = user

def update_user(conn, user):
    repo = UserRepository(conn)
    ctll = UserController(repo)
    ctll.edit_user(user['id'], user)
    update_session_user(ctll)