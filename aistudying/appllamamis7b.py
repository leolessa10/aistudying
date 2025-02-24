from flask import Flask, request, jsonify, send_from_directory
import subprocess
from gtts import gTTS
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips
import os
from flask_cors import CORS
import subprocess

app = Flask(__name__)

# Caminho onde o vídeo será salvo
VIDEO_FOLDER = os.getcwd()
app.config["VIDEO_FOLDER"] = VIDEO_FOLDER

@app.route("/video_final.mp4")
def get_video():
    return send_from_directory(app.config["VIDEO_FOLDER"], "video_final.mp4")

# Permite requisições de 'http://aistudying.leo.com:3000'
CORS(app, resources={r"/gerar_video": {"origins": "http://aistudying.leo.com:3000"}})

# Caminho do modelo Mistral no llama.cpp
LLAMA_CLI_PATH = "/app/modelos/llama.cpp/build/bin/llama-cli"
MODEL_PATH = "/app/modelos/llama.cpp/mistral-7b-instruct-v0.1.Q4_K_M.gguf"

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
        criar_video(audio_path, video_path)
        
        return jsonify({"video_url": video_path})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def gerar_roteiro(resumo, idade):
    prompt = (
        f"Explique o seguinte tema de forma simples para uma criança de {idade} anos e sem analogias.\n"
        f"Não repita informações já mencionadas e finalize a explicação de maneira natural, tente não cometer erros de português brasileiro.\n"
        f"Resuma em no máximo 3 frases curtas e objetivas.\n"
        f"Tema: {resumo}\n"
        #f"Explicação:"
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

        if not resposta:
            raise ValueError("O modelo não retornou uma resposta válida.")
        return resposta
    except subprocess.CalledProcessError as e:
        return f"Erro ao executar o modelo: {e}"


#def gerar_texto(prompt):
#    try:
#        result = subprocess.run([LLAMA_CLI_PATH, "-m", MODEL_PATH, "-p", prompt, "--no-display-prompt", "--simple-io"],
#                                capture_output=True, text=True, check=True)
#        return result.stdout.strip()
#
        # Remover o prompt da resposta
#        resposta_limpa = resposta.split("\n")[-1].strip()  # Pega apenas a última linha gerada

#        return resposta_limpa

#    except subprocess.CalledProcessError as e:
#        return f"Erro ao executar o modelo: {e}"

def gerar_audio(roteiro, arquivo_saida):
    if os.path.exists(arquivo_saida):
        os.remove(arquivo_saida)  # Remove qualquer áudio antigo antes de gerar um novo
    tts = gTTS(roteiro, lang='pt-br')
    tts.save(arquivo_saida)

def criar_video(audio_path, video_path):
    audio = AudioFileClip(audio_path)
    imagens = ["imagem1.png", "imagem2.png"]

    if not all(os.path.exists(img) for img in imagens):
        raise Exception("Arquivos de imagem não encontrados.")
    
    duracao_total = audio.duration
    duracao_por_imagem = duracao_total / len(imagens)
    clips = [ImageClip(img).with_duration(duracao_por_imagem) for img in imagens]
    
    video = concatenate_videoclips(clips, method="compose").with_audio(audio)
    video = video.with_duration(audio.duration)
    video.write_videofile(video_path, fps=24, codec='libx264', audio_codec='aac', threads=4, preset='slow')

if __name__ == '__main__':
    app.run(host="aistudying.leo.com", port=5000, debug=True)

