'''
import speech_recognition as sr
from thefuzz import fuzz, process
import time


recognizer = sr.Recognizer()



def listen():
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)  # Ajusta para o ruído ambiente
        print("Diga algo...")
        #audio = recognizer.listen(source, timeout=3, phrase_time_limit=6)  # Limita o tempo de escuta
        audio = recognizer.listen(source, phrase_time_limit=5)
        t = time.localtime()
        current_time = time.strftime("%H:%M:%S", t)
        print(current_time)
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



import pandas as pd

df = pd.read_csv('tabela_consulta2.csv', usecols=[0])


item = df.sample(n=1).iloc[0, 0].upper()
print(item)
exit()
command = ''
while fuzz.ratio(item, command) < 90:
    command = listen().upper()
    print(command)
    print(fuzz.ratio(item, command))

print("Frase reconhecida")
'''



import speech_recognition as sr
from thefuzz import fuzz
import pandas as pd
import time

# Setup do reconhecedor
recognizer = sr.Recognizer()

# Função para ouvir o usuário
def listen():
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        print("Diga algo...")
        audio = recognizer.listen(source, phrase_time_limit=5)
        current_time = time.strftime("%H:%M:%S", time.localtime())
        print(current_time)
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

# Lê apenas a primeira coluna do CSV
df = pd.read_csv('tabela_consulta2.csv', usecols=[0])

# Seleciona um item aleatório (valor puro, não string formatada)
item = df.sample(n=1).iloc[0, 0].upper()
print(f"Item sorteado: {item}")

# Inicializa o comando como vazio
command = ""

# Continua escutando até a similaridade ser alta o suficiente
while fuzz.ratio(item, command.upper()) < 90:
    command = listen()
    print(f"Similaridade: {fuzz.ratio(item, command.upper())}%")

print("Frase reconhecida corretamente!")
