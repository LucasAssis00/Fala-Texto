import whisper
model = whisper.load_model("small")

import warnings
warnings.filterwarnings("ignore")


    
def transcricao(arquivo):
	result = model.transcribe(arquivo, language = 'Portuguese')
	return result['text']

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

text5 = transcricao(wav_files[int(i)])
#
text5 = text5.upper()
#text5 = text5.replace(".", "")
text5 = text5.replace(",", "")
#
print(text5)

text5 = text5.split()
print(text5)
