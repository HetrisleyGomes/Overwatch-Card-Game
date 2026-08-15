from flask import blueprints, send_from_directory
from server import app

documents = blueprints.Blueprint('documents', __name__, static_folder='static', template_folder='templates')

@documents.route("/llms.txt")
def llms():
    return send_from_directory(app.static_folder, "llms.txt")

@documents.route("/robots.txt")
def robots():
    return send_from_directory(app.static_folder, "robots.txt")

@documents.route("/sitemap.xml")
def sitemap():
    return send_from_directory(app.static_folder, "sitemap.xml")