import whisper
model = whisper.load_model("small")

import warnings
warnings.filterwarnings("ignore")

    
def transcricao(arquivo):
	result = model.transcribe(arquivo, language = 'Portuguese')
	return result['text']


#essa chave é a palavra a ser procurada. "HOBBY" ou "OCUPAÇÃO" ou "MATRÍCULA" ou "NOME"
def separa(texto, chave):
    texto = texto.split()

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

#Mostrar arquivos .wav da pasta
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

text5 = transcricao(wav_files[int(i)])
#Coloca tudo em maiúsculo, remove pontos e virgulas
#
text5 = text5.upper()
text5 = text5.replace(".", "")
text5 = text5.replace(",", "")
#
print(text5)

#Cria-se os campos e procura na string pra ir separando, isso é feito do último campo para o primeiro
hobby = ""
ocupacao = ""
matricula = ""
nome = ""


text5 = separa(text5, "HOBBY")
hobby = text5[1]



text5 = text5[0]
text5 = separa(text5, "OCUPAÇÃO")
ocupacao = text5[1]

text5 = text5[0]
text5 = separa(text5, "MATRÍCULA")
matricula = text5[1]


text5 = text5[0]
text5 = separa(text5, "NOME")
nome = text5[1]


print(":)")
print(nome)
print(matricula)
print(ocupacao)
print(hobby)



