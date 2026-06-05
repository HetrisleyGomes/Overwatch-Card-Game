from server import app, socketio
from waitress import serve
from routes import main
from routescombate import combate

app.secret_key = "chave_secretissima"
app.register_blueprint(main)
app.register_blueprint(combate)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True, port=5000, allow_unsafe_werkzeug=True)
    #serve(app, host='0.0.0.0', port=5000)
