from faster_whisper import WhisperModel
import os

import pdfplumber
import re
import time
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
import io

def ajuste_palavras_campos(texto):
   texto = texto.upper()
   #texto = texto.replace(".", "")
   #texto = texto.replace(",", "")

   texto = texto.replace("NOME,", "NOME")
   texto = texto.replace(", PRONTUÁRIO,", " PRONTUÁRIO")
   texto = texto.replace(", DATA,", " DATA")
   texto = texto.replace(", INDICAÇÃO DO EXAME,", " INDICAÇÃO DO EXAME")
   texto = texto.replace(", VULVOSCOPIA,", " VULVOSCOPIA")
   texto = texto.replace(", EXAME ESPECULAR,", " EXAME ESPECULAR")
   texto = texto.replace(", LOCALIZAÇÃO DA LESÃO,", " LOCALIZAÇÃO DA LESÃO")
   texto = texto.replace(", CONCLUSÃO,", " CONCLUSÃO")
   texto = texto.replace(", CONDUTA,", " CONDUTA")
   texto = texto.replace(", EXAMINADOR,", " EXAMINADOR")



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

   texto = texto.replace("POLIPO", "PÓLIPO")   

   return texto


def substituir_mes_por_numero(data_str):
    # Expressão regular para encontrar o nome do mês
    pattern = re.compile(r'\b(' + '|'.join(meses.keys()) + r')\b')
    
    # Função de substituição
    def replace(match):
        return meses[match.group(0)]
    
    # Substituir o nome do mês pelo número correspondente
    return pattern.sub(replace, data_str)

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

#segments, info = model.transcribe(wav_files[int(i)], beam_size=5, language="pt")
#segments, info = model.transcribe(wav_files[int(i)], beam_size=5, language="pt", initial_prompt="Nome, Prontuário, Data, Exame, Vulvoscopia, especular, colposcopia, lesão, Conclusão, Conduta, Examinados")
segments, info = model.transcribe(wav_files[int(i)], beam_size=5, language="pt", initial_prompt="""Nome, Prontuário, Data, Exame, Vulvoscopia, especular, 
                                  colposcopia, lesão, Conclusão, Conduta, Examinador, Trófico, Atrófico, Ectopia, com Cistos de naboth, Ilhotas de epitélio glandular, Deciduose de Gravidez, 
                                  EAB, tênue, Pontilhado, Orifícios, Leucoplasia, Condiloma, Estenose, Endometriose, exérese""")

tudo = ""
for segment in segments:
    #print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
    tudo += segment.text
tudo = ajuste_palavras_campos(tudo)
'''
tudo = tudo.upper()
tudo = tudo.replace(",", "")
'''

print(tudo)

patterns = {
    #'Nome': r'(?=(NOME|NOME,))\s+(.*?)\s+(?=(DATA|DATA,|PRONTUÁRIO|PRONTUÁRIO,|IDENTIFICAÇÃO|IDENTIFICAÇÃO,))',
    'Nome': r'NOME\s+(.*?)\s+(?=(DATA|PRONTUÁRIO|IDENTIFICAÇÃO))',
    #'PRONTUÁRIO': r'PRONTUÁRIO\s+(\d+)\s+DATA',
    'Prontuário': r'PRONTUÁRIO\s+(.*?)\s+(?=(DATA|IDENTIFICAÇÃO))',
    #'Data': r'DATA\s+(\d+)\s+DE\s+(\d+)\s+DE\s+(\d+)\s+IDENTIFICAÇÃO',
    'Data': r'DATA\s+(.*?)\s+INDICAÇÃO',
    #'IDENTIFICAÇÃO DO EXAME': r'IDENTIFICAÇÃO DO EXAME\s+(.*?)\s+VULVOSCOPIA',
    'Indicação do Exame': r'INDICAÇÃO DO EXAME\s+(.*?)\s+(?=(VULVOSCOPIA|EXAME ESPECULAR|COLPOSCOPIA))',
    #'VULVOSCOPIA': r'VULVOSCOPIA\s+(.*?)\s+EXAME',
    'Vulvoscopia': r'VULVOSCOPIA\s+(.*?)\s+(?=(EXAME ESPECULAR|COLPOSCOPIA))',
    'Exame especular': r'EXAME ESPECULAR\s+(.*?)\s+(?=(COLPOSCOPIA|AVALIAÇÃO|LOCALIZAÇÃO|CONCLUSÃO))',
    'Localização da lesão': r'LOCALIZAÇÃO DA LESÃO\s+(.*?)\s+(?=(GRAU|SUSPEITA|VASOS|SINAIS|CONCLUSÃO))',
    #'LOCALIZAÇÃO DA LESÃO': r'LOCALIZAÇÃO DA LESÃO\s+(.*?)\s+GRAU',
    'Conclusão': r'CONCLUSÃO\s+(.*?)\s+(?=(CONDUTA|EXAMINADOR|EXAMINADORA))',
    'Conduta': r'CONDUTA\s+(.*?)\s+(?=(EXAMINADOR|EXAMINADORA))',
    #'Examinador': r'(?=(EXAMINADOR|EXAMINADORA))\s+(.*)'
    'Examinador': r'EXAMINADOR\s+(.*)'
}

meses = {
    'JANEIRO': '1', 'FEVEREIRO': '2', 'MARÇO': '3', 'ABRIL': '4',
    'MAIO': '5', 'JUNHO': '6', 'JULHO': '7', 'AGOSTO': '8',
    'SETEMBRO': '9', 'OUTUBRO': '10', 'NOVEMBRO': '11', 'DEZEMBRO': '12'
}

dados = {}
for campo, pattern in patterns.items():
    match = re.search(pattern, tudo, re.IGNORECASE)

    if match:
        dados[campo] = match.group(1).strip()
        
        if campo == 'Data':
           print("lobinho")
           gambiarra = match.group(1).strip()
           gambiarra = substituir_mes_por_numero(gambiarra).split()
           dados[campo] = gambiarra[0] + '          ' + gambiarra[2] + '          ' + gambiarra[4]
           #print(gambiarra[0] + ' ' + gambiarra[2] + ' ' + gambiarra[4])
        else:
           dados[campo] = match.group(1).strip()
        
    else:
        dados[campo] = ""

for campo, valor in dados.items():
    print(f"{campo}: {valor}")

'''
dic_text = {'Conclusão':'AA', 'Nome':'paulo', 'Data':['16','07','2024'], 'Satisfatória':True,'Tipo 2':True,'Iodo positivo':True,'Prontuário':'dsddfg',
'Exame especular':'kdhfskehu','Localização da lesão':'dkjgrdgl','Vasos atípicos':True}
'''
arquivo = 'Laudo4.pdf'


def Encontrar_campos(arquivo):
  laudo = {'Vulvoscopia':'','especular':'','Conclusão':'','Conduta':'','Examinador':''}

  campo = []
  padrao =  r"\w+_$"
  padrao2 = r"\)\w+"

  enumeracao = 0

  with pdfplumber.open(arquivo) as leitor:
    for i in range(len(leitor.pages)):
      page = leitor.pages[i]
      palavra = page.extract_words()
      for j in palavra:
        if re.match(padrao, j['text']) or re.match(padrao2, j['text']):
          campo.append(j)

  procedimentos = []
  for item in campo:
     palavra = item['text'].replace('_', '')
     palavra = palavra.replace(')', '')
     palavra = palavra.upper()
     procedimentos.append(palavra)
  
  foidito = []
  
  for procedimento in procedimentos:
     foidito.append(procedimento in tudo)
     #foidito.append(procedimento in tudo.split())

  print("::))")
  '''
  for i in range(len(procedimentos)):
     print(procedimentos[i], foidito[i])

  '''
  for c in campo:
    if re.match(r"^Data_", c['text']):
      laudo[c['text']] = ['0','0','0']
    else:
      enumeracao+=1
      #laudo[c['text']] = ''
      if (foidito[enumeracao]):
         laudo[c['text']] = 'x'
      else:
         laudo[c['text']] = ''
      #enumeracao+=1

  l = []
  with pdfplumber.open(arquivo) as pdf:
    for i in range(len(pdf.pages)):
      page = pdf.pages[i]
      d = {}
      for chave, valor in laudo.items():
          if re.match(padrao2, chave):
            dados = page.search(chave[1:],return_groups=False, return_chars=True, layout=False)
          else:
            dados = page.search(chave,return_groups=False, return_chars=True, layout=False)

          if len(dados) != 0:
            if re.match(padrao, chave):
              if re.match(r"^Data_", chave):
                x = dados[0]['x0']
                y = dados[0]['chars'][0]['y0']
                d[chave] = (x+25,y+2,x+55,y+2,x+78,y+2)
              elif re.match(r"^Prontuário_", chave):
                x = dados[0]['x0']
                y = dados[0]['chars'][0]['y0']
                d[chave] = (x+45,y+2)
              else:
                x = dados[0]['x0']
                y = dados[0]['chars'][0]['y0']
                d[chave] = (x+30,y+2)
            elif re.match(padrao2, chave):
              if chave == ')Zona-de-transformação-congênita':
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
  return l, laudo


l, laudo = Encontrar_campos(arquivo)

## Realiza a assimilação das informações oriundas da fala para preencher os campos mencionados
for chave, valor in dados.items():
  for c, v in laudo.items():
    if '_' in c:
      p = c.find('_')
      if len(chave.split()) == 1:
        if chave == c[:p]:
          laudo[c] = valor

      else:
        if chave.split()[-1] == c[:p]:
          laudo[c] = valor

    elif ')' in c and '-' in c:
      if c.replace('-',' ')[1:] == chave and valor == True:
          laudo[c] = 'x'

    elif ')' in c and '-' not in c:
      if c[1:] == chave.split()[0] and valor == True:
          laudo[c] = 'x'

    else:
      if len(chave.split()) == 1 and chave == c:
          laudo[c] = valor
      elif len(chave.split()) > 1 and chave.split()[-1] == c:
          laudo[c] = valor


def Preencher_fomulario(arquivo,l,laudo):
  existing_pdf = PdfReader(open(arquivo, 'rb'))
  output = PdfWriter()

  # Criar um novo PDF com o ReportLab para sobrepor o existente
  for i in range(len(existing_pdf.pages)):
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=letter)
    c.setFont('Helvetica-Bold',8)

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

Preencher_fomulario(arquivo,l,laudo)