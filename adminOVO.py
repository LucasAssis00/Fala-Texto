import tkinter as tk
import speech_recognition as sr
import threading
import pyttsx3
import subprocess
from PIL import Image, ImageTk

import os
'''
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
'''
import time

import csv

import platform
from gtts import gTTS


keywords = ["Nome do paciente", "Data", "Horário", "Concentração", "Dose oferecida", 
            "FC", "Saturação de Oxigênio", "PA", "PF", "Reações", "Comentários"]


# Inicializa o reconhecedor de voz e o sintetizador de voz
#recognizer = sr.Recognizer()
engine = pyttsx3.init()


def speak(text):
    engine.say(text)
    engine.runAndWait()
'''
def speak(text):
    if platform.system() == "Linux":
        tss = gTTS(text,lang="pt")
        tss.save(f"teste.mp3")
        os.system(f"mpg321 teste.mp3")
    else:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
'''

# Função para reconhecimento de voz
def reconhecer_comando():
    recognizer = sr.Recognizer()
    """O parâmetro pause_threshold define a quantidade de silêncio que o algoritmo de reconhecimento de fala
    deve considerar antes de parar de escutar. Reduzir esse valor pode acelerar a detecção de fim de fala."""
    recognizer.pause_threshold = 0.8  # O valor padrão é 0.8, reduza para um valor menor
    """non_speaking_duration: Define a duração do silêncio necessário antes de começar a escutar.
    Diminuir esse valor pode iniciar a captação mais rapidamente."""
    recognizer.non_speaking_duration = 0.5  # O valor padrão é 0.5

    with sr.Microphone() as source:
        stringEntrada = ""
        #while stringEntrada.upper() != "SAIR":
        while True:
            if(stringEntrada.upper() == "SAIR"):
                #sys.exit()
                root.destroy()
                #break
            print("Aguardando comando...")
            """                                         phrase_time_limit: Limita o tempo máximo que a biblioteca irá ouvir,
                                                        o que pode forçar o reconhecimento a acontecer mais rápido."""
            audio = recognizer.listen(source, timeout=4, phrase_time_limit=8)  # Adiciona timeout e tempo limite
            try:
                stringEntrada = recognizer.recognize_google(audio, language='pt-BR')
                stringEntrada = stringEntrada.upper()
                print(f"Você disse: {stringEntrada}")

                for chave in associacoes:
                    if stringEntrada.startswith(chave.upper()):
                        separado = stringEntrada.split(chave.upper())[1]
                        if(isinstance(associacoes.get(chave), str)):
                            associacoes[chave] = separado
                            #print("|U.u")
                            #print(associacoes[chave])
                        else:
                            for naonulo in range(len(associacoes[chave])):
                                if associacoes[chave][naonulo] == " ":
                                    associacoes[chave][naonulo] = separado
                                    break
                print(associacoes["Nome do paciente"])
                print(associacoes["Data"])
                print(associacoes["Horário"])
                print(associacoes["Concentração"])
                print(associacoes["Dose oferecida"])
                print(associacoes["FC"])
                print(associacoes["Saturação de Oxigênio"])
                print(associacoes["PA"])
                print(associacoes["PF"])
                print(associacoes["Reações"])
                print(associacoes["Comentários"])
                print()
                print()
                '''
                if stringEntrada.lower() == "abrir janela 1":
                    abrir_janela1()
                elif stringEntrada.lower() == "abrir janela 2":
                    abrir_janela2()
                elif(stringEntrada.upper() == "SAIR"):
                    pass#gambiarra monstra (funciona)
                else:
                    print("Comando não reconhecido.")
                '''
            except sr.UnknownValueError:
                print("Não entendi o comando.")
            except sr.RequestError:
                print("Erro ao se comunicar com o serviço de reconhecimento de voz.")

"""def listen():
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)  # Ajusta para o ruído ambiente
        print("Diga algo...")
        #audio = recognizer.listen(source, timeout=3, phrase_time_limit=6)  # Limita o tempo de escuta
        audio = recognizer.listen(source, phrase_time_limit=6)
        try:
            command = recognizer.recognize_google(audio, language='pt-BR')
            print(f"Você disse: {command}")
            return command
        except sr.UnknownValueError:
            print("Não entendi o que você disse.")
            return ""
        except sr.RequestError:
            print("Erro ao se comunicar com o serviço de reconhecimento de voz.")
            return """""

def iniciar_reconhecimento():
    thread = threading.Thread(target=reconhecer_comando)
    thread.daemon = True
    thread.start()

varNome = ""
#varData = ["","",""]#vai dar merda isso aqui
varData = ""
listaHorarios = [" "] * 10
listaConcentracoes = [" "] * 10
listaDoses = [" "] * 10
listaFCs = [" "] * 10
listaSats = [" "] * 10
listaPAs = [" "] * 10
listaPFs = [" "] * 10
listaReacoes = [" "] * 10
varComentarios = ""

# Criando o dicionário que associa cada palavra-chave à variável correspondente
associacoes = {
    "Nome do paciente": varNome,
    "Data": varData,
    "Horário": listaHorarios,
    "Concentração": listaConcentracoes,
    "Dose oferecida": listaDoses,
    "FC": listaFCs,
    "Saturação de Oxigênio": listaSats,
    "PA": listaPAs,
    "PF": listaPFs,
    "Reações": listaReacoes,
    "Comentários": varComentarios,
}


stringEntrada = ""
indice=1
while os.path.exists(f'registroOVO{indice}.csv'):
    indice+=1



# Criar a janela principal
root = tk.Tk()
root.title("Aplicação com Comandos de Voz")
root.configure(bg="#083f76")
label = tk.Label(root, text="Aplicações do Fala-Texto", font=("Arial", 14),bg="#083f76",fg="white")
label.pack()
message = tk.Message(root, text="* Preenchimento online\n\n* Faturamento\n\n* Preenchimento PDF's",bg="#083f76",fg="white")
message.pack(padx=20, pady=20)
message2 = tk.Label(root, text="Instrução: Fale a aplicação que você deseja trabalhar \n",bg="#083f76",fg="white")
message2.pack(padx=50, pady=80)
root.geometry("700x400+100+100")



# Carregar a imagem usando PIL
imagem = Image.open("Projeto (4).png")
imagem_tk = ImageTk.PhotoImage(imagem)


# Criar um widget Label para exibir a imagem
label_imagem = tk.Label(root, image=imagem_tk,borderwidth=0, highlightthickness=0)
label_imagem.place(x=0, y=0)

# Iniciar o reconhecimento de voz automaticamente
iniciar_reconhecimento()

root.mainloop()


"""
#####################################################################################################################
while stringEntrada != "SAIR":
    stringEntrada = listen().upper()
    print(stringEntrada)

    for chave in associacoes:
        if stringEntrada.startswith(chave.upper()):
            separado = stringEntrada.split(chave.upper())[1]
            if(isinstance(associacoes.get(chave), str)):
                associacoes[chave] = separado
                #print("|U.u")
                #print(associacoes[chave])
            else:
                for naonulo in range(len(associacoes[chave])):
                    if associacoes[chave][naonulo] == " ":
                        associacoes[chave][naonulo] = separado
                        break
    '''
    for chave, valor in associacoes.items:
        if stringEntrada.startswith(chave.upper()):
            separado = stringEntrada.split(chave.upper())[1]
            if(isinstance(valor, str)):
                valor = separado
            else:
                for naonulo in range(len(valor)):
                    if valor[naonulo] == " ":
                        valor[naonulo] == separado
                        break
    '''
    
    print(associacoes["Nome do paciente"])
    print(associacoes["Data"])
    print(associacoes["Horário"])
    print(associacoes["Concentração"])
    print(associacoes["Dose oferecida"])
    print(associacoes["FC"])
    print(associacoes["Saturação de Oxigênio"])
    print(associacoes["PA"])
    print(associacoes["PF"])
    print(associacoes["Reações"])
    print(associacoes["Comentários"])
    print()
    print()
"""