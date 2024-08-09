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


br_number_system = {
    'zero': 0,
    'um': 1,
    'uma': 1,
    'dois': 2,
    'duas': 2,
    'tres': 3,
    'quatro': 4,
    'cinco': 5,
    'seis': 6,
    'sete': 7,
    'oito': 8,
    'nove': 9,
    'dez': 10,
    'onze': 11,
    'doze': 12,
    'treze': 13,
    'catorze': 14,
    'quinze': 15,
    'dezesseis': 16,
    'dezessete': 17,
    'dezoito': 18,
    'dezenove': 19,
    'vinte': 20,
    'trinta': 30,
    'quarenta': 40,
    'cinquenta': 50,
    'sessenta': 60,
    'setenta': 70,
    'oitenta': 80,
    'noventa': 90,
    'cem': 100,
    'cento': 100,
    #'mil': 1000,
    #'milhão': 1000000,
    #'bilhão': 1000000000,
    #'ponto': '.'

}

def number_formation(number_words):
    numbers = []
    for number_word in number_words:
        numbers.append(br_number_system[number_word])
#    if len(numbers) == 4:
#        return (numbers[0] * numbers[1]) + numbers[2] + numbers[3]
    if len(numbers) == 3:
        return numbers[0] + numbers[1] + numbers[2]
    elif len(numbers) == 2:
        return numbers[0] + numbers[1]
    else:
        return numbers[0]


def word_to_num(number_sentence):
    if type(number_sentence) is not str:
        raise ValueError("Type of input is not string! Please enter a valid number word (eg. \'two million twenty three thousand and forty nine\')")

    number_sentence = number_sentence.replace('-', ' ')
    number_sentence = number_sentence.lower()  # converting input to lowercase

    if(number_sentence.isdigit()):  # return the number if user enters a number string
        return int(number_sentence)

    split_words = number_sentence.strip().split()  # strip extra spaces and split sentence into words

    clean_numbers = []
    clean_decimal_numbers = []

    # removing and, & etc.
    for word in split_words:
        if word in br_number_system:
            clean_numbers.append(word)

    # Error message if the user enters invalid input!
    if len(clean_numbers) == 0:
        raise ValueError("No valid number words found! Please enter a valid number word (eg. two million twenty three thousand and forty nine)")

    # Error if user enters million,billion, thousand or decimal point twice
    if clean_numbers.count('thousand') > 1 or clean_numbers.count('million') > 1 or clean_numbers.count('billion') > 1 or clean_numbers.count('point')> 1:
        raise ValueError("Redundant number word! Please enter a valid number word (eg. two million twenty three thousand and forty nine)")

    # separate decimal part of number (if exists)
    if clean_numbers.count('point') == 1:
        clean_decimal_numbers = clean_numbers[clean_numbers.index('point')+1:]
        clean_numbers = clean_numbers[:clean_numbers.index('point')]

    billion_index = clean_numbers.index('billion') if 'billion' in clean_numbers else -1
    million_index = clean_numbers.index('million') if 'million' in clean_numbers else -1
    thousand_index = clean_numbers.index('thousand') if 'thousand' in clean_numbers else -1

    if (thousand_index > -1 and (thousand_index < million_index or thousand_index < billion_index)) or (million_index>-1 and million_index < billion_index):
        raise ValueError("Malformed number! Please enter a valid number word (eg. two million twenty three thousand and forty nine)")

    total_sum = 0  # storing the number to be returned

    if len(clean_numbers) > 0:
        # hack for now, better way TODO
        if len(clean_numbers) == 1:
                total_sum += br_number_system[clean_numbers[0]]

        else:
            if billion_index > -1:
                billion_multiplier = number_formation(clean_numbers[0:billion_index])
                total_sum += billion_multiplier * 1000000000

            if million_index > -1:
                if billion_index > -1:
                    million_multiplier = number_formation(clean_numbers[billion_index+1:million_index])
                else:
                    million_multiplier = number_formation(clean_numbers[0:million_index])
                total_sum += million_multiplier * 1000000

            if thousand_index > -1:
                if million_index > -1:
                    thousand_multiplier = number_formation(clean_numbers[million_index+1:thousand_index])
                elif billion_index > -1 and million_index == -1:
                    thousand_multiplier = number_formation(clean_numbers[billion_index+1:thousand_index])
                else:
                    thousand_multiplier = number_formation(clean_numbers[0:thousand_index])
                total_sum += thousand_multiplier * 1000

            if thousand_index > -1 and thousand_index != len(clean_numbers)-1:
                hundreds = number_formation(clean_numbers[thousand_index+1:])
            elif million_index > -1 and million_index != len(clean_numbers)-1:
                hundreds = number_formation(clean_numbers[million_index+1:])
            elif billion_index > -1 and billion_index != len(clean_numbers)-1:
                hundreds = number_formation(clean_numbers[billion_index+1:])
            elif thousand_index == -1 and million_index == -1 and billion_index == -1:
                hundreds = number_formation(clean_numbers)
            else:
                hundreds = 0
            total_sum += hundreds

    # adding decimal part to total_sum (if exists)
    if len(clean_decimal_numbers) > 0:
        decimal_sum = get_decimal_sum(clean_decimal_numbers)
        total_sum += decimal_sum

    return total_sum






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
speak("""Olá. Eu sou o assistente de voz. Fale o termo navegador para abri-lo, 
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
        #esse match é realmente necessário? talvez bastaria apenas o 'if "qlq coisa" in command'
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
                '''
            case cmd if "YOUTUBE" in cmd:
                #speak("youtube")
                driver.get("http://www.youtube.com")
                janelas_ativas = driver.window_handles
            case cmd if "INSTAGRAM" in cmd:
                speak("abrindo instagram")
                driver.get("https://www.instagram.com/")
                janelas_ativas = driver.window_handles
            case cmd if "FACEBOOK" in cmd:
                speak("abrindo Facebook")
                driver.get("https://www.facebook.com/")
                janelas_ativas = driver.window_handles
                '''
            case cmd if "FORMULÁRIO TESTE" in cmd:
                speak("abrindo practice-automation")
                driver.get("https://practice-automation.com/form-fields/")
                janelas_ativas = driver.window_handles
                '''
            #vinculado ao youtube/facebook. Desnecessário para essa parte, mas demostra como dar múltiplos cliques para chegar em um ponto
            case cmd if "CRIAR CONTA" in cmd:
                if 'youtube' in driver.current_url:
                    xpath_register1 = '/html/body/ytd-app/div[1]/div/ytd-masthead/div[4]/div[3]/div[2]/ytd-button-renderer/yt-button-shape/a/yt-touch-feedback-shape/div/div[2]'
                    botao_register1 = driver.find_element("xpath", xpath_register1)
                    botao_register1.click()
                    xpath_register2 = '/html/body/div[1]/div[1]/div[2]/c-wiz/div/div[3]/div/div[2]/div/div/div[1]/div/button/span'
                    botao_register2 = driver.find_element("xpath", xpath_register2)
                    botao_register2.click()
                    xpath_register3 = '/html/body/div[1]/div[1]/div[2]/c-wiz/div/div[3]/div/div[2]/div/div/div[2]/div/ul/li[1]'
                    botao_register3 = driver.find_element("xpath", xpath_register3)
                    botao_register3.click()
                if 'facebook' in driver.current_url:
                    xpath_register = '/html/body/div[1]/div[1]/div[1]/div/div/div/div[2]/div/div[1]/form/div[5]/a'
                    botao_register = driver.find_element("xpath", xpath_register)
                    botao_register.click()
                '''
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
                    senha_user = senha_user.replace(" ", "")
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
                    email_box.clear()
                else:
                    email_user = (command.split("E-MAIL", 1)[1]).strip()
                    email_user = email_user.replace("ARROBA", "@")
                    email_user = email_user.replace(" ", "")
                    email_user = email_user.lower()
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
                '''
            case cmd if "ABRIR VÍDEO" in cmd:
                numero_video_extenso = (command.split("ABRIR VÍDEO", 1)[1])
                numero_video_extenso = numero_video_extenso.strip()
                numero_video = word_to_num(numero_video_extenso)
                speak("Pesquisando" + str(numero_video))
                xpath_video = f'/html/body/ytd-app/div[1]/ytd-page-manager/ytd-search/div[1]/ytd-two-column-search-results-renderer/div/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/ytd-video-renderer[{numero_video}]/div[1]/div/div[1]/div/h3/a/yt-formatted-string'
                link_video = driver.find_element("xpath", xpath_video)
                link_video.click()
                '''
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