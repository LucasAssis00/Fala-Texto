import speech_recognition as sr
import pyttsx3
import subprocess

import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time

import platform
from gtts import gTTS


# Inicializa o reconhecedor de voz e o sintetizador de voz
recognizer = sr.Recognizer()
engine = pyttsx3.init()

'''
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

while True:
    command = listen().upper()
    print(command)
    if "NAVEGADOR" in command:
        speak("Abrindo o navegador")
        #subprocess.run(["start","chromium"], shell=True)
        driver = webdriver.Edge()
        #subprocess.run(["chromium"], shell=True)
    elif "NOVA ABA" in command:
        speak("nova aba")
        driver.switch_to.new_window('tab')
    elif "NOVA JANELA" in command:
        speak("nova janela")
        driver.switch_to.new_window('window')
        #driver.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 't')
    elif "YOUTUBE" in command:
        speak("youtube")
        driver.get("http://www.youtube.com")
        #driver.find_element_by_tag_name('body').send_keys('youtube.com')
        #driver.find_element_by_tag_name('body').send_keys(Keys.ENTER)
    elif "INSTAGRAM" in command:
        speak("abrindo insta")
        driver.get("https://www.instagram.com/")
        #driver.find_element_by_tag_name('body').send_keys('instagram.com')
        #driver.find_element_by_tag_name('body').send_keys(Keys.ENTER)
    elif "SAIR" in command:
        driver.quit()
        speak("Fechando o navegador")
        #break
    elif "ENCERRAR" in command:
        driver.quit()
        speak("Encerrando o assistente")
        break
    elif "PESQUISAR" in command:
        texto_pesquisa = (command.split("PESQUISAR",1)[1])
        speak("Pesquisando" + texto_pesquisa)
        #search_box = driver.find_element("xpath", '//*[@id="search"]')
        search_box = driver.find_element("xpath", '/html/body/ytd-app/div[1]/div/ytd-masthead/div[4]/div[2]/ytd-searchbox/form/div[1]/div[1]/input')
        time.sleep(1)
        #search_box.send_keys(texto_pesquisa + Keys.RETURN)
        search_box.send_keys(texto_pesquisa)
        search_box.send_keys(Keys.RETURN)

    elif 'EXCEL' in command:
        speak("Abrindo o Excel")
        #subprocess.run(["start", "Excel"], shell=True)
        #subprocess.run(["Excel"], shell=True)

