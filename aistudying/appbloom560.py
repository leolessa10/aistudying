from flask import Flask, request, jsonify
#import requests
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from gtts import gTTS
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips
import os
from flask import Flask
from flask_cors import CORS
from flask import Flask, send_from_directory
import os

app = Flask(__name__)

# Caminho onde o vídeo está salvo
VIDEO_FOLDER = os.getcwd()
app.config["VIDEO_FOLDER"] = VIDEO_FOLDER

@app.route("/video_final.mp4")
def get_video():
    return send_from_directory(app.config["VIDEO_FOLDER"], "video_final.mp4")

# Permite requisições de 'http://aistudying.leo.com:3000'
CORS(app, resources={r"/gerar_video": {"origins": "http://aistudying.leo.com:3000"}})

# Carrega o modelo BLOOM
model_name = "bigscience/bloom-560m"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

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
        roteiro_limpo = limpar_roteiro(roteiro)
        gerar_audio(roteiro, audio_path)

        video_path = "video_final.mp4"
        criar_video(audio_path, video_path)

        return jsonify({"video_url": video_path})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def gerar_roteiro(resumo, idade):
    #prompt = f"Explique para uma criança de {idade} anos: {resumo}"
    #prompt = (
    #    f"Explique o seguinte tema de forma simples para uma criança de {idade} anos. "
    #    f"Seja breve e não repita frases desnecessariamente. "
    #    f"Use frases curtas e objetivas:\n{resumo}"
    prompt = (
        f"Explique o seguinte tema de forma simples para uma criança de {idade} anos.\n\n"
        f"Não repita informações já mencionadas e finalize a explicação de maneira natural. "
        f"Resuma em no máximo 3 frases curtas e objetivas.\n"
        f"Tema: {resumo}\n\n"
        f"Explicação:"
    )
    return gerar_texto(prompt)

#def gerar_texto(prompt):
#    inputs = tokenizer(prompt, return_tensors="pt")
#    outputs = model.generate(**inputs, max_length=150)
#    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
#    return generated_text

def gerar_texto(prompt):
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(**inputs, max_length=150)
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Remove qualquer parte do prompt que possa ter sido repetida no início
    if "Explicação:" in generated_text:
        generated_text = generated_text.split("Explicação:")[-1].strip()

    return generated_text


def limpar_roteiro(roteiro):
    frases = roteiro.split(". ")
    frases_unicas = []
    for frase in frases:
        if frase not in frases_unicas:
            frases_unicas.append(frase)
    return ". ".join(frases_unicas)


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
    #clips = [ImageClip(img).set_duration(duracao_por_imagem) for img in imagens]
    clips = [ImageClip(img).with_duration(duracao_por_imagem) for img in imagens]


    #video = concatenate_videoclips(clips).with_audio(audio)
    video = concatenate_videoclips(clips, method="compose").with_audio(audio)
    video = video.with_duration(audio.duration)  # Garante que o vídeo tenha o mesmo tempo do áudio
    if video.duration < audio.duration:
        video = video.set_duration(audio.duration)  # Força o vídeo a durar o mesmo tempo do áudio
    #video.write_videofile(video_path, fps=24, codec='libx264', audio_codec='aac')
    video.write_videofile(video_path, fps=24, codec='libx264', audio_codec='aac', threads=4, preset='slow')

if __name__ == '__main__':
    app.run(host="aistudying.leo.com", port=5000, debug=True)

