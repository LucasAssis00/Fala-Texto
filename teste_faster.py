from faster_whisper import WhisperModel

model_size = "small"

# Run on GPU with FP16
#model = WhisperModel(model_size, device="cuda", compute_type="float16")

# or run on GPU with INT8
# model = WhisperModel(model_size, device="cuda", compute_type="int8_float16")
# or run on CPU with INT8
#model = WhisperModel(model_size, device="cpu", compute_type="int8")



##################


model = WhisperModel(model_size, download_root="/alterar/localizacao/pasta/no/dispositivo")

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



#segments, info = model.transcribe(wav_files[int(i)], beam_size=5, language="pt")
segments, info = model.transcribe(wav_files[int(i)], beam_size=5, language="pt", initial_prompt="""Nome, Prontuário, Data, Exame, Vulvoscopia, especular, 
                                  colposcopia, lesão, Conclusão, Conduta, Examinados, Eutópico, com Cistos de naboth, Ilhotas de epitélio glandular, Deciduose de Gravidez, 
                                  EAB, tênue, Pontilhado, Orifícios, Leucoplasia, Condiloma, Estenose, Endometriose""")


print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

tudo = ""
for segment in segments:
    print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
    tudo += segment.text
    #tudo = tudo + segment.text
print("^\t", tudo)
tudo = tudo.upper()
tudo = tudo.replace(".", "")
tudo = tudo.replace(",", "")
#tudo = tudo.replace(" POR ", "X")

print("~\t", tudo)
######################
'''
print("a")
model = WhisperModel(model_size)
print("b")
segments, info = model.transcribe("redacao.wav")
print("c")
for segment in segments:
    print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
print("d")
'''
