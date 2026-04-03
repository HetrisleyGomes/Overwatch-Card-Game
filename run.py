from flask import Flask
from routes import main


app = Flask(__name__)
app.secret_key = "chave_secretissima"

if __name__ == '__main__':
    app.register_blueprint(main)
    app.run('0.0.0.0', debug=True, port=5000)