from utils.json_utils import get_icons
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

def icon_view(conn, user_id, nivel, event):
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
            **icon,
            "possui": possui,
            "disponivel": disponivel
        })

    return result

def get_new_img(conn, user_id, img_id):
    repo = ProgressRepository(conn)
    ctll = ProgressController(repo)

    ctll.set_icon(user_id, img_id)