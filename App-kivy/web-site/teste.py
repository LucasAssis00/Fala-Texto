from flask import Flask, render_template, request, jsonify, send_file
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import uuid
import numpy as np
import datetime


# Gerando uma chave secreta aleatória para autenticação JWT
secret_key = os.urandom(32)
hash_senha = generate_password_hash("Transcrição_de_fala_em_texto_api")
hash_senha2 = generate_password_hash("Transcrição_de_fala_api")

# Inicializando o aplicativo Flask
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = secret_key
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(hours=6) # Definindo o tempo de expiração do token JWT
app.config['UPLOAD_FOLDER'] = 'uploads'  # Diretório 
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


jwt = JWTManager(app) # Inicializando gerenciamento de autenticação JWT
limiter = Limiter(app=app, key_func=get_remote_address) # Configurando o limitador de requisições

# Dicionário de usuários com senhas hash
usuarios = {
    'Fala-texto': hash_senha,
    'whisperadm': hash_senha2
}


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
    """Rota para autenticação do usuário."""
    username = request.json.get('username')
    password = request.json.get('password')
    # Verifique as credenciais do usuário aqui
    if username in usuarios and check_password_hash(usuarios[username], password):
        access_token = create_access_token(identity=str(username))
        return jsonify(access_token=access_token)
    else:
        return jsonify({"msg": "Nome de usuário ou senha incorretos"}), 401


@app.route('/upload-imagem', methods=['POST'])
@jwt_required()
@limiter.limit("10 per minute")
def upload_imagem():
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "Nome do arquivo vazio"}), 400

    # Salvar com nome único
    filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    # Aqui você pode processar a imagem, enviar para OCR, análise, etc.
    # Por agora, só retornamos uma confirmação
    return jsonify({"mensagem": "Imagem recebida com sucesso", "arquivo": filename}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)