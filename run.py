from server import app, socketio
from waitress import serve
from routes import main


app.secret_key = "chave_secretissima"
app.register_blueprint(main)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True, port=5000)
    #serve(socketio, host='0.0.0.0', port=5000)
