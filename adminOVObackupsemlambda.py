import speech_recognition as sr
import pyttsx3
import subprocess

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
recognizer = sr.Recognizer()
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
def listen():
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
            return ""

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
    
    print("Nome do paciente\t", associacoes["Nome do paciente"])
    print("Data\t\t\t", associacoes["Data"])
    print("Horário\t\t\t", associacoes["Horário"])
    print("Concentração\t\t", associacoes["Concentração"])
    print("Dose oferecida\t\t", associacoes["Dose oferecida"])
    print("FC\t\t\t", associacoes["FC"])
    print("Saturação de Oxigênio\t", associacoes["Saturação de Oxigênio"])
    print("PA\t\t\t", associacoes["PA"])
    print("PF\t\t\t", associacoes["PF"])
    print("Reações\t\t\t", associacoes["Reações"])
    print("Comentários", associacoes["Comentários"])
    print()
    print()




indice=1
while os.path.exists(f'registroOVO{indice}.csv'):
    indice+=1



with open(f'registroOVO{indice}.csv', mode='w', newline='') as arquivo_csv:
    #print("oi")
    escritor_csv = csv.writer(arquivo_csv)

    for campo in keywords:
        valor = associacoes.get(campo) #busca o valor no dicionario

        if valor is not None:
            '''
            #se for uma lista, converte em string
            if isinstance(valor, list):
                valor = ', '.join(map(str, valor))
            '''
            if isinstance(valor, list):
                escritor_csv.writerow([campo] + valor)
            elif isinstance(valor, str):
                escritor_csv.writerow([campo, valor])
        else:
            #valor = "N/A" #caso o valor não seja encontrado, pode inserir um valor padrão
            escritor_csv.writerow([campo, 'N/A'])

        #escritor_csv.writerow([campo, valor])