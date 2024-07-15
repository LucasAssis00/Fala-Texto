from time import sleep
import subprocess
from thefuzz import fuzz, process
from unidecode import unidecode
import os

import pandas as pd

df = pd.read_csv('tabela_consulta_Z1.csv', sep=',')


import whisper
model = whisper.load_model("small")


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


def edit_text_in_terminal(text):
    # Save the text to a temporary file
    with open("temp_text.txt", "w") as temp_file:
        temp_file.write(text)
    
    # Open the text editor (nano) for editing
    subprocess.run(["nano", "temp_text.txt"])
    
    # Read the edited text
    with open("temp_text.txt", "r") as temp_file:
        edited_text = temp_file.read()
    
    # Remove the temporary file
    os.remove("temp_text.txt")

    print("( ͡° ͜ʖ ͡°)")
    print(edited_text)
    
    return edited_text


def save_variables(Quantidade, Custo, Procedimento, Somatudo):
    file = open("resumo.csv", "w")


    Somatudo = repr(Somatudo)

    file.write("Quantidade\tCusto\tProcedimento\n")

    for i in range(len(Quantidade)):
        Quantidade[i] = repr(Quantidade[i])
        Custo[i] = repr(Custo[i])
        Procedimento[i] = repr(Procedimento[i])
        file.write(Quantidade[i] + "\t" + Custo[i] + "\t" + Procedimento[i] + "\n")
    
    file.write("Custo(s) Total(is):\tR$" + Somatudo)
    file.close




def transcricao(arquivo):
	result = model.transcribe(arquivo, language = 'Portuguese')
	texto = result["text"].upper()
	return texto

#texto = result["text"].replace(",", "")
#texto = texto.replace(".", "")
#texto = texto.upper()


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
#print(indexed_list)
i = input('Escolha o(s) indice(s) do(s) arquivo(s) de áudio que você deseja: \nEx: 0 ou 0-4\n')
#print(wav_files[int(i)])
i = i.split("-")
if(len(i)>1):
    #print(f'{i[0]}~{i[1]}')
    i = range(int(i[0]), int(i[1])+1)

print('a')

print()
print()


quantidade = []
transcricoesProced = []

for j in i:
    #print(j)
    text5 = unidecode(transcricao(wav_files[int(j)]))
    
    x = text5.split()
    print(x)
    beginning_phrase = []
    remaining_phrase = []
    #i = 0
    valor = 0
    excluir = 0


    for word in x:
        if word == 'e':
            # Ignora a palavra 'e' e continua para a próxima
            continue
        try:
            # Tenta converter a palavra em um número
            number = word_to_num(word)
            # Se for um número, adiciona ao valor total
            valor += number
            excluir += 1
        except ValueError:
            # Se não for um número, interrompe a iteração
            break


    beginning_phrase.append(" ".join(x[:excluir]))
    remaining_phrase.append(" ".join(x[excluir:]))


    for item in beginning_phrase:
        if item == '':
            print('até aqui blz...')
            x = " ".join(x)
            input(f'Ocorreu um erro referente ao item "{x}", reescreva-o corretamente:\n(Pressione "Enter" para continuar)')
            correcao = edit_text_in_terminal(x)
            correcao = correcao.split()
            print(f"após correção: {x}")

            i = 0
            valor = 0
            excluir = 0

            while i < len(correcao):
                #
                current_word = correcao[i]
                next_word = ""

                if i < len(correcao) - 1:
                    next_word = correcao[i + 1]

                i += 1

                try:
                    if correcao[i-1] == 'e':
                        pass
                    elif word_to_num(current_word):
                        valor += word_to_num(current_word)
                        print(valor)
                    excluir+=1
                except ValueError:
                    break
            beginning_ajuste = " ".join(correcao[:excluir])
            remaining_ajuste = " ".join(correcao[excluir:])
            print('~')
            print(f"palavras pra separar: {excluir}")
            print(f"parte numérica pós ajuste: {beginning_ajuste}")
            print(f"parte procedimento pós ajuste: {remaining_ajuste}")
            beginning_phrase = beginning_ajuste
            remaining_phrase = remaining_ajuste
            print(';)')

    print(f"beggining - {beginning_phrase}")
    print(f"remaining - {remaining_phrase}")

    if(isinstance(beginning_phrase, str)):
        print("V")
        pass
    else:
        print("F")
        beginning_phrase = " ".join(beginning_phrase)

    teste = word_to_num(beginning_phrase)
    print(teste)
    quantidade.append(teste)
    transcricoesProced.append(remaining_phrase)
    

print(quantidade)

print(f"Verificação parte final: {transcricoesProced}")



procedimento = []
codigo = []


a=0
#esse "a" é pra acessar a posição no array transcricoesProced, pra procurar no csv cada valor do a-ésimo procedimento
for item in transcricoesProced:
  possibilidades = process.extract("".join(item), df.loc[:,'Descricao'], scorer=fuzz.ratio, limit = 3)
  print("miaau")
  print(f"O {a+1}º procedimento citado corresponde à:\n")
  for j in range (3):
      print(f"{j}.\t{possibilidades[j][0]}")
  print("3.\tReescrever procedimento")
  ajuste = input()

  if ajuste == '0' or ajuste == '1' or ajuste == '2':
      procedimento.append(possibilidades[int(ajuste)][0])
      codigo.append(df.loc[df.Descricao == procedimento[a], 'Classificacao'].item())

  elif ajuste == "3":
      gambiarra = "".join(transcricoesProced[a])
      troca = edit_text_in_terminal(gambiarra)
      procedimento.append(process.extractOne(troca, df.loc[:,'Descricao'], scorer=fuzz.ratio)[0])
      codigo.append(df.loc[df.Descricao == procedimento[a], 'Classificacao'].item())

  a += 1
sleep(1)


print(f"Verificação procedimentos: {procedimento}")


print()
print(quantidade)
print()
print(procedimento)
print()
print(codigo)
print()
print()

listagem = dict()



for i in range(len(quantidade)):
    print(quantidade[i], '\t', codigo[i], '\t\t', procedimento[i])
    #listagem[procedimento[i]] = codigo[i]
    listagem[codigo[i]] = str(quantidade[i])
somatudo=0
print()
#save_variables(quantidade, custo, procedimento, somatudo)
print("---------------------------------------------")
print()
print(listagem)

##################################################################################################################################
##################################################################################################################################
##################################################################################################################################

import pdfplumber
import re
import time
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
import io


campos_ucpia = {'PACIENTE':'FULANO DE TAL','AIH':'2x2','PROCEDIMENTO REGULADO':'sem reação','ADM':'5x5', 'MUDANÇA DE PROCEDIMENTO':'sem reação',
'PRONTUARIO':'sem reação','ALTA':'1x2','ESPEC. LEITO':'sem reação','APRESENTAÇÃO':'sem reação','DATA NASCIMENTO':'15/02/2000','TIPO ALTA':'sem reação',
'CID 1º':'hcd','CID OBITO':'1'}

arquivo = "FATURA.pdf"

def Encontrar_campos_codigo(arquivo,campos_ucpia):

  campo = []
  padrao =  r"\d{2}\.\d{2}\.\d{2}\.\d{3}-\d{1}"
  padrao2 = r"\d{6}$"
  padrao3 = r"\d{2}\.\d{2}\.\d{3}\.\d{2}-\d{1}"

  with pdfplumber.open(arquivo) as leitor:
    for i in range(len(leitor.pages)):
      page = leitor.pages[i]
      palavra = page.extract_words()
      for j in palavra:
        if re.match(padrao, j['text']) or re.match(padrao2, j['text']) or re.match(padrao3, j['text']):
          campo.append(j['text'])


  ini = campo.index('03.01.01.001-7')
  auxiliar = []
  for k in campo[ini+1:]:
    auxiliar.append(k)


  conjuto = set(campo)
#  '''
  for i in conjuto:
    if i == '03.01.01.004-8':
      campos_ucpia[i] = ''
    elif i == '03.01.01.001-7':
      campos_ucpia[i] = ('','','','')
    elif i in auxiliar:
      campos_ucpia[i] = ''
    else:
      campos_ucpia[i] = ('','')
#  '''

  for x, y in listagem.items():
    if x == '03.01.01.004-8':
      campos_ucpia[x] = ''
    elif x == '03.01.01.001-7':
      #print("ok...")
      campos_ucpia[x] = (y,y,y,y)
    elif x in auxiliar:
      campos_ucpia[x] = y
      #print("ok1")
    else:
      campos_ucpia[x] = (y,y)
      #print("ok2")
  
   


#  for x, y in listagem.items():
#    campos_ucpia[x] = y

  l = []
  with pdfplumber.open(arquivo) as pdf:
    for i in range(len(pdf.pages)):
      page = pdf.pages[i]
      d = {}
      for chave, valor in campos_ucpia.items():
          dados = page.search(chave,return_groups=False, return_chars=True, layout=False)
          if len(dados) != 0:
            if chave == 'DATA NASCIMENTO':
              x = dados[0]['x0']
              y = dados[0]['chars'][0]['y0']
              d[chave] = (x,y-7)
            elif re.match(padrao, chave) or re.match(padrao2, chave) or re.match(padrao3, chave):
              if chave in ('08.02.01.002-4','08.02.01.001-6','08.02.01.004-0','08.02.01.014-8','08.02.01.008-3','08.02.01.016-4','03.01.01.017-0','08.02.01.019-9'):
                x = dados[0]['x1']
                y = dados[0]['chars'][0]['y0']
                d[chave] = (x+12,y+1,x+45,y+1)

              elif chave in ('03.01.10.010-1','03.01.10.014-4','03.01.10.008-0','03.01.10.004-7','03.01.10.005-5'):
                x = dados[0]['x1']
                y = dados[0]['chars'][0]['y0']
                d[chave] = (x+27,y+1,x+80,y+1)

              elif chave in ('02.06.01.002-8','02.06.01.003-6','02.06.01.007-9','02.06.03.002-9','02.06.02.001-5','02.06.01.005-2','02.06.01.004-4','02.06.01.006-0','02.06.02.003-1',
                             '02.05.02.003-8','02.05.02.004-6','02.05.02.005-4','02.05.02.006-2','02.05.02.007-0','02.05.02.013-5','02.05.02.009-7','02.05.02.012-7','02.05.02.017-8',
                             '02.05.02.018-6','02.12.01.002-6','02.12.01.003-4','02.02.09.019-1','03.05.01.004-2','06.03.05.010-7','06.03.05.001-8','06.03.05.003-4'):
                x = dados[0]['x1']
                y = dados[0]['chars'][0]['y0']
                d[chave] = (x+18.5,y+1,x+104,y+1)

              elif chave in ('02.11.03.004-0','03.02.06.002-2','03.02.04.001-3'):
                x = dados[0]['x1']
                y = dados[0]['chars'][0]['y0']
                d[chave] = (x+22,y+1,x+129,y+1)

              elif chave == '03.01.01.001-7':
                x = dados[0]['x1']
                y = dados[0]['chars'][0]['y0']
                d[chave] = (x-120,y-8,x+70,y-8,x-120,y-18,x+70,y-18)

              elif chave in ('223810','223710','223208','251520','251510','251605','223905'):
                if chave in ('251520','251510'):
                  x = 219
                  y = 466.42
                  d[chave] = (x+14,y+1,x+122,y+1)
                else:
                  x = dados[0]['x1']
                  y = dados[0]['chars'][0]['y0']
                  d[chave] = (x+34,y+1,x+142,y+1)
              elif chave in ('02.02.01.060-0','02.02.06.029-2','02.02.01.062-7','02.02.03.020-2','02.02.01.061-9','02.02.01.044-9','02.02.02.049-5','02.02.02.003-7','02.02.09.006-0',
                             '02.02.01.063-5','02.02.05.001-7','02.02.01.064-3','02.02.01.065-1','02.02.03.076-8','02.02.03.087-3','02.02.02.048-7','02.02.01.066-0','02.02.01.067-8',
                             '02.02.06.025-0','02.02.01.069-4','02.02.03.111-0','02.02.02.015-0','02.14.01.011-2'):
                x = dados[0]['x1']
                y = dados[0]['chars'][0]['y0']
                d[chave] = (x+37,y+1)
              else:
                x = dados[0]['x1']
                y = dados[0]['chars'][0]['y0']
                d[chave] = (x+18.5,y+1,x+83,y+1)
            else:
                x = dados[0]['x1']
                y = dados[0]['chars'][0]['y0']
                d[chave] = (x+2.3,y-4)
      l.append(d)
  return campos_ucpia, l

ini = time.time()
campos_ucpia, l = Encontrar_campos_codigo(arquivo,campos_ucpia)
fim = time.time()
print(f'Tempo: {fim-ini}')



def Preencher_fomulario(pdf_path,campos_ucpia,l):
  # Carregar o PDF existente
  existing_pdf = PdfReader(open(pdf_path, 'rb'))
  output = PdfWriter()

  conta = 0
  # Criar um novo PDF com o ReportLab para sobrepor o existente
  for i in range(len(existing_pdf.pages)):
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=letter)
    c.setFont('Times-Roman',9)

    for chave, valor in campos_ucpia.items():
      if chave in l[i].keys():
        if type(valor) is str:
          c.setFillColor('blue')
          if chave == '02.02.01.029-5':
            c.drawString(l[i][chave][0],l[i][chave][1], valor)
            c.drawString(l[i][chave][0],l[i][chave][1]-9, valor)
          else:
            c.drawString(l[i][chave][0],l[i][chave][1], valor)
        else:
          c.setFillColor('blue')
          if chave in ('251520','251510') and conta == 0:
            c.drawString(l[i][chave][0],l[i][chave][1], valor[0])
            c.drawString(l[i][chave][2],l[i][chave][3], valor[1])
            conta += 1

          elif chave == '03.01.01.001-7':
            c.drawString(l[i][chave][0],l[i][chave][1], valor[0])
            c.drawString(l[i][chave][2],l[i][chave][3], valor[1])
            c.drawString(l[i][chave][4],l[i][chave][5], valor[2])
            c.drawString(l[i][chave][6],l[i][chave][7], valor[3])

          elif chave in ('223810','223710','223208','251605','223905','02.11.03.004-0','03.02.06.002-2','03.02.04.001-3',
                         '04.17.01.004-4','04.17.01.005-2','04.01.01.001-5','04.07.04.019-6','04.12.03.012-8','04.17.01.006-0',
                         '04.12.05.017-0','04.12.01.012-7'):
            c.drawString(l[i][chave][0],l[i][chave][1], valor[0])
            c.drawString(l[i][chave][2],l[i][chave][3], valor[1])

          elif chave not in ('251520','251510','03.01.01.001-7'):
            c.drawString(l[i][chave][0],l[i][chave][1], valor[0])
            c.setFillColor('red')
            c.drawString(l[i][chave][2],l[i][chave][3], valor[1])


    c.save()
    packet.seek(0)
    new_pdf = PdfReader(packet)
    page = existing_pdf.pages[i]
    page.merge_page(new_pdf.pages[0])
    output.add_page(page)


  while os.path.exists(f'pdf_editado{i}.pdf' ):
     i+=1
  filename = f'pdf_editado{i}.pdf'
  
  # Salvar o PDF resultante
  with open(filename, 'wb') as output_pdf:
     output.write(output_pdf)

  print(f"PDF editado salvo como '",filename,"'")
  '''
  # Salvar o PDF resultante
  with open('pdf_editado.pdf', 'wb') as output_pdf:
    output.write(output_pdf)

  print("PDF editado salvo como 'pdf_editado.pdf'")
  '''

Preencher_fomulario(arquivo,campos_ucpia,l)
