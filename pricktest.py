from faster_whisper import WhisperModel

import warnings
warnings.filterwarnings("ignore")

model_size = "small"

#essa chave é a palavra a ser procurada. "PROFISSÃO" ou "CIVIL" ou "IDADE" ou "GÊNERO" ou "NOME"
def separa(texto, chave):
    #print("<>", chave)
    texto = texto.split()
    '''
    ############################
    for i, word in enumerate(texto):
        if word == "POR":
            words[i] = "X"
    texto = ' '.join(words)
    ############################
    '''

    if texto[-1] == "CAMPO":
        texto = texto[:-1]

    excluir = 0
    temporary = ""
    for word in texto:
        if word == chave:
            break
        else:
            excluir +=1

    temporary = " ".join(texto[:excluir])
    campo = " ".join(texto[excluir+1:])

    return temporary, campo

#from unidecode import unidecode
import os
directory = os.getcwd()
wav_files = []

for file_path in os.listdir(directory):
    # check if current file_path is a file
    if file_path.endswith('.wav'):
    #if os.path.isfile(os.path.join(files, file_path)):
        # add filename to list
        wav_files.append(file_path)
wav_files = sorted(wav_files, key=lambda t: -os.stat(t).st_mtime)
#print(wav_files)
#indexed_list = [f'{index}: {value}' for index, value in enumerate(wav_files)]
for index, value in enumerate(wav_files):
    print(f'{index}:\t{value}')
#print(indexed_list)
i = input('Escolha o indice do arquivo de áudio que você deseja: ')

model = WhisperModel(model_size, download_root="/media/assis/3fc2a7ec-618b-4235-a50a-636507205078/home/oltest3/Downloads/aaa")
segments, info = model.transcribe(wav_files[int(i)], beam_size=5, language="pt")

print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

tudo = ""
for segment in segments:
    #print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
    tudo += segment.text

tudo = tudo.upper()
tudo = tudo.replace(".", "")
tudo = tudo.replace(",", "")
#tudo = tudo.replace("UM", "1")
tudo = tudo.replace(" POR ", "X")


print("~\t", tudo)
'''
tudo = separa(tudo, "PROFISSÃO")
profissao = tudo[1]
tudo = tudo[0]

tudo = separa(tudo, "CIVIL")
eCivil = tudo[1]
tudo = tudo[0]

tudo = separa(tudo, "IDADE")
idade = tudo[1]
tudo = tudo[0]

tudo = separa(tudo, "GÊNERO")
genero = tudo[1]
tudo = tudo[0]

tudo = separa(tudo, "NOME")
nome = tudo[1]
tudo = tudo[0]
'''
campos = []
for i in range(14):
    #tudo = separa(tudo, str(i+1))
    tudo = separa(tudo, str(14-i))
    #campos.append(tudo[1])
    campos.insert(0, tudo[1])
    tudo = tudo[0]
print()
print("Valores:")
for i in range(14):
    print(campos[i])
    print()
'''
print("1. ", nome)
print("2. ", genero)
print("3. ", idade)
print("4. ", eCivil)
print("5. ", profissao)
'''
#######################################################################################

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

# Inicializa o navegador
driver = webdriver.Edge()  # Você precisa do driver do Chrome ou de outro navegador que desejar
# Abre a página de login da rede social
driver.get("https://docs.google.com/forms/d/1pk4Ecrw7ySOo1opqXJTxhD0ZUccttjQ8cFyeE1VP1Hw/edit")
time.sleep(1)
'''
campo1 = driver.find_element("xpath", '/html/body/div/div[3]/form/div[2]/div/div[2]/div[1]/div/div/div[2]/div/div[1]/div/div[1]/input')
campo1.send_keys(campos[0])
time.sleep(1)

campo2 = driver.find_element("xpath", '/html/body/div/div[3]/form/div[2]/div/div[2]/div[2]/div/div/div[2]/div/div[1]/div/div[1]/input')
campo2.send_keys(campos[1])
time.sleep(1)

campo3 = driver.find_element("xpath", '/html/body/div/div[3]/form/div[2]/div/div[2]/div[3]/div/div/div[2]/div/div[1]/div/div[1]/input')
campo3.send_keys(campos[2])
time.sleep(1)

campo4 = driver.find_element("xpath", '/html/body/div/div[3]/form/div[2]/div/div[2]/div[4]/div/div/div[2]/div/div[1]/div/div[1]/input')
campo4.send_keys(campos[3])
time.sleep(1)

campo5 = driver.find_element("xpath", '/html/body/div/div[3]/form/div[2]/div/div[2]/div[5]/div/div/div[2]/div/div[1]/div/div[1]/input')
campo5.send_keys(campos[4])
time.sleep(1)

campo6 = driver.find_element("xpath", '/html/body/div/div[3]/form/div[2]/div/div[2]/div[6]/div/div/div[2]/div/div[1]/div/div[1]/input')
campo6.send_keys(campos[5])
time.sleep(1)

campo7 = driver.find_element("xpath", '/html/body/div/div[3]/form/div[2]/div/div[2]/div[7]/div/div/div[2]/div/div[1]/div/div[1]/input')
campo7.send_keys(campos[6])
time.sleep(1)

campo8 = driver.find_element("xpath", '/html/body/div/div[3]/form/div[2]/div/div[2]/div[8]/div/div/div[2]/div/div[1]/div/div[1]/input')
campo8.send_keys(campos[7])
time.sleep(1)

campo9 = driver.find_element("xpath", '/html/body/div/div[3]/form/div[2]/div/div[2]/div[9]/div/div/div[2]/div/div[1]/div/div[1]/input')
campo9.send_keys(campos[8])
time.sleep(1)

campo10 = driver.find_element("xpath", '/html/body/div/div[3]/form/div[2]/div/div[2]/div[10]/div/div/div[2]/div/div[1]/div/div[1]/input')
campo10.send_keys(campos[9])
time.sleep(1)

campo11 = driver.find_element("xpath", '/html/body/div/div[3]/form/div[2]/div/div[2]/div[11]/div/div/div[2]/div/div[1]/div/div[1]/input')
campo11.send_keys(campos[10])
time.sleep(1)

campo12 = driver.find_element("xpath", '/html/body/div/div[3]/form/div[2]/div/div[2]/div[12]/div/div/div[2]/div/div[1]/div/div[1]/input')
campo12.send_keys(campos[11])
time.sleep(1)

campo13 = driver.find_element("xpath", '/html/body/div/div[3]/form/div[2]/div/div[2]/div[13]/div/div/div[2]/div/div[1]/div/div[1]/input')
campo13.send_keys(campos[12])
time.sleep(1)

campo14 = driver.find_element("xpath", '/html/body/div/div[3]/form/div[2]/div/div[2]/div[14]/div/div/div[2]/div/div[1]/div/div[1]/input')
campo14.send_keys(campos[13])
time.sleep(1)
'''
for i in range(1, 15):
    #xpath = '/html/body/div/div[3]/form/div[2]/div/div[2]/div[%i]/div/div/div[2]/div/div[1]/div/div[1]/input'
    xpath = '/html/body/div/div[3]/form/div[2]/div/div[2]/div[%i]/div/div/div[2]/div/div[1]/div/div[1]/input' % i
    campo = driver.find_element("xpath", xpath)
    campo.send_keys(campos[i-1])# Index starts from 0, so subtract 1 from i
    time.sleep(1)

button = driver.find_element("xpath", '/html/body/div/div[3]/form/div[2]/div/div[3]/div[1]/div[1]/div/span/span')
button.click()
time.sleep(1)

# Feche o navegador
driver.quit()
