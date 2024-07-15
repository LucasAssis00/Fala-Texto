from faster_whisper import WhisperModel
import os
import re



import time
'''
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
'''
import io

from time import sleep
import subprocess
from thefuzz import fuzz, process
from unidecode import unidecode

import pandas as pd

import unicodedata

from selenium import webdriver
from selenium.webdriver.common.keys import Keys


def remover_acentos(texto):
    # Normaliza a string para decompor os caracteres acentuados
    texto_normalizado = unicodedata.normalize('NFKD', texto)
    # Filtra os caracteres que não são combinantes (não são acentos)
    texto_sem_acento = ''.join(c for c in texto_normalizado if not unicodedata.combining(c))
    # Retorna a string resultante
    return texto_sem_acento




model_size = "small"
model = WhisperModel(model_size, download_root="/media/assis/3fc2a7ec-618b-4235-a50a-636507205078/home/oltest3/Downloads/aaa")

directory = os.getcwd()
wav_files = []

for file_path in os.listdir(directory):
    # check if current file_path is a file
    if file_path.endswith('.wav'):
    #if os.path.isfile(os.path.join(files, file_path)):
        # add filename to list
        wav_files.append(file_path)

wav_files = sorted(wav_files, key=lambda t: -os.stat(t).st_mtime)


for index, value in enumerate(wav_files):
    print(f'{index}:\t{value}')

i = input('Escolha o indice do arquivo de áudio que você deseja (etapa descrição): ')

segments, info = model.transcribe(wav_files[int(i)], beam_size=5, language="pt")


tudo = ""
for segment in segments:
    print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
    tudo += segment.text

tudo = tudo.upper()
tudo = tudo.replace(".", "")
tudo = tudo.replace(",", "")
tudo = remover_acentos(tudo)
print("1.", tudo)



def parse_input(input_string, field_names):
    # Create a pattern to match field names
    pattern = r"|".join(re.escape(field) for field in field_names)
    
    # Initialize a dictionary with field names set to empty strings
    fields = {field: '' for field in field_names}
    
    # Use regex to find all occurrences of field names
    matches = re.finditer(pattern, input_string)
    
    # Extract the positions of the matches
    field_positions = [(match.start(), match.group()) for match in matches]
    
    # Add an end position for the last field
    field_positions.append((len(input_string), ''))
    
    # Extract and map values to their respective fields
    for i in range(len(field_positions) - 1):
        start_pos, field_name = field_positions[i]
        end_pos = field_positions[i + 1][0]
        value = input_string[start_pos + len(field_name):end_pos].strip()
        if field_name in fields:
            fields[field_name] = value
    
    return fields


field_names = ["NOME", "GENERO", "IDADE", "ESTADO CIVIL", "PROFISSAO"]


outputDict = parse_input(tudo, field_names)


xpaths = {
    'NOME': '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[1]/div/div/div[2]/div/div[1]/div/div[1]/input',
    'GENERO': '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[2]/div/div/div[2]/div/div[1]/div/div[1]/input',
    'IDADE': '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[3]/div/div/div[2]/div/div[1]/div/div[1]/input',
    'ESTADO CIVIL': '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[4]/div/div/div[2]/div/div[1]/div/div[1]/input',
    'PROFISSAO': '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[5]/div/div/div[2]/div/div[1]/div/div[1]/input'
}

outputDict = {key: {'value': value, 'xpath': xpaths[key]} for key, value in outputDict.items()}
#print(outputDict)
'''
for x, y in outputDict.items():
    print(x)
    print(y['value'])
    print(y['xpath'])
'''
#print(fields_with_xpaths)


#########################################################################################################
#etapa do navegador agora
#########################################################################################################

# Inicializa o navegador
driver = webdriver.Edge()

# Abre a página do formulario
driver.get("https://docs.google.com/forms/d/1UZkASiSkVhUnS-ppKGi7mStAF14UAw5zL_YIvHMzIjM/edit")
time.sleep(1)

for campo, descricao in outputDict.items():
    posicao = driver.find_element("xpath", descricao['xpath'])
    posicao.send_keys(descricao['value'])
    time.sleep(1)

button = driver.find_element("xpath", '//*[@id="mG61Hd"]/div[2]/div/div[3]/div[1]/div[1]/div/span/span')
button.click()


# Aguarde um momento para o login ser concluído
time.sleep(1)

# Feche o navegador
driver.quit()