from utils.json_utils import get_icons, get_themes
from sql.controller.progress_controller import ProgressController
from sql.repositories.progress_repository import ProgressRepository

# INVENTÁRIOS ==================================================
def get_img_logos():
    imgs = get_icons()
    return imgs

def user_get_inventory(conn, user_id):
    repo = ProgressRepository(conn)
    ctll = ProgressController(repo)
    
    icons = get_icons()
    user_inv = ctll.get_user_icons(user_id)
    icons_user = []

    for icon in icons:
        possui = str(icon["id"]) in user_inv
        icons_user.append({
            **icon,
            "possui": possui
        })
    return icons_user

def icon_view(conn, user_id, nivel, event, lang):
    repo = ProgressRepository(conn)
    ctll = ProgressController(repo)

    icons = get_icons()
    user_inv = ctll.get_user_icons(user_id)
    progress = ctll.get_all_sets(user_id)

    result = []

    for icon in icons:
        possui = str(icon["id"]) in user_inv
        unlock = icon.get("unlock",{"type":"free"})
        disponivel = False

        if unlock["type"] == "free" or unlock["type"] == "purchase":
            disponivel = True
        elif unlock["type"] == "set":
            if unlock["value"] in progress:
                disponivel = True
        elif unlock["type"] == "event":
            if event == unlock["value"]:
                disponivel = True
        elif unlock["type"] == "nivel":
            if unlock["value"] <= nivel:
                disponivel = True

        result.append({
            "id": icon['id'],
            "nome": icon["lang"][lang]["nome"],
            "descricao": icon["lang"][lang]["descricao"],
            "img": icon['img'],
            "price": icon['price'],
            "rarity": icon['rarity'],
            "possui": possui,
            "disponivel": disponivel
        })

    return result

def themes_view(lang, temas):
    themes = get_themes()
    result = []
    for theme in themes:
        possui = str(theme["id"]) in temas
        unlock = theme.get("unlock",{"type":"free"})
        disponivel = False

        if unlock["type"] == "free" or unlock["type"] == "purchase":
            disponivel = True
        
        result.append({
            "id": theme['id'],
            "nome": theme["lang"][lang]["nome"],
            "descricao": theme["lang"][lang]["descricao"],
            "price": theme['price'],
            "rarity": theme['rarity'],
            "preview": theme['preview'],
            "possui": possui,
            "disponivel": disponivel
        })
    return result

def get_new_img(conn, user_id, img_id):
    repo = ProgressRepository(conn)
    ctll = ProgressController(repo)

    ctll.set_icon(user_id, img_id)