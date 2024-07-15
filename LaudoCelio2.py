from faster_whisper import WhisperModel
import os

#import pdfplumber
import re
import time
#from reportlab.pdfgen import canvas
#from PyPDF2 import PdfReader, PdfWriter
#from reportlab.lib.pagesizes import letter
import fitz
import io

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

decimal_words = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']


"""
function to form numeric multipliers for million, billion, thousand etc.

input: list of strings
return value: integer
"""
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


"""
function to return integer for an input `number_sentence` string
input: string
output: int or double or None
"""
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



def ajuste_palavras_campos(texto):
   texto = texto.upper()

   #ver formas pra contornar isso, não tá muito legal
   
   #texto = texto.replace(".", "")
   #texto = texto.replace(",", "")

   '''
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
   '''

   '''
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
   '''

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
                                  colposcopia, lesão, Conclusão, Conduta, Examinador, Trófico, Atrófico, Ectopia, Cistos de naboth, Ilhotas de epitélio glandular,
                                  Deciduose de Gravidez, EAB, tênue, Pontilhado, Orifícios, Leucoplasia, Condiloma, Estenose, Endometriose, exérese""")

tudo = ""
for segment in segments:
    #print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
    tudo += segment.text
tudo = ajuste_palavras_campos(tudo)

tudo2 = tudo.upper()
tudo2 = tudo2.replace(",", "")

#print(tudo)
print(tudo)

patterns = {
    #'Nome': r'NOME\s+(.*?)\s+(?=(DATA|PRONTUÁRIO|INDICAÇÃO))',
    'Nome': r'NOME+(.*?)\s+(?=(DATA|PRONTUÁRIO|INDICAÇÃO))',
    #'Prontuário': r'PRONTUÁRIO\s+(.*?)\s+(?=(DATA|INDICAÇÃO))',
    'Prontuário': r'PRONTUÁRIO+(.*?)\s+(?=(DATA|INDICAÇÃO))',
    #'Data': r'DATA\s+(.*?)\s+INDICAÇÃO',
    'Data': r'DATA+(.*?)\s+INDICAÇÃO',
    #'Indicação do Exame': r'INDICAÇÃO DO EXAME\s+(.*?)\s+(?=(VULVOSCOPIA|EXAME ESPECULAR|COLPOSCOPIA))',
    'Indicação do Exame': r'INDICAÇÃO DO EXAME+(.*?)\s+(?=(VULVOSCOPIA|EXAME ESPECULAR|COLPOSCOPIA))',
    #'Vulvoscopia': r'VULVOSCOPIA\s+(.*?)\s+(?=(EXAME ESPECULAR|COLPOSCOPIA))',
    'Vulvoscopia': r'VULVOSCOPIA+(.*?)\s+(?=(EXAME ESPECULAR|COLPOSCOPIA))',
    #'Exame especular': r'EXAME ESPECULAR\s+(.*?)\s+(?=(COLPOSCOPIA|AVALIAÇÃO|LOCALIZAÇÃO|CONCLUSÃO))',
    'Exame especular': r'EXAME ESPECULAR+(.*?)\s+(?=(COLPOSCOPIA|AVALIAÇÃO|LOCALIZAÇÃO|CONCLUSÃO))',
    #'Localização da lesão': r'LOCALIZAÇÃO DA LESÃO\s+(.*?)\s+(?=(GRAU|SUSPEITA|VASOS|SINAIS|CONCLUSÃO))',
    'Localização da lesão': r'LOCALIZAÇÃO DA LESÃO+(.*?)\s+(?=(GRAU|SUSPEITA|VASOS|SINAIS|CONCLUSÃO))',
    #'Conclusão': r'CONCLUSÃO\s+(.*?)\s+(?=(CONDUTA|EXAMINADOR|EXAMINADORA))',
    'Conclusão': r'CONCLUSÃO+(.*?)\s+(?=(CONDUTA|EXAMINADOR|EXAMINADORA))',
    #'Conduta': r'CONDUTA\s+(.*?)\s+(?=(EXAMINADOR|EXAMINADORA))',
    'Conduta': r'CONDUTA+(.*?)\s+(?=(EXAMINADOR|EXAMINADORA))',
    #'Examinador': r'EXAMINADOR\s+(.*)'
    'Examinador': r'EXAMINADOR+(.*)'
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
        '''
        if campo == 'Data':
           #print("lobinho")
           gambiarra = match.group(1).strip()
           gambiarra = substituir_mes_por_numero(gambiarra).split()
           dados[campo] = gambiarra[0] + '        ' + gambiarra[2] + '      ' + gambiarra[4]
           #print(gambiarra[0] + ' ' + gambiarra[2] + ' ' + gambiarra[4])
        else:
           dados[campo] = match.group(1).strip()
        '''

    else:
        dados[campo] = ""
print(dados)
for campo, valor in dados.items():
    print("oi")
    gambiarra = valor.lstrip(", .")
    gambiarra = gambiarra.rstrip(", .")

    if campo == 'Data':
       gambiarra = substituir_mes_por_numero(gambiarra).split(" DE ")
       print(gambiarra)

       dados[campo] = str(word_to_num(gambiarra[0])) + '          ' + gambiarra[1] + '      ' + str(word_to_num(gambiarra[2]))
    else:
       dados[campo] = gambiarra
    #print(f"{campo}: {valor}")
print(dados)
'''
dic_text = {'Conclusão':'AA', 'Nome':'paulo', 'Data':['16','07','2024'], 'Satisfatória':True,'Tipo 2':True,'Iodo positivo':True,'Prontuário':'dsddfg',
'Exame especular':'kdhfskehu','Localização da lesão':'dkjgrdgl','Vasos atípicos':True}
'''
#arquivo = 'Laudo4.pdf'

# Função para adicionar "X" no início de um retângulo, agora trocado por conteúdo
def adicionar_x(pdf_page, inicio, conteudo, dx, dy):
    # Define as coordenadas para desenhar o "X"
    x, y = inicio  # Ponto de início do retângulo
    tamanho = 10  # Tamanho do marcador "X"

    # Adiciona o "X" como texto na página
    pdf_page.insert_text((x-dx, y-dy), conteudo, fontsize=10, fontname="helv", color=(1, 0, 0))


# Abre o documento PDF
doc = fitz.open("Laudo4.pdf")

# Termos que você deseja procurar
tupla2 = ("Satisfatória", "Insatisfatória", "Completamente visível", "parcialmente visível", "não visível", "Tipo 1", "Tipo 2", "Tipo 3", "Trófico", "Atrófico", 
          "Ectopia", "Cistos de naboth", "Orifícios glandulares abertos", "Ilhotas de epitélio glandular", "Deciduose de Gravidez", "EAB tênue", "mosaico fino", 
          "Pontilhado fino", "EAB denso", "mosaico grosseiro", "Pontilhado grosseiro", "Orifícios glandulares espessados", "Leucoplasia", "Erosão", "Iodo positivo", 
          "Iodo Negativo", "Vasos atípicos", "Fragilidades dos vasos", "Lesão exotípica", "Superfície irregular", "necrose", "Ulceração", "Tumor", "Condiloma", 
          "Pólipo", "Estenose", "Endometriose", "Zona de transformação congênita", "Sequela pós-tratamento", "Inflamação", "Anomalia congênita")
writeright = ("Nome", "Data", "Prontuário", "Indicação do Exame", "Localização da lesão")
writebelow = ("Vulvoscopia", "Exame especular", "Conclusão", "Conduta", "Examinador") #padrão3, são palavras isoladas que precisa preencher "no ar", aí é foda, não tem padrão


# Percorre todas as páginas do documento
for page_num in range(len(doc)):
    page = doc.load_page(page_num)

    # Procura cada termo na página atual
    for termo in tupla2:
        resultados = page.search_for(termo)
        while len(resultados) > 1:
          resultados.pop()
        # Percorre os resultados encontrados para o termo
        for resultado in resultados:
            # Obtém o ponto de início do retângulo
            ponto_inicio = resultado[:2]
            #if termo.upper() in tudo.split():
            if " "+termo.upper()+" " in tudo2:
               adicionar_x(page, ponto_inicio, "X", 13, -8)
    # Procura cada termo na página atual
    for termo in writeright:
        resultados = page.search_for(termo)
        while len(resultados) > 1:
          resultados.pop()
        # Percorre os resultados encontrados para o termo
        for resultado in resultados:
            # Obtém o ponto de *fim* do retângulo
            ponto_inicio = resultado[2:]
            adicionar_x(page, ponto_inicio, dados[termo], -5, 2)
    for termo in writebelow:
        resultados = page.search_for(termo)
        while len(resultados) > 1:
          resultados.pop()
        # Percorre os resultados encontrados para o termo
        for resultado in resultados:
            # Obtém o ponto de início do retângulo
            ponto_inicio = resultado[:2]
            adicionar_x(page, ponto_inicio, dados[termo], 0, -23)

# Salva o documento modificado com as infos marcadas
doc.save("Laudo_preenchido.pdf")

# Fecha o documento após a conclusão do processamento
doc.close()

exit()
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