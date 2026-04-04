from flask import Flask
from waitress import serve
from routes import main


app = Flask(__name__)
app.secret_key = "chave_secretissima"
app.register_blueprint(main)

if __name__ == '__main__':
    app.run('0.0.0.0', debug=True, port=5000)
    #serve(app, host='0.0.0.0', port=5000)