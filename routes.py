from flask import blueprints, render_template, request, session, redirect, url_for
from services.user_service import criar_usuario, carregar_usuarios, verify_date, salvar_usuarios, get_img_logos, user_get_inventory, icon_view, get_new_img
from services.progress_service import registry_cards
from services.pack_sevice import abrir_pack, abrir_pack_evento
from services.collection_service import verificar_sets, formatar_inventario, listar_sets_usuario
from services.eventos_service import check_event_activation, get_eventos_ativos

main = blueprints.Blueprint('main', __name__, static_folder='static', template_folder='templates')


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

    return render_template('home.html', user=user, ev=ev)

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
    sets, pontos_sets = session.pop("sets")

    return render_template("resultado.html", cartas = cartas, user = user, tipo_pack=rarity, pontos=pontos, sets=sets, pontos_sets=pontos_sets)


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

# LOJINHAAAAAA =======================================
@main.route("/loja")
def loja():
    usuarios = carregar_usuarios()
    user = next((u for u in usuarios if u["id"] == session["usuario_id"]), None)

    ev = get_eventos_ativos()
    imgs = icon_view(user["id"], ev["id"])

    return render_template('loja.html', user = user, ev=ev, imgs=imgs)

@main.route("/comprar-pack", methods=["POST"])
def comprar_pack():
    data = request.get_json()
    tipo = data.get("tipo")
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
    elif tipo == 'icone':
        imgs = get_img_logos()
        img = next(i for i in imgs if i["id"] == id)
        preco = img["price"]
        get_new_img(user["id"], id)
        msg = "Icone " + img["nome"] + ' adquirido!'


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
    print(img)
    usuarios = carregar_usuarios()
    user = next(u for u in usuarios if u["id"] == session["usuario_id"])

    user["profile_img"] = img
    salvar_usuarios(usuarios)

    return {"status": "ok"}

# LOGOFF =========================================
@main.route("/sair")
def logoff():
    session.pop("usuario_id")
    return redirect(url_for('main.login'))


# LOGIN ==============================================
@main.before_request
def verificar_usuario():
    rotas_livres = ["login", "criar_usuario", "static"]

    if 'usuario_id' not in session:
        if not any(r in str(request.path) for r in rotas_livres):
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
        nome = request.form["nome"]
        usuarios = carregar_usuarios()

        usuario = next((u for u in usuarios if u["nome"] == nome), None)

        if usuario:
            session["usuario_id"] = usuario["id"]
            return redirect(url_for("main.home"))
        else:
            has_event = 0
            if get_eventos_ativos():
                has_event = 1
            usuario = criar_usuario(nome, has_event)
            session["usuario_id"] = usuario
            return redirect(url_for("main.home"))

    return render_template("login.html")