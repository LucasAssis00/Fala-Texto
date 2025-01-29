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
            print(f"Você disse: {command}")
            return command
        except sr.UnknownValueError:
            print("Não entendi o que você disse.")
            return ""
        except sr.RequestError:
            print("Erro ao se comunicar com o serviço de reconhecimento de voz.")
            return ""
'''
        case cmd if "NAVEGADOR" in cmd:
            print(cmd)
            speak("Abrindo o navegador")
            driver = webdriver.Edge()
        case cmd if "FORMULÁRIO" in cmd:
            speak("ABRINDO LISTA DE VERIFICAÇÃO DA CIRURGIA SEGURA")
            driver.get("https://forms.gle/XZ2Yxms98WCVFbNN9")
            
        case cmd if "PACIENTE" in cmd:
            nome_user = (command.split("PACIENTE", 1)[1]).strip()
            search_box = driver.find_element("xpath", '/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/input[1]')
            search_box.send_keys(nome_user)
            
'''
driver = webdriver.Edge()
driver.get("https://forms.gle/XZ2Yxms98WCVFbNN9")
while True:
    command = listen().upper()  # string
    match command:
        case cmd if "PRONTUÁRIO" in cmd:
            senha_user = (command.split("PRONTUÁRIO", 1)[1]).strip()
            search_box = driver.find_element("xpath", '/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[2]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/input[1]')
            search_box.send_keys(senha_user)
        case cmd if "SALA" in cmd:
            senha_user = (command.split("SALA", 1)[1]).strip()
            search_box = driver.find_element("xpath", '/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[3]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/input[1]')
            search_box.send_keys(senha_user)
            '''
        case cmd if "CONFIRMAÇÃO DOS DADOS" in cmd:#precisa estar junto lá em cima, devido a muito provavelmente falar a palavra 'paciente aqui
            if 'NÃO' in cmd:
                botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[14]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[2]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                botao_cor.click()
            else:
                botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[14]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[1]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                botao_cor.click()
 
            elif "CONFIRMAÇÃO" in cmd and "VERBAL" in cmd:
                if 'NÃO' in cmd:
                    botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[14]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[2]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                    botao_cor.click()
                else:
                    botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[14]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[1]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                    botao_cor.click()
                
            elif "CONFIRMAÇÃO DOS DADOS" in cmd:
                pass
            else:
                nome_user = (command.split("PACIENTE", 1)[1]).strip()
                search_box = driver.find_element("xpath", '/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/input[1]')
                search_box.send_keys(nome_user)'''
        case cmd if (("SÍTIO" in cmd and "DEMARCADO" in cmd) or "LATERALIDADE" in cmd):
            if 'NÃO SE APLICA' in cmd:
                botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[6]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[3]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                botao_cor.click()
            elif 'NÃO' in cmd:
                botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[6]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[2]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                botao_cor.click()
            else:
                botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[6]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[1]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                botao_cor.click()
                #VER LÓGICA PARA 'NÃO SE APLICA' 
        case cmd if "SEGURANÇA ANESTÉSICA" in cmd:
            if 'MONTAGEM DA SO' in cmd:
                botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[7]/div[1]/div[1]/div[2]/div[1]/div[1]/label[1]/div[1]/div[2]/div[1]/span[1]")
                botao_cor.click()
            if 'MATERIAL ANESTÉSICO' in cmd:
                botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[7]/div[1]/div[1]/div[2]/div[1]/div[2]/label[1]/div[1]/div[2]/div[1]/span[1]")
                botao_cor.click()
            if not 'MONTAGEM DA SO' in cmd and not 'MATERIAL ANESTÉSICO' in cmd:
                #botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[7]/div[1]/div[1]/div[2]/div[1]/div[3]/label[1]/div[1]/div[2]/div[1]/span[1]")
                botao_cor = driver.find_element("xpath", "/html/body/div/div[2]/form/div[2]/div/div[2]/div[7]/div/div/div[2]/div[1]/div[3]/div/label/div/div[2]/div/span")
                botao_cor.click()
                texto_excecao = (command.split("ANESTÉSICA", 1)[1]).strip()
                search_box = driver.find_element("xpath", '/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[7]/div[1]/div[1]/div[2]/div[1]/div[3]/div[1]/div[1]/div[1]/div[1]/div[1]/input[1]')
                search_box.send_keys(texto_excecao)
        case cmd if "VIA AÉREA" in cmd:#podemos utilizar aqui fácil ou desobstruida?; como fazer para "NÂO ACESSIVEL"?
            if 'FÁCIL' in cmd or 'DESOBSTRUÍDA' in cmd or 'ACESSÍVEL' in cmd:
                botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[8]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[1]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                
                botao_cor.click()
            else:
                botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[8]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[2]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                #botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[8]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[1]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                botao_cor.click()
            #if 'NÃO' in cmd:
            #    botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[8]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[1]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
            #    botao_cor.click()
            #else:
            #    botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[8]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[2]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
            #    botao_cor.click()
        case cmd if "PERDA SANGUÍNEA" in cmd:
            if 'NÃO' in cmd:
                botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[9]/div[1]/div[1]/div[2]/div[1]/div[2]/label[1]/div[1]/div[2]/div[1]/span[1]")
                botao_cor.click()
            else:
                botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[9]/div[1]/div[1]/div[2]/div[1]/div[1]/label[1]/div[1]/div[2]/div[1]/span[1]")
                botao_cor.click()
            if 'RESERVA DE SANGUE DISPONÍVEL' in cmd or 'RESERVA DISPONÍVEL' in cmd:
                botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[9]/div[1]/div[1]/div[2]/div[1]/div[3]/label[1]/div[1]/div[2]/div[1]/span[1]")
                botao_cor.click()
        case cmd if "ACESSO VENOSO" in cmd:
            if 'NÃO' in cmd or 'INADEQUADO' in cmd :
                botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[10]/div[1]/div[1]/div[2]/div[1]/div[2]/label[1]/div[1]/div[2]/div[1]/span[1]")
                botao_cor.click()
            else:
                botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[10]/div[1]/div[1]/div[2]/div[1]/div[1]/label[1]/div[1]/div[2]/div[1]/span[1]")
                botao_cor.click()
            if 'PROVIDENCIADO NA SO' in cmd:
                botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[10]/div[1]/div[1]/div[2]/div[1]/div[3]/label[1]/div[1]/div[2]/div[1]/span[1]")
                botao_cor.click()
        case cmd if "REAÇÃO ALÉRGICA" in cmd:
            if 'NÃO' in cmd or 'SEM' in cmd:
                botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[11]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[1]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                botao_cor.click()
            else:
                botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[11]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[2]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                botao_cor.click()
                texto_excecao = (command.split("ALÉRGICA", 1)[1]).strip()
                search_box = driver.find_element("xpath", '/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[11]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[2]/div[1]/span[1]/div[1]/div[1]/div[1]/input[1]')
                search_box.send_keys(texto_excecao)
        #2. ANTES DA INCISÃO CIRÚRGICA--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        case cmd if "APRESENTAÇÃO ORAL" in cmd:
            if 'NÃO' in cmd:
                botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[13]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[2]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                botao_cor.click()
            else:
                botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[13]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[1]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                botao_cor.click()
        case cmd if "CONFIRMAÇÃO VERBAL" in cmd or "DADOS DO PACIENTE" in cmd:#precisa estar junto lá em cima, devido a muito provavelmente falar a palavra 'paciente aqui
            if 'NÃO' in cmd:
                botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[14]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[2]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                botao_cor.click()
            else:
                botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[14]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[1]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                botao_cor.click()
        case cmd if "ANTIBIÓTICO PROFILÁTICO" in cmd:
            if 'NÃO SE APLICA' in cmd:
                botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[15]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[3]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                botao_cor.click()
            elif 'NÃO' in cmd:
                botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[15]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[2]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                botao_cor.click()
            else:
                botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[15]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[1]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                botao_cor.click()
        #case cmd if "MOMENTOS CRÍTICOS" in cmd:
        case cmd if "REVISÃO DO CIRURGIÃO" in cmd or "MOMENTOS CRÍTICOS" in cmd:
            if 'NÃO' in cmd:
                botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[16]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[2]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                botao_cor.click()
            else:
                botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[16]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[1]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                botao_cor.click()
        case cmd if "REVISÃO DO ANESTESISTA" in cmd or (("PREOCUPAÇÃO" in cmd or "PREOCUPAÇÕES" in cmd and "PACIENTE" in cmd)):
            if 'NÃO' in cmd:
                botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[17]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[2]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                botao_cor.click()
            else:
                botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[17]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[1]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                botao_cor.click()
        #case cmd if "PREOCUPAÇÃO EM RELAÇÃO AO PACIENTE" in cmd:
        case cmd if "ESTERILIZAÇÃO DO MATERIAL CIRÚRGICO" in cmd:
            if 'NÃO' in cmd:
                botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[18]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[2]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                botao_cor.click()
            else:
                botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[18]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[1]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                botao_cor.click()
        case cmd if "PLACA DE ELETROCAUTÉRIO" in cmd:
            if 'NÃO' in cmd:
                botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[19]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[2]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                botao_cor.click()
            else:
                botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[19]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[1]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                botao_cor.click()
        case cmd if "DISPONÍVEIS E FUNCIONANTES" in cmd or "EQUIPAMENTOS DISPONÍVEIS" in cmd or "EQUIPAMENTOS FUNCIONANTES" in cmd:
            if 'NÃO' in cmd:#^VER SE ISSO AQUI TEM UMA FORMA MAIS EFICIENTE DE ESCREVER
                botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[20]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[2]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                botao_cor.click()
            else:
                botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[20]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[1]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                botao_cor.click()
        case cmd if "INSUMOS E INSTRUMENTAIS" in cmd:
            if 'NÃO' in cmd or 'INDISPONÍVEIS' in cmd:
                botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[21]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[2]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                botao_cor.click()
            else:
                botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[21]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[1]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                botao_cor.click()
        case cmd if "PROCEDIMENTO" in cmd and "REALIZADO" in cmd:
            if 'NÃO' in cmd:
                botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[23]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[2]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                botao_cor.click()
            else:
                botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[23]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[1]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                botao_cor.click()
        case cmd if "CONTAGEM DE COMPRESSAS" in cmd:
            if 'NÃO SE APLICA' in cmd:
                botao_cor3 = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[24]/div[1]/div[1]/div[2]/div[1]/div[3]/label[1]/div[1]/div[2]/div[1]/span[1]")
                botao_cor3.click()
            elif 'NÃO' in cmd:
                botao_cor3 = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[24]/div[1]/div[1]/div[2]/div[1]/div[2]/label[1]/div[1]/div[2]/div[1]/span[1]")
                botao_cor3.click()
            else:
                botao_cor3 = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[24]/div[1]/div[1]/div[2]/div[1]/div[1]/label[1]/div[1]/div[2]/div[1]/span[1]")
                botao_cor3.click()
            #if not 'NÃO' in cmd and not 'HOUVE' in cmd:
            if 'ENTREGUES' in cmd:
                botao_cor3 = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[24]/div[1]/div[1]/div[2]/div[1]/div[4]/div[1]/label[1]/div[1]/div[2]/div[1]/span[1]")
                botao_cor3.click()
                texto_excecao3 = (command.split("ENTREGUES", 1)[1]).strip()
                search_box3 = driver.find_element("xpath", '/html/body/div/div[2]/form/div[2]/div/div[2]/div[24]/div/div/div[2]/div[1]/div[4]/div/div/div/div/div[1]/input')
                search_box3.send_keys(texto_excecao3)
        case cmd if "CONTAGEM DE INSTRUMENTOS" in cmd:
            if 'NÃO SE APLICA' in cmd:
                botao_cor1 = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[25]/div[1]/div[1]/div[2]/div[1]/div[3]/label[1]/div[1]/div[2]/div[1]/span[1]")
                botao_cor1.click()
            elif 'NÃO' in cmd:
                botao_cor1 = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[25]/div[1]/div[1]/div[2]/div[1]/div[2]/label[1]/div[1]/div[2]/div[1]/span[1]")
                botao_cor1.click()
            else:
                botao_cor1 = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[25]/div[1]/div[1]/div[2]/div[1]/div[1]/label[1]/div[1]/div[2]/div[1]/span[1]")
                botao_cor1.click()
            if 'ENTREGUES' in cmd:
                botao_cor1 = driver.find_element("xpath", "/html/body/div/div[2]/form/div[2]/div/div[2]/div[25]/div/div/div[2]/div[1]/div[4]/div/div/div/div/div[1]/input")
                botao_cor1.click()
                texto_excecao1 = (command.split("ENTREGUES", 1)[1]).strip()
                search_box1 = driver.find_element("xpath", '/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[25]/div[1]/div[1]/div[2]/div[1]/div[4]/div[1]/div[1]/div[1]/div[1]/div[1]/input[1]')
                search_box1.send_keys(texto_excecao1)
        case cmd if "CONTAGEM DE AGULHAS" in cmd:
            if 'NÃO SE APLICA' in cmd:
                botao_cor2 = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[26]/div[1]/div[1]/div[2]/div[1]/div[3]/label[1]/div[1]/div[2]/div[1]/span[1]")
                botao_cor2.click()
            elif 'NÃO' in cmd:
                botao_cor2 = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[26]/div[1]/div[1]/div[2]/div[1]/div[2]/label[1]/div[1]/div[2]/div[1]/span[1]")
                botao_cor2.click()
            else:
                botao_cor2 = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[26]/div[1]/div[1]/div[2]/div[1]/div[1]/label[1]/div[1]/div[2]/div[1]/span[1]")
                botao_cor2.click()
            if 'ENTREGUES' in cmd:
                botao_cor2 = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[26]/div[1]/div[1]/div[2]/div[1]/div[4]/div[1]/div[1]/div[1]/div[1]/div[1]/input[1]")
                botao_cor2.click()
                texto_excecao2 = (command.split("ENTREGUES", 1)[1]).strip()
                search_box2 = driver.find_element("xpath", '/html/body/div/div[2]/form/div[2]/div/div[2]/div[26]/div/div/div[2]/div[1]/div[4]/div/div/div/div/div[1]/input')
                search_box2.send_keys(texto_excecao2)
        case cmd if "AMOSTRA CIRÚRGICA" in cmd or "IDENTIFICADA ADEQUADAMENTE" in cmd:
            if 'NÃO SE APLICA' in cmd:
                botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[27]/div[1]/div[1]/div[2]/div[1]/div[3]/label[1]/div[1]/div[2]/div[1]/span[1]")
                botao_cor.click()
            elif 'NÃO' in cmd:
                botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[27]/div[1]/div[1]/div[2]/div[1]/div[2]/label[1]/div[1]/div[2]/div[1]/span[1]")
                botao_cor.click()
            else:
                botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[27]/div[1]/div[1]/div[2]/div[1]/div[1]/label[1]/div[1]/div[2]/div[1]/span[1]")
                botao_cor.click()
            if 'REQUISIÇÃO COMPLETA' in cmd:
                botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[27]/div[1]/div[1]/div[2]/div[1]/div[4]/label[1]/div[1]/div[2]/div[1]/span[1]")
                botao_cor.click()
                #texto_excecao = (command.split("COMPRESSAS", 1)[1]).strip()
                #search_box = driver.find_element("xpath", '/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[27]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[4]/div[1]/span[1]/div[1]/div[1]/div[1]/input[1]')
                #search_box.send_keys(texto_excecao)
        case cmd if "PROBLEMA COM EQUIPAMENTOS" in cmd or "PROBLEMAS COM EQUIPAMENTOS" in cmd:
            if 'NÃO' in cmd:
                botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[28]/div[1]/div[1]/div[2]/div[1]/div[2]/label[1]/div[1]/div[2]/div[1]/span[1]")
                botao_cor.click()
            else:
                botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[28]/div[1]/div[1]/div[2]/div[1]/div[1]/label[1]/div[1]/div[2]/div[1]/span[1]")
                botao_cor.click()
            if 'COMUNICADO À ENFERMEIRA' in cmd:
                botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[28]/div[1]/div[1]/div[2]/div[1]/div[2]/label[1]/div[1]/div[2]/div[1]/span[1]")
                botao_cor.click()
        case cmd if (("RECOMENDAÇÕES" in cmd or "RECOMENDAÇÃO" in cmd) and "CIRURGIÃO" in cmd):
            senha_user = (command.split("CIRURGIÃO", 1)[1]).strip()
            search_box = driver.find_element("xpath", '/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[30]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/input[1]')
            search_box.send_keys(senha_user)
        case cmd if (("RECOMENDAÇÕES" in cmd or "RECOMENDAÇÃO" in cmd) and "ANESTESISTA" in cmd):
            senha_user = (command.split("ANESTESISTA", 1)[1]).strip()
            search_box = driver.find_element("xpath", '/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[31]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/input[1]')
            search_box.send_keys(senha_user)
        case cmd if (("RECOMENDAÇÕES" in cmd or "RECOMENDAÇÃO" in cmd) and "ENFERMAGEM" in cmd):
            senha_user = (command.split("ENFERMAGEM", 1)[1]).strip()
            search_box = driver.find_element("xpath", '/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[32]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/input[1]')
            search_box.send_keys(senha_user)
        case cmd if "PACIENTE" in cmd:# and ("CONFIRMOU" in cmd or "CONFIRMADO" in cmd):
            #if "CONFIRMOU" in cmd:
            if "CONFIRMOU" in cmd or "CONFIRMADO" in cmd:
                if 'IDENTIDADE' in cmd:
                    #botao_bebida = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[5]/div[1]/div[1]/div[2]/div[1]/div[1]/label[1]/div[1]/div[1]/div[2]")
                    botao_bebida = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[5]/div[1]/div[1]/div[2]/div[1]/div[1]/label[1]/div[1]/div[2]/div[1]/span[1]")
                    botao_bebida.click()
                if 'PROCEDIMENTO' in cmd:
                    botao_bebida = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[5]/div[1]/div[1]/div[2]/div[1]/div[2]/label[1]/div[1]/div[2]/div[1]/span[1]")
                    botao_bebida.click()
                if 'SÍTIO CIRÚRGICO' in cmd:
                    botao_bebida = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[5]/div[1]/div[1]/div[2]/div[1]/div[3]/label[1]/div[1]/div[2]/div[1]/span[1]")
                    botao_bebida.click()
                if 'CONSENTIMENTO' in cmd:
                    botao_bebida = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[5]/div[1]/div[1]/div[2]/div[1]/div[4]/label[1]/div[1]/div[2]/div[1]/span[1]")
                    botao_bebida.click()
            elif "NOME" in cmd:
                nome_user = (command.split("PACIENTE", 1)[1]).strip()
                search_box = driver.find_element("xpath", '/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/input[1]')
                search_box.send_keys(nome_user)
        #case cmd if (("SÍTIO" in cmd and "DEMARCADO" in cmd) or "LATERALIDADE" in cmd):
        case cmd if "ENVIAR" in cmd:
                botao_avanca = driver.find_element("xpath", '/html/body/div/div[2]/form/div[2]/div/div[3]/div[1]/div[1]/div/span/span')
                botao_avanca.click()
        case cmd if "SAIR" in cmd:
                #botao_avanca = driver.find_element("xpath", '/html/body/div/div[2]/form/div[2]/div/div[3]/div[1]/div[1]/div/span/span')
                #botao_avanca.click()
                try:
                    driver.quit()
                except:
                    pass
                break