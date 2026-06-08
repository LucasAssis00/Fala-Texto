import whisper
model = whisper.load_model("medium")

import warnings
warnings.filterwarnings("ignore")

import spacy
#nlp = spacy.load("modelo_medico_teste_dados3_1")
nlp = spacy.load("modelo_medico_teste_dados4_1")

from collections import Counter, defaultdict

    
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
#i = 0

text5 = transcricao(wav_files[int(i)])
#
text5 = text5.upper()
#text5 = text5.replace(".", "")
#
#print(text5)

#text5 = text5.split()
print(text5)
text5 = text5.replace(",", "")
#text5 = text5.replace("PRONTUÁRIO", "PRONTUARIO")
print(text5)

doc = nlp(text5)
input('Pressione "Enter" para continuar')

# --- Step 1: Show all entities ---
print("-")
for ent in doc.ents:
    print(ent.label_,"->", ent.text)
print("-")



# --- Step 2: Count occurrences ---
label_counts = Counter(ent.label_ for ent in doc.ents)
print(label_counts)

# --- Step 3: Identify labels that appear more than once ---
duplicates = {label for label, count in label_counts.items() if count > 1}

# -- Step 3.5: Colocar as não duplicadas num dicionario
registro = dict()

for ent in doc.ents:
     if label_counts[ent.label_] == 1:
          registro[ent.label_] = ent.text
#print(registro)

print()
if duplicates:
    print("These labels appear multiple times:", duplicates)
else:
    print("No labels repeated.")

#print(duplicates.keys)

# --- Step 4: Group all entities by label ---
grouped = defaultdict(list)
for ent in doc.ents:
    grouped[ent.label_].append(ent)

# --- Step 5: Ask the user ONCE for each duplicated label ---
selected_values = {}

for label in duplicates:
    print(f"\nMultiple values found for '{label}':")

    ents = grouped[label]

    for i, value in enumerate(ents, 1):
         print(f"{i}. {value.text}")
    #choice = int(input(f"Choose the correct value for '{label}' (1–{len(selected_values)}): "))
    choice = int(input(f"Choose the correct value for '{label}': "))
    selected_values[label] = ents[choice - 1]
    #selected_values[label] = value[choice - 1]
    print(selected_values[label])
    registro[label] = selected_values[label]

print('\n\n\n')
print(registro)
'''
# --- Step 6: Build new ents list: keep only chosen ones ---
new_ents = []
print(".")
for ent in doc.ents:
    print(ent)
    # Para manter a escolhida
    if ent.label_ in selected_values:
        print("*")
        if ent is selected_values[ent.label_]:
            new_ents.append(ent)
        else:
            new_ents.append
    else:
        print("#")
        print(new_ents)

# --- Step 7: Replace doc.ents with the filtered list ---
doc.ents = new_ents   

print("\nFinal selections:")
for ent in doc.ents:
    print(ent.label_, "->", ent.text)
'''
