'''
import speech_recognition as sr
import os
import subprocess


def ouvir_microfone():
    microfone = sr.Recognizer()

    with sr.Microphone() as source:
        microfone.adjust_for_ambient_noise(source)

        print("Diga algo: ")

        audio = microfone.listen(source)

    try:
        print("Utilizando o SR:")
        frase = microfone.recognize_google(audio,language='pt-BR')
        #frase = microfone.recognize_whisper(audio,language='portuguese')
        #frase = microfone.recognize_whisper(audio)
        print("Você disse: " + frase)
        print("---------------------------------------")

        return frase

    except sr.UnknownValueError:
        print("Não entendi")
        print("---------------------------------------")

        return ""


transcricao = ''
while 'sair' not in transcricao:
    transcricao = ouvir_microfone()
'''
import speech_recognition as sr

import whisper

import warnings
warnings.filterwarnings("ignore")

def transcricao(arquivo):
	result = model.transcribe(arquivo, language = 'Portuguese')
	return result['text']

# Inicializando o reconhecedor de áudio
recognizer = sr.Recognizer()

# Capturando áudio do microfone
with sr.Microphone() as source:
    print("Fale algo:")
    audio = recognizer.listen(source, timeout=4, phrase_time_limit=8)  # Adiciona timeout e tempo limite

    # Salvando o áudio em um arquivo temporário
    with open("audio.wav", "wb") as f:
        f.write(audio.get_wav_data())



# Carregando o modelo Whisper
model = whisper.load_model("base")

'''
# Transcrevendo o arquivo de áudio
result = model.transcribe("audio.wav", language = 'Portuguese')
'''

# Exibindo o resultado
#print("Transcrição:", result['text'])
print("Transcrição:", transcricao("audio.wav"))