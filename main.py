import os
import subprocess
import argparse
from pytubefix import YouTube
import openai

openai.api_key = os.getenv('OPENAI_API_KEY')


# Configure sua chave de API da OpenAI
#openai.api_key = 'SUA_CHAVE_DE_API_AQUI'

def baixar_video(url, caminho_saida):
    yt = YouTube(url)
    video = yt.streams.filter(only_audio=True).first()
    caminho_video = video.download(output_path=caminho_saida)
    return caminho_video

def extrair_audio(caminho_video, caminho_audio):
    comando = [
        'ffmpeg',
        '-i', caminho_video,
        '-vn',
        '-acodec', 'pcm_s16le',
        '-ar', '44100',
        '-ac', '2',
        caminho_audio
    ]
    subprocess.run(comando, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def transcrever_audio(caminho_audio):
    with open(caminho_audio, 'rb') as arquivo_audio:
        transcricao = openai.Audio.transcribe("whisper-1", arquivo_audio)
    return transcricao['text']

def resumir_texto(texto):
    resposta = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Resuma o seguinte texto:\n\n{texto}",
        temperature=0.7,
        max_tokens=150,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return resposta['choices'][0]['text'].strip()

def main():
    parser = argparse.ArgumentParser(description='Analisador de vídeo do YouTube que gera um resumo.')
    parser.add_argument('url', help='URL do vídeo do YouTube')
    args = parser.parse_args()

    url = args.url
    caminho_saida = "."

    # Passo 1: Baixar o vídeo
    print("Baixando o vídeo...")
    caminho_video = baixar_video(url, caminho_saida)

    # Passo 2: Extrair o áudio
    print("Extraindo o áudio...")
    caminho_audio = os.path.splitext(caminho_video)[0] + '.wav'
    extrair_audio(caminho_video, caminho_audio)

    # Passo 3: Transcrever o áudio
    print("Transcrevendo o áudio...")
    transcricao = transcrever_audio(caminho_audio)

    # Passo 4: Resumir o texto
    print("Resumindo o texto...")
    resumo = resumir_texto(transcricao)

    print("\nResumo do vídeo:")
    print(resumo)

    # Limpar arquivos temporários
    os.remove(caminho_video)
    os.remove(caminho_audio)

if __name__ == "__main__":
    main()
