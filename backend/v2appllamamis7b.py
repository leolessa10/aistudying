from flask import Flask, request, jsonify, send_from_directory
import subprocess
from gtts import gTTS
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips
import os
from flask_cors import CORS
import requests
import shutil
from dotenv import load_dotenv
from datetime import datetime
import re

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

app = Flask(__name__)

# Caminhos dos diretórios
BASE_DIR = os.getcwd()
VIDEO_FINAL_DIR = os.path.join(BASE_DIR, os.getenv("VIDEO_FINAL_DIR"))
TEMP_DIR = os.path.join(BASE_DIR, os.getenv("TEMP_DIR"))

# Certifique-se de que os diretórios existam
os.makedirs(VIDEO_FINAL_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

# Configuração do Flask
app.config["VIDEO_FOLDER"] = VIDEO_FINAL_DIR

# Permite requisições de Servidor na porta 3000
CORS(app, resources={r"/gerar_video": {"origins": f"http://{os.getenv('SERVER_HOST')}:3000"}})

# Caminho do modelo Mistral no llama.cpp
LLAMA_CLI_PATH = os.getenv("LLAMA_CLI_PATH")
MODEL_PATH = os.getenv("MODEL_PATH")

# Chave de API do Unsplash
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")

@app.route("/videos/<path:filename>")
def get_video(filename):
    return send_from_directory(VIDEO_FINAL_DIR, filename)

@app.route('/gerar_video', methods=['POST'])
def gerar_video():
    try:
        data = request.get_json()
        if not all(k in data for k in ['resumo', 'idade']):
            return jsonify({"error": "Os campos 'resumo' e 'idade' são obrigatórios."}), 400
        resumo = data['resumo']
        idade = data['idade']

        roteiro = gerar_roteiro(resumo, idade)
        audio_path = os.path.join(TEMP_DIR, "audio.mp3")
        gerar_audio(roteiro, audio_path)
        
        # Gera timestamp para o nome do arquivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Extrai as primeiras palavras do resumo para nomear o arquivo
        resumo_clean = re.sub(r"[^\w\s]", "", resumo)  # Remove caracteres especiais
        palavras_resumo = resumo_clean.split()[:3]  # Usa até 3 palavras do resumo
        resumo_nome = "_".join(palavras_resumo).lower()  # Junta as palavras em minúsculas

        # Define o nome do arquivo com data, hora e resumo
        video_filename = f"video_{timestamp}_{resumo_nome}.mp4"
        video_path = os.path.join(VIDEO_FINAL_DIR, video_filename)

        criar_video(audio_path, video_path, resumo)  # Adicionado o resumo como parâmetro


        # Retorna um caminho HTTP acessível
        return jsonify({"video_url": f"/videos/{video_filename}"})
    
    except Exception as e:

        print(f"Erro ao gerar vídeo: {str(e)}")  # Loga o erro no terminal
        return jsonify({"error": str(e)}), 500


def gerar_roteiro(resumo, idade):
    prompt = (
        f"Explique {resumo} de forma simples para uma pessoa  de {idade} anos e sem analogias.\n"
        f"Não repita informações já mencionadas e finalize a explicação de maneira natural, tente não cometer erros de português brasileiro.\n"
        f"Resuma em no máximo 10 frases curtas e objetivas interligando os fatos e se possível dando exemplos.\n"
        #"Tema: {resumo}\n"
        f"Resposta:"
    )
    return gerar_texto(prompt)

def limpar_resposta(resposta):
    # Remove qualquer texto após o último ponto final
    ultimo_ponto = resposta.rfind(".")
    if ultimo_ponto != -1:
        resposta = resposta[:ultimo_ponto + 1]
    return resposta

def gerar_texto(prompt):
    try:
        result = subprocess.run([LLAMA_CLI_PATH, "-m", MODEL_PATH, "-p", prompt, "--no-display-prompt", "--simple-io"],
                                capture_output=True, text=True, check=True, timeout=60)
        resposta = result.stdout.strip()

        # Remove frases indesejadas e limpa o final
        resposta = limpar_resposta(resposta)

        print(f"Resposta do modelo: {resposta}")  # Log da resposta

        if not resposta:
            raise ValueError("O modelo não retornou uma resposta válida.")
        return resposta
    except subprocess.CalledProcessError as e:
        return f"Erro ao executar o modelo: {e}"


def gerar_audio(roteiro, arquivo_saida):
    print(f"Gerando áudio em: {arquivo_saida}")  # Debug
    
    # Garantir que o diretório existe
    diretorio = os.path.dirname(arquivo_saida)
    os.makedirs(diretorio, exist_ok=True)

    # Se o arquivo já existir, removê-lo
    if os.path.exists(arquivo_saida):
        os.remove(arquivo_saida)

    # Gerar áudio
    tts = gTTS(roteiro, lang='pt-br')
    tts.save(arquivo_saida)

    # Verificar se o arquivo foi criado
    if not os.path.exists(arquivo_saida):
        raise Exception(f"Erro: {arquivo_saida} não foi criado!")


def buscar_imagens_unsplash(query, quantidade=3):
    url = f"https://api.unsplash.com/search/photos?query={query}&per_page={quantidade}"
    headers = {"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        dados = response.json()
        print(f"Dados retornados pela API: {dados}")  # Log dos dados
        
        if not dados["results"]:  # Verifica se a lista está vazia
            print("Nenhuma imagem encontrada para a busca no Unsplash.")
            return []  # Retorna lista vazia
        
        urls_imagens = [imagem["urls"]["regular"] for imagem in dados["results"]]
        return urls_imagens
    else:
        raise Exception(f"Erro ao buscar imagens: {response.status_code}")



def baixar_imagens(urls, pasta="imagens_temporarias"):
    """
    Baixa as imagens a partir de uma lista de URLs e salva em uma pasta temporária.
    Retorna uma lista com os caminhos das imagens baixadas.
    """
    if not os.path.exists(pasta):
        os.makedirs(pasta)
    
    caminhos = []
    for i, url in enumerate(urls):
        resposta = requests.get(url, stream=True)
        if resposta.status_code == 200:
            caminho = os.path.join(pasta, f"imagem{i+1}.jpg")
            with open(caminho, 'wb') as arquivo:
                resposta.raw.decode_content = True
                shutil.copyfileobj(resposta.raw, arquivo)
            caminhos.append(caminho)
        else:
            raise Exception(f"Erro ao baixar imagem: {resposta.status_code}")
    return caminhos

def criar_video(audio_path, video_path, resumo):
    """
    Cria um vídeo a partir de um áudio e imagens relacionadas ao resumo.
    As imagens são descartadas após o uso.
    """
    caminhos_imagens = []  # Inicializa a variável como uma lista vazia

    try:
        # Busca e baixa 2 imagens relacionadas ao resumo
        urls_imagens = buscar_imagens_unsplash(resumo)
        caminhos_imagens = baixar_imagens(urls_imagens, pasta=TEMP_DIR)  # Usa o diretório temporário

        # Carrega o áudio
        audio = AudioFileClip(audio_path)
        duracao_total = audio.duration
        duracao_por_imagem = duracao_total / len(caminhos_imagens)

        # Cria os clipes de vídeo a partir das imagens
        clips = [ImageClip(img).with_duration(duracao_por_imagem) for img in caminhos_imagens]
        
        # Concatena os clipes e adiciona o áudio
        video = concatenate_videoclips(clips, method="compose").with_audio(audio)
        video = video.with_duration(audio.duration)

        # Salva o vídeo final no diretório de vídeos
        video_path_final = video_path  # Usa o nome dinâmico recebido
        video.write_videofile(video_path_final, fps=24, codec='libx264', audio_codec='aac', threads=4, preset='slow')
        # fechamento explicito
        video.close()
        audio.close()

    finally:
        # Exclui as imagens temporárias após o uso
        for img in caminhos_imagens:
            if os.path.exists(img):
                os.remove(img)
        for arquivo in os.listdir(TEMP_DIR):
            caminho = os.path.join(TEMP_DIR, arquivo)
        if os.path.isfile(caminho):
            os.remove(caminho)

if __name__ == '__main__':
    app.run(
        host=os.getenv("SERVER_HOST"),  # Host do servidor
        port=5000,  # Porta fixa (ou você pode adicionar ao .env se quiser)
        debug=True
        )
