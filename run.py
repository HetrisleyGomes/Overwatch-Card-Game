from server import app, socketio
from routes.routes import main
from routes.routescombate import combate
from routes.routesdocs import documents

app.secret_key = "chave_secretissima"
app.register_blueprint(main)
app.register_blueprint(combate)
app.register_blueprint(documents)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True, port=5000, allow_unsafe_werkzeug=True)