"""
from flask import Flask, request, jsonify, send_file
import fitz  # PyMuPDF
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'  # Diretório onde os arquivos serão salvos
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def listar_campos_pdf(pdf_path):
    try:
        pdf_document = fitz.open(pdf_path)
        dados = {}
        for page_num in range(pdf_document.page_count):
            page = pdf_document.load_page(page_num)
            annotations = page.widgets()
            if annotations:
                for annot in annotations:
                    #dados[(annot.field_name, annot.field_type)] = None
                    chave = f"{annot.field_name}|{annot.field_type}"
                    dados[chave] = None
        return dados
    except Exception as e:
        return {"error": str(e)}

def preencher_campos_pdf(pdf_path, output_path, data):
    try:
        pdf_document = fitz.open(pdf_path)
        for page_num in range(pdf_document.page_count):
            page = pdf_document.load_page(page_num)
            annotations = page.widgets()
            if annotations:
                for annot in annotations:
                    field_name = annot.field_name
                    for campo in data.keys():
                        if field_name == campo[0]:
                            annot.field_value = data[campo]
                            annot.update()
        pdf_document.save(output_path)
        return output_path
    except Exception as e:
        return {"error": str(e)}


@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Bem-vindo à API!"})

@app.route('/listar-campos', methods=['POST'])
def listar_campos():
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo encontrado"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Nenhum arquivo selecionado"}), 400
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    campos = listar_campos_pdf(file_path)
    os.remove(file_path)
    return jsonify(campos)

@app.route('/preencher-campos', methods=['POST'])
def preencher_campos():
    dados = {}
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo encontrado"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Nenhum arquivo selecionado"}), 400
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    output_filename = "preenchido_teste.pdf"
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
    data = request.form.to_dict()
    for c,v in data.items():
        chaves = c.split('|')
        dados[(chaves[0],int(chaves[1]))] = v
    resultado = preencher_campos_pdf(file_path, output_path, dados)
    os.remove(file_path)
    return send_file(resultado, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

"""

from flask import Flask, request, jsonify, send_file
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import fitz  # PyMuPDF
import os
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import whisper
from carregar import get_model
import uuid
import numpy as np
import librosa
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

# Carregando modelo de transcrição
modelo = get_model()


def transcricao_pdf(audio):
    try:
        result = modelo.transcribe(audio,fp16=True,language="pt")
        return result
    except Exception as e:
        return {"error": str(e)}

def listar_campos_pdf(pdf_path):
    try:
        pdf_document = fitz.open(pdf_path)
        dados = {}
        for page_num in range(pdf_document.page_count):
            page = pdf_document.load_page(page_num)
            annotations = page.widgets()
            if annotations:
                for annot in annotations:
                    #dados[(annot.field_name, annot.field_type)] = None
                    chave = f"{annot.field_name}|{annot.field_type}"
                    dados[chave] = None
        return dados
    except Exception as e:
        return {"error": str(e)}


def preencher_campos_pdf(pdf_path, output_path, data):
    try:
        pdf_document = fitz.open(pdf_path)
        for page_num in range(pdf_document.page_count):
            page = pdf_document.load_page(page_num)
            annotations = page.widgets()
            if annotations:
                for annot in annotations:
                    field_name = annot.field_name
                    for campo in data.keys():
                        if field_name == campo[0]:
                            annot.field_value = data[campo]
                            annot.update()
        pdf_document.save(output_path)
        return output_path
    except Exception as e:
        return {"error": str(e)}


def calculate_snr_speech(audio_path):
    # Carregar o arquivo de áudio
    y, sr = librosa.load(audio_path, sr=None)

    # Detectar silêncios para estimar o ruído
    intervals = librosa.effects.split(y, top_db=20)

    # Calcular a potência do sinal (somente partes faladas)
    signal_power = np.mean([np.mean(np.square(y[start:end])) for start, end in intervals])

    # Verificar se há intervalos de ruído detectados
    if len(intervals) > 1:
        noise_intervals = np.concatenate([y[i:j] for i, j in zip(intervals[:-1, 1], intervals[1:, 0])])
        noise_power = np.mean(np.square(noise_intervals))
    else:
        # Caso não haja intervalos de ruído suficientes, usar um valor padrão pequeno para evitar divisão por zero
        noise_power = np.mean(np.square(y[-int(sr*0.1):]))  # Usando os últimos 10% do áudio como ruído

    # Calcular o SNR
    snr = 10 * np.log10(signal_power / noise_power)
    return snr

def analyze_audio(audio_path):
    y, sr = librosa.load(audio_path, sr=None)

    # Calcular a amplitude RMS
    rms = np.mean(librosa.feature.rms(y=y))

    # Calcular a frequência fundamental usando o autocorrelação
    pitches, magnitudes = librosa.core.piptrack(y=y, sr=sr)
    pitch = np.mean(pitches[pitches > 0])  # Média das frequências detectadas

    # Calcular o espectro de frequências
    spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))

    return rms, pitch, spectral_centroid



@app.route('/', methods=['GET'])
def home():
    """Rota inicial da API."""
    return jsonify({"message": "Bem-vindo à API!"})

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
    
"""Rota para listar os campos do documento"""
@app.route('/listar-campos', methods=['POST'])
@jwt_required()
@limiter.limit("10 per minute")
def listar_campos():
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo encontrado"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Nenhum arquivo selecionado"}), 400
    #filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    file.save(file_path)
    campos = listar_campos_pdf(file_path)
    os.remove(file_path)
    return jsonify(campos)

"""Rota para preencher o documento"""
@app.route('/preencher-campos', methods=['POST'])
@jwt_required()
@limiter.limit("10 per minute")
def preencher_campos():
    dados = {}
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo encontrado"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Nenhum arquivo selecionado"}), 400
    #filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    file.save(file_path)

    output_filename = f"{uuid.uuid4()}_preenchido_teste.pdf"
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
    data = request.form.to_dict()
    for c,v in data.items():
        chaves = c.split('|')
        if int(chaves[1]) == 7:
            dados[(chaves[0],int(chaves[1]))] = v
        elif int(chaves[1]) == 5:
            dados[(chaves[0],int(chaves[1]))] = int(v)
        elif int(chaves[1]) == 2:
            dados[(chaves[0],int(chaves[1]))] = bool(v)
    resultado = preencher_campos_pdf(file_path, output_path, dados)
    os.remove(file_path)
    return send_file(resultado, as_attachment=True)

"""Rota para realizar as transcrições"""
@app.route('/transcricao', methods=['POST'])
@jwt_required()
@limiter.limit("10 per minute")
def transcricao():
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo encontrado"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Nenhum arquivo selecionado"}), 400
    #filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    file.save(file_path)

    snr_value = calculate_snr_speech(file_path)
    rms, pitch, spectral_centroid = analyze_audio(file_path)
    if snr_value > 12 and pitch > 100 and rms >= 0.008:
        texto = transcricao_pdf(file_path)
    else:
        texto = {'text':'Audio de baixa qualidade,Tente novamente'}
    os.remove(file_path)
    return jsonify(texto)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

