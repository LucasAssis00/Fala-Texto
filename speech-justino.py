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
        audio = recognizer.listen(source, phrase_time_limit=5)
        try:
            command = recognizer.recognize_google(audio, language='pt-BR')
            if interrupcao == False:
                print(f"Você disse: {command}")
            return command
        except sr.UnknownValueError:
            if interrupcao == False:
                print("Não entendi o que você disse.")
            return ""
        except sr.RequestError:
            print("Erro ao se comunicar com o serviço de reconhecimento de voz.")
            return ""

interrupcao = False

start_time = time.time()
speak("Olá. Eu sou o assistente de voz. ")
'''
speak("""Olá. Eu sou o assistente de voz. Fale o termo navegador para abrí-lo, 
      preencher formulario para carregar a página web do formulário, 
      cite o nome do campo antes de pronunciar a informação
       ou depois da palavra  limpar para apagar algo já preenchido""")
'''
while True:
    command = listen().upper()  # string
    if "INTERROMPER GRAVAÇÃO" in command:
        if interrupcao == False:
            speak("Sistema em modo de espera")
        interrupcao = True
    elif "INICIAR GRAVAÇÃO" in command or "CONTINUAR GRAVAÇÃO" in command:
        if interrupcao == True:
            speak("Sistema identificando fala")
        interrupcao = False

    if interrupcao == False:
        match command:
            case cmd if "NAVEGADOR" in cmd:
                print(cmd)
                #speak("Abrindo o navegador")
                driver = webdriver.Edge()
            case cmd if "NOVA ABA" in cmd:
                #speak("nova aba")
                driver.switch_to.new_window('tab')
                janelas_ativas = driver.window_handles
            case cmd if "MUDAR ABA" in cmd:
                #speak("mudando de aba")
                #driver.find_element(By.TAG_NAME, "body").send_keys(Keys.CONTROL + Keys.TAB)
                #driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.TAB)
                janela_atual = driver.current_window_handle
                indice_atual = janelas_ativas.index(janela_atual)
                driver.switch_to.window(janelas_ativas[indice_atual - 1])
            case cmd if "NOVA JANELA" in cmd:
                #speak("nova janela")
                driver.switch_to.new_window('window')
                janelas_ativas = driver.window_handles
            case cmd if "GOOGLE" in cmd:
                speak("google")
                driver.get("http://www.google.com")
                janelas_ativas = driver.window_handles
            case cmd if "FORMULÁRIO TESTE" in cmd:
                speak("abrindo practice-automation")
                driver.get("https://practice-automation.com/form-fields/")
                janelas_ativas = driver.window_handles
            case cmd if "NOME" in cmd:
                search_box = driver.find_element("xpath", '/html/body/div[1]/div[2]/div/div/main/div/article/div/form/label[1]/input')
                if "LIMPAR" in command:
                    search_box.clear()
                else:
                    nome_user = (command.split("NOME", 1)[1]).strip()                
                    search_box.send_keys(nome_user)
            case cmd if "SENHA" in cmd:
                search_box = driver.find_element("xpath", '/html/body/div[1]/div[2]/div/div/main/div/article/div/form/label[2]/input')
                if "LIMPAR" in command:
                    search_box.clear()
                else:
                    senha_user = (command.split("SENHA", 1)[1]).strip()
                    search_box.send_keys(senha_user)
            case cmd if "BEBIDA FAVORITA" in cmd:
                if "LIMPAR" in command:
                    for i in range(1,6):
                        botao_bebida = driver.find_element("xpath", f"/html/body/div[1]/div[2]/div/div/main/div/article/div/form/input[{i}]")
                        print(botao_bebida.get_attribute('value'))
                        if botao_bebida.is_selected():
                            botao_bebida.click()
                else:
                    if 'ÁGUA' in cmd:
                        botao_bebida = driver.find_element("xpath", "/html/body/div[1]/div[2]/div/div/main/div/article/div/form/label[4]")
                        botao_bebida.click()
                    if 'LEITE' in cmd:
                        botao_bebida = driver.find_element("xpath", "/html/body/div[1]/div[2]/div/div/main/div/article/div/form/label[5]")
                        botao_bebida.click()
                    if 'CAFÉ' in cmd:
                        botao_bebida = driver.find_element("xpath", "/html/body/div[1]/div[2]/div/div/main/div/article/div/form/label[6]")
                        botao_bebida.click()
                    if 'VINHO' in cmd:
                        botao_bebida = driver.find_element("xpath", "/html/body/div[1]/div[2]/div/div/main/div/article/div/form/label[7]")
                        botao_bebida.click()
                    if 'CHÁ' in cmd:
                        botao_bebida = driver.find_element("xpath", "/html/body/div[1]/div[2]/div/div/main/div/article/div/form/label[8]")
                        botao_bebida.click()
            case cmd if "COR FAVORITA" in cmd:
                #pelo menos por hora não sei como/ tá dando pra limpar esse campo. Depois que seleciona um aí fudeu
                if 'VERMELHO' in cmd:
                    botao_cor = driver.find_element("xpath", "/html/body/div[1]/div[2]/div/div/main/div/article/div/form/input[6]")
                    #botao_cor = driver.find_element("xpath", "/html/body/div[1]/div[2]/div/div/main/div/article/div/form/label[10]")
                    botao_cor.click()
                if 'AZUL' in cmd:
                    botao_cor = driver.find_element("xpath", "/html/body/div[1]/div[2]/div/div/main/div/article/div/form/input[7]")
                    #botao_cor = driver.find_element("xpath", "/html/body/div[1]/div[2]/div/div/main/div/article/div/form/label[11]")
                    botao_cor.click()
                if 'AMARELO' in cmd:
                    botao_cor = driver.find_element("xpath", "/html/body/div[1]/div[2]/div/div/main/div/article/div/form/input[8]")
                    #botao_cor = driver.find_element("xpath", "/html/body/div[1]/div[2]/div/div/main/div/article/div/form/label[12]")
                    botao_cor.click()
                if 'VERDE' in cmd:
                    botao_cor = driver.find_element("xpath", "/html/body/div[1]/div[2]/div/div/main/div/article/div/form/input[9]")
                    #botao_cor = driver.find_element("xpath", "/html/body/div[1]/div[2]/div/div/main/div/article/div/form/label[13]")
                    botao_cor.click()
                if 'ROSA' in cmd:
                    botao_cor = driver.find_element("xpath", "/html/body/div[1]/div[2]/div/div/main/div/article/div/form/input[10]")
                    #botao_cor = driver.find_element("xpath", "/html/body/div[1]/div[2]/div/div/main/div/article/div/form/label[14]")
                    botao_cor.click()
            case cmd if "GOSTO" in cmd:
                botao_caixa = driver.find_element("xpath", '/html/body/div[1]/div[2]/div/div/main/div/article/div/form/select')
                botao_caixa.click()
                if "NÃO SEI" in cmd:
                    botao_caixa = driver.find_element("xpath", '/html/body/div[1]/div[2]/div/div/main/div/article/div/form/select/option[4]')
                elif "NÃO GOSTO" in cmd:
                    botao_caixa = driver.find_element("xpath", '/html/body/div[1]/div[2]/div/div/main/div/article/div/form/select/option[3]')
                else:
                    botao_caixa = driver.find_element("xpath", '/html/body/div[1]/div[2]/div/div/main/div/article/div/form/select/option[2]')
                botao_caixa.click()
            case cmd if "E-MAIL" in cmd:
                email_box = driver.find_element("xpath", '/html/body/div[1]/div[2]/div/div/main/div/article/div/form/input[11]')
                if "LIMPAR" in command:
                    search_box.clear()
                else:
                    email_user = (command.split("E-MAIL", 1)[1]).strip()
                    email_user = email_user.replace("ARROBA", "@")
                    email_box.send_keys(email_user)
                #email_box.send_keys(Keys.RETURN)
            case cmd if "MENSAGEM" in cmd:
                message_box = driver.find_element("xpath", '/html/body/div[1]/div[2]/div/div/main/div/article/div/form/textarea')
                if "LIMPAR" in command:
                    search_box.clear()
                else:
                    input_message = (command.split("MENSAGEM", 1)[1]).strip()
                    message_box.send_keys(input_message)
            case cmd if "ENVIAR" in cmd:
                botao_avanca = driver.find_element("xpath", '/html/body/div[1]/div[2]/div/div/main/div/article/div/form/button')
                botao_avanca.click()
            

            case cmd if "SAIR" in cmd:
                print(janelas_ativas)
                driver.quit()
                #speak("Fechando o navegador")
            case cmd if "PESQUISAR" in cmd:
                texto_pesquisa = (command.split("PESQUISAR", 1)[1])
                #speak("Pesquisando" + texto_pesquisa)
                if 'youtube' in driver.current_url:
                    search_box = driver.find_element("xpath", '/html/body/ytd-app/div[1]/div/ytd-masthead/div[4]/div[2]/ytd-searchbox/form/div[1]/div[1]/input')
                if 'google' in driver.current_url:
                    search_box = driver.find_element("xpath", '/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[2]/textarea')
                time.sleep(1)
                search_box.send_keys(texto_pesquisa)
                search_box.send_keys(Keys.RETURN)
            case cmd if "ENCERRAR" in cmd:
                try:
                    driver.quit()
                except:
                    pass
                speak("Até a próxima.")
                break
                '''
            case cmd if "EXCEL" in cmd:
                speak("Abrindo o Excel")
                '''
    else:
        pass


print("--- %s seconds ---" % (time.time() - start_time))
