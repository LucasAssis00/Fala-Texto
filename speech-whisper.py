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
import warnings
import speech_recognition as sr
import whisper
import tempfile
import numpy as np
import os

warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

# Initialize the Whisper model
model = whisper.load_model("base")

def ouvir_microfone():
    microfone = sr.Recognizer()

    with sr.Microphone() as source:
        microfone.adjust_for_ambient_noise(source)
        print("Diga algo: ")
        audio = microfone.listen(source)

    # Save the audio data to a temporary WAV file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio_file:
        temp_audio_file.write(audio.get_wav_data())

        # Transcribe using Whisper
        print("Utilizando o Whisper:")
        result = model.transcribe(temp_audio_file.name, language='portuguese')
        transcricao = result['text'].strip()
        print("Você disse: " + transcricao)
        print("---------------------------------------")

        # Clean up the temporary file
        os.remove(temp_audio_file.name)

    return transcricao

transcricao = ''
while 'sair' not in transcricao.lower():
    transcricao = ouvir_microfone()
