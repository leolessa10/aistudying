from flask import Flask, request, jsonify, send_from_directory
from gtts import gTTS
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips
import os
from flask_cors import CORS
import requests
import shutil
from transformers import AutoTokenizer, AutoModelForCausalLM  # Novas importações

app = Flask(__name__)

# Caminho onde o vídeo será salvo
VIDEO_FOLDER = os.getcwd()
app.config["VIDEO_FOLDER"] = VIDEO_FOLDER

# Permite requisições de 'http://aistudying.leo.com:3000'
CORS(app, resources={r"/gerar_video": {"origins": "http://aistudying.leo.com:3000"}})

# Defina o modelo que você quer usar
MODEL_NAME = "mistralai/Mistral-7B-v0.1"  # Substitua pelo modelo desejado

# Carregue o tokenizer e o modelo
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)

# Chave da API Unsplash (substitua pela sua chave)
UNSPLASH_ACCESS_KEY = "yBnAwMiI_VSPVqP82RyOQ4EbqHj6fWQazMtdhs8k_XE"

@app.route("/video_final.mp4")
def get_video():
    return send_from_directory(app.config["VIDEO_FOLDER"], "video_final.mp4")

@app.route('/gerar_video', methods=['POST'])
def gerar_video():
    try:
        data = request.json
        if not data or 'resumo' not in data or 'idade' not in data:
            return jsonify({"error": "Os campos 'resumo' e 'idade' são obrigatórios."}), 400
        
        resumo = data['resumo']
        idade = data['idade']

        roteiro = gerar_roteiro(resumo, idade)
        audio_path = "audio.mp3"
        gerar_audio(roteiro, audio_path)
        
        video_path = "video_final.mp4"
        criar_video(audio_path, video_path, resumo)  # Adicionado o resumo como parâmetro
        
        return jsonify({"video_url": video_path})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def gerar_roteiro(resumo, idade):
    prompt = (
        f"Explique o seguinte tema de forma simples para uma criança de {idade} anos e sem analogias.\n"
        f"Não repita informações já mencionadas e finalize a explicação de maneira natural, tente não cometer erros de português brasileiro.\n"
        f"Resuma em no máximo 3 frases curtas e objetivas.\n"
        f"Tema: {resumo}\n"
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
        # Tokenize o prompt
        inputs = tokenizer(prompt, return_tensors="pt")

        # Gere a resposta com parâmetros ajustados
        outputs = model.generate(
            inputs.input_ids,
            max_length=200,  # Tamanho máximo da resposta
            temperature=0.7,  # Controla a criatividade
            top_p=0.9,        # Controla a diversidade
            do_sample=True,   # Ativa a amostragem
            repetition_penalty=1.2,  # Evita repetições
        )

        # Decodifique a resposta
        resposta = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Remove frases indesejadas e limpa o final
        resposta = limpar_resposta(resposta)

        if not resposta:
            raise ValueError("O modelo não retornou uma resposta válida.")
        return resposta
    except Exception as e:
        return f"Erro ao gerar texto: {e}"

def gerar_audio(roteiro, arquivo_saida):
    if os.path.exists(arquivo_saida):
        os.remove(arquivo_saida)  # Remove qualquer áudio antigo antes de gerar um novo
    tts = gTTS(roteiro, lang='pt-br')
    tts.save(arquivo_saida)

def buscar_imagens_unsplash(query, quantidade=3):
    """
    Busca imagens no Unsplash com base em uma consulta (query).
    Retorna uma lista de URLs das imagens.
    """
    url = f"https://api.unsplash.com/search/photos?query={query}&per_page={quantidade}"
    headers = {"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        dados = response.json()
        print(f"Dados retornados pela API: {dados}")  # Log dos dados
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
        caminhos_imagens = baixar_imagens(urls_imagens)

        # Carrega o áudio
        audio = AudioFileClip(audio_path)
        duracao_total = audio.duration
        duracao_por_imagem = duracao_total / len(caminhos_imagens)

        # Cria os clipes de vídeo a partir das imagens
        clips = [ImageClip(img).with_duration(duracao_por_imagem) for img in caminhos_imagens]
        
        # Concatena os clipes e adiciona o áudio
        video = concatenate_videoclips(clips, method="compose").with_audio(audio)
        video = video.with_duration(audio.duration)

        # Salva o vídeo final
        video.write_videofile(video_path, fps=24, codec='libx264', audio_codec='aac', threads=4, preset='slow')
    finally:
        # Exclui as imagens temporárias após o uso
        for img in caminhos_imagens:
            os.remove(img)
        if os.path.exists("imagens_temporarias"):
            os.rmdir("imagens_temporarias")

if __name__ == '__main__':
    app.run(host="aistudying.leo.com", port=5000, debug=True)
