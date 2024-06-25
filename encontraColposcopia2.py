#alterações Justino - enumerar marcações
import pdfplumber
import re
import time
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
import io

from faster_whisper import WhisperModel
import os
from unidecode import unidecode
import unicodedata
import subprocess





def remover_acentos(texto):
    # Normaliza a string para decompor os caracteres acentuados
    texto_normalizado = unicodedata.normalize('NFKD', texto)
    # Filtra os caracteres que não são combinantes (não são acentos)
    texto_sem_acento = ''.join(c for c in texto_normalizado if not unicodedata.combining(c))
    # Retorna a string resultante
    return texto_sem_acento

def ajuste_palavras_campos(texto):
   texto = texto.upper()
   #texto = texto.replace(".", "")
   texto = texto.replace(",", "")

   texto = texto.replace("TIPO 1", "TIPO-1")
   texto = texto.replace("TIPO 2", "TIPO-2")
   texto = texto.replace("TIPO 3", "TIPO-3")
   texto = texto.replace("ORIFÍCIOS GLANDULARES ABERTOS", "ORIFÍCIOS-GLANDULARES-ABERTOS")
   texto = texto.replace("EAB TÊNUE", "EAB-TÊNUE")
   texto = texto.replace("MOSAICO FINO", "MOSAICO-FINO")
   texto = texto.replace("PONTILHADO FINO", "PONTILHADO-FINO")
   texto = texto.replace("EAB DENSO", "EAB-DENSO")
   texto = texto.replace("MOSAICO GROSSEIRO", "MOSAICO-GROSSEIRO")
   texto = texto.replace("PONTILHADO GROSSEIRO", "PONTILHADO-GROSSEIRO")
   texto = texto.replace("ORIFÍCIOS GLANDULARES ESPESSADOS", "ORIFÍCIOS-GLANDULARES-ESPESSADOS")
   texto = texto.replace("IODO POSITIVO", "IODO-POSITIVO")
   texto = texto.replace("IODO NEGATIVO", "IODO-NEGATIVO")
   texto = texto.replace("ZONA DE TRANSFORMAÇÃO CONGÊNITA", "ZONA-DE-TRANSFORMAÇÃO-CONGÊNITA")

   return texto

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
    if(index == 9):
        break

i = input('Escolha o indice do arquivo de áudio que você deseja (etapa descrição): ')

segments, info = model.transcribe(wav_files[int(i)], beam_size=5, language="pt", initial_prompt="Nome, Prontuário, Data, Exame, Vulvoscopia, especular, Colposcopia, lesão, Conclusão, Conduta, Examinados")


tudo = ""
for segment in segments:
    print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
    tudo += segment.text

tudo = ajuste_palavras_campos(tudo)


print(tudo)
print()

patterns = {
    'NOME': r'NOME\s+(.*?)\s+PRONTUÁRIO',
    #'PRONTUÁRIO': r'PRONTUÁRIO\s+(\d+)\s+DATA',
    'PRONTUÁRIO': r'PRONTUÁRIO\s+(.*?)\s+DATA',
    'DATA': r'DATA\s+(.*?)\s+IDENTIFICAÇÃO',
    #'IDENTIFICAÇÃO DO EXAME': r'IDENTIFICAÇÃO DO EXAME\s+(.*?)\s+VULVOSCOPIA',
    'IDENTIFICAÇÃO DO EXAME': r'IDENTIFICAÇÃO DO EXAME\s+(.*?)\s+(?=(VULVOSCOPIA|EXAME ESPECULAR|COLPOSCOPIA))',
    #'VULVOSCOPIA': r'VULVOSCOPIA\s+(.*?)\s+EXAME',
    'VULVOSCOPIA': r'VULVOSCOPIA\s+(.*?)\s+(?=(EXAME ESPECULAR|COLPOSCOPIA))',
    'EXAME ESPECULAR': r'EXAME ESPECULAR\s+(.*?)\s+(?=(COLPOSCOPIA|AVALIAÇÃO|LOCALIZAÇÃO|CONCLUSÃO))',
    'LOCALIZAÇÃO DA LESÃO': r'LOCALIZAÇÃO DA LESÃO\s+(.*?)\s+(?=(GRAU|SUSPEITA|VASOS|SINAIS|CONCLUSÃO))',
    #'LOCALIZAÇÃO DA LESÃO': r'LOCALIZAÇÃO DA LESÃO\s+(.*?)\s+GRAU',
    'CONCLUSÃO': r'CONCLUSÃO\s+(.*?)\s+CONDUTA',
    'CONDUTA': r'CONDUTA\s+(.*?)\s+EXAMINADOS',
    'EXAMINADOS': r'EXAMINADOS\s+(.*)'
}

dados = {}
for campo, pattern in patterns.items():
    match = re.search(pattern, tudo, re.IGNORECASE)

    if match:
        dados[campo] = match.group(1).strip()
    else:
        dados[campo] = ""

for campo, valor in dados.items():
    print(f"{campo}: {valor}")

field_names = ["NOME", "PRONTUARIO", "DATA", "IDENTIFICACAO DO EXAME", "VULVOSCOPIA", "EXAME ESPECULAR", "CONCLUSAO", "CONDUTA", "EXAMINADOS"]

outputDict = parse_input(tudo, field_names)
#print("u.u", outputDict)


laudo = {'Vulvoscopia':'AA','especular':'AA','Conclusão':'AA','Conduta':'AA','Examinados':'AA'}

campo = []
padrao =  r"\w+_$"
padrao2 = r"\)\w+"

enumeracao = 0

with pdfplumber.open('Laudo4.pdf') as leitor:
    for i in range(len(leitor.pages)):
      page = leitor.pages[i]
      palavra = page.extract_words()
      for j in palavra:
        #if re.match(padrao, j['text']) or re.match(padrao2, j['text']):
        if re.match(padrao2, j['text']):
          campo.append(j)

print(".")
#print(campo[0].values())
# Extract 'text' values using list comprehension
'''
texts = [item['text'] for item in campo]
for palavra in texts:
    print(palavra)
    #palavra = palavra.upper()
    #palavra = palavra.replace("_", "")
    #palavra = palavra.replace(")", "")
# Print the extracted texts
#print(texts)
'''
print("oi bb", campo)

procedimentos = []
for item in campo:
   palavra = item['text'].replace('_', '')
   palavra = palavra.replace(')', '')
   palavra = palavra.upper()
   procedimentos.append(palavra)

#que porra é essa?
'''
while(procedimentos[0] != 'SATISFATÓRIA'):
   procedimentos.pop(0)
'''
#print(procedimentos)
#print(type(procedimentos))
#print(len(procedimentos))


foidito = []

for procedimento in procedimentos:
   foidito.append(procedimento in tudo.split())

'''
for i in range(len(procedimentos)):
   print(procedimentos[i])
   print(foidito[i])
'''


for c in campo:
  if re.match(r"^Data_", c['text']):
    laudo[c['text']] = ['02','05','2024']
  else:
      if (foidito[enumeracao]):
         laudo[c['text']] = 'x'
      else:
         laudo[c['text']] = ''
      '''
      laudo[c['text']] = str(enumeracao)
      '''
      enumeracao+=1


print(laudo)
l = []
with pdfplumber.open('Laudo4.pdf') as pdf:
    for i in range(len(pdf.pages)):
      page = pdf.pages[i]
      d = {}
      for chave, valor in laudo.items():
          if re.match(padrao2, chave):
            dados = page.search(chave[1:],return_groups=False, return_chars=True, layout=False)
          else:
            dados = page.search(chave,return_groups=False, return_chars=True, layout=False)

          if len(dados) != 0:
            if re.match(padrao2, chave):
              if chave == ')Zona':
                x = 224.82
                y = 240.32
                d[chave] = (x+77,y)
              else:
                x = dados[0]['x0']
                y = dados[0]['chars'][0]['y0']
                d[chave] = (x-11,y+3)
            elif chave == 'especular':
              x = dados[0]['x0']
              y = dados[0]['chars'][0]['y0']
              d[chave] = (x-30,y-7)
            else:
              x = dados[0]['x0']
              y = dados[0]['chars'][0]['y0']
              d[chave] = (x,y-7)

          l.append(d)


existing_pdf = PdfReader(open('Laudo4.pdf', 'rb'))
output = PdfWriter()

# Criar um novo PDF com o ReportLab para sobrepor o existente
for i in range(len(existing_pdf.pages)):
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=letter)
    c.setFont('Times-Roman',9)

    for chave, valor in laudo.items():
      if chave in l[i].keys():
        if type(valor) is str:
          c.drawString(l[i][chave][0],l[i][chave][1], valor)
        else:
            c.drawString(l[i][chave][0],l[i][chave][1], valor[0])
            c.drawString(l[i][chave][2],l[i][chave][3], valor[1])
            c.drawString(l[i][chave][4],l[i][chave][5], valor[2])


    c.save()
    packet.seek(0)
    new_pdf = PdfReader(packet)
    page = existing_pdf.pages[i]
    page.merge_page(new_pdf.pages[0])
    output.add_page(page)


  # Salvar o PDF resultante
with open('pdf_editado.pdf', 'wb') as output_pdf:
    output.write(output_pdf)

print("PDF editado salvo como 'pdf_editado.pdf'")
