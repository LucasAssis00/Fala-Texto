import fitz  # PyMuPDF
import whisper
import sounddevice as sd
import numpy as np
import wavio
import time
import librosa
import re
import tkinter as tk 
from tkinter import StringVar
import threading
from tkinter import filedialog
import os
import platform
from PIL import Image, ImageTk

# variaveis globais
model = whisper.load_model("small")
limiar = 0.05


def determine_channels():
    devices = sd.query_devices()
    l = []
    for i, device in enumerate(devices):
        if 'microfone' in device['name'].lower():
            l.append(device['max_input_channels'])
            
    if 1 in l:
        x = 1
    else:
        x = 2
    print(x)
    return x
canal = determine_channels()

def calculate_snr_speech(audio_path):
    # Carregar o arquivo de áudio
    y, sr = librosa.load(audio_path, sr=None)
    
    # Detectar silêncios para estimar o ruído
    intervals = librosa.effects.split(y, top_db=20)
    
    # Calcular a potência do sinal (somente partes faladas)
    signal_power = np.mean([np.mean(np.square(y[start:end])) for start, end in intervals])
    
    # Verificar se há intervalos de ruído detectados
    if len(intervals) > 1:
        noise_intervals = np.concatenate([y[i:j] for i, j in zip(intervals[:-1, 1], intervals[1:, 0])])
        noise_power = np.mean(np.square(noise_intervals))
    else:
        # Caso não haja intervalos de ruído suficientes, usar um valor padrão pequeno para evitar divisão por zero
        noise_power = np.mean(np.square(y[-int(sr*0.1):]))  # Usando os últimos 10% do áudio como ruído
    
    # Calcular o SNR
    snr = 10 * np.log10(signal_power / noise_power)
    return snr

def analyze_audio(audio_path):
    y, sr = librosa.load(audio_path, sr=None)
    
    # Calcular a amplitude RMS
    rms = np.mean(librosa.feature.rms(y=y))
    
    # Calcular a frequência fundamental usando o autocorrelação
    pitches, magnitudes = librosa.core.piptrack(y=y, sr=sr)
    pitch = np.mean(pitches[pitches > 0])  # Média das frequências detectadas
    
    # Calcular o espectro de frequências
    spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
    
    return rms, pitch, spectral_centroid


def listar_campos_pdf(pdf_path):
    pdf_document = fitz.open(pdf_path)
    dados = {}
    for page_num in range(pdf_document.page_count):
        page = pdf_document.load_page(page_num)
        print(f"\nPágina {page_num + 1}:\n")
        annotations = page.widgets()
        if annotations:
            for annot in annotations:
                dados[(annot.field_name, annot.field_type)] = None
                print(f"Campo: {annot.field_name}, Tipo: {annot.field_type}, Valor: {annot.field_value}")
        else:
            print("Nenhum campo preenchível encontrado nesta página.")
    return dados


def preencher_campos_pdf(pdf_path, output_path, data):
    pdf_document = fitz.open(pdf_path)
    for page_num in range(pdf_document.page_count):
        page = pdf_document.load_page(page_num)
        annotations = page.widgets()
        if annotations:
            for annot in annotations:
                field_name = annot.field_name
                for campo in data.keys():
                    if field_name == campo[0]:
                        annot.field_value = data[campo]
                        annot.update()
    
    pdf_document.save(output_path)
    print(f"PDF salvo em {output_path}")


def reconhecer_comando():
    global limiar
    global canal
    fs = 44100  # Taxa de amostragem
    seconds = 8 # Duração da gravação
    if canal == 2:
            amplitude = 0.01
            sinal = 12
    else:
            amplitude = 0.005
            sinal = 12
            
    d = time.time()
    print("Diga algo:")
    label_var2.set('Diga algo:')

    recording = sd.rec(int(seconds * fs), samplerate=fs, channels=canal)
    sd.wait()  # Espera até que a gravação esteja finalizada
    print(limiar)
    print(np.max(np.abs(recording)))

    if np.max(np.abs(recording)) > limiar:
        wavio.write("comando.wav", recording, fs, sampwidth=2)
        snr_value = calculate_snr_speech("comando.wav")
        rms, pitch, spectral_centroid = analyze_audio("comando.wav")
        print(snr_value,rms,pitch,spectral_centroid)

        if snr_value > sinal and pitch > 100 and rms > amplitude and spectral_centroid > 1800:
            print(f"A qualidade do áudio é: boa (SNR: {snr_value:.2f} dB)")
            print(f"O tipo de fala é: Normal")
            result = model.transcribe("comando.wav",fp16=False) # configuração sem gpu 
            comando = result["text"]
            with open('registro-fala.txt', 'a',encoding='utf-8') as arquivo: 
                arquivo.write(comando + '\n')
        else:
            comando = ' '

    else: 
        comando = 'Não entendi o que você falou, fale novamente !'
    print(comando)
    print(f'tempo {time.time() - d}')
    
    return comando

def atualizar_dados_com_fala(dados):
    while True:
        
        canvas.itemconfig(circulo, fill="green")
        root.update_idletasks()
        comando = reconhecer_comando()
        label_var.set(comando)

        
        if 'preencher' in comando.lower():
            canvas.itemconfig(circulo, fill="gray")
            listbox.delete(0, tk.END)
            root.update_idletasks()
            label_var2.set(' ')
            label_var.set(' ')
            break
        for campo in dados.keys():
            if campo[0].lower() in comando.lower():
                if campo[1] == 7:  # Tipo texto
                    valor = comando.lower().split(campo[0])[-1].strip()
                    if bool(re.search(r'[^\w\s]', valor[0])): # verifica se tem pontuação no inicio da string
                        valor = valor[1:].strip()
                    dados[campo] = valor
                    print(f"Atualizando {campo} com valor: {valor}")
                elif campo[1] == 5:  
                    dados[campo] = 1
                    print(f"Marcando rádio: {campo}")
                elif campo[1] == 2:  
                    dados[campo] = True
                    print(f"Selecionando checkbox: {campo}")
        label_var2.set(' ')
        time.sleep(0.15)
    return dados

def exibir_dicionario(dados):
    
    # Adicione os itens do dicionário na Listbox
    for chave, valor in dados.items():
        listbox.insert(tk.END, f"{chave[0]}")
    
    # Ajusta a largura com base no item mais longo 
    max_width = max([len(item) for item in listbox.get(0, tk.END)]) 
    listbox.config(width=max_width)

def iniciar_atualizacao_dados(caminho_arquivo):
    botao1['state'] = tk.DISABLED
    dados = listar_campos_pdf(caminho_arquivo)
    exibir_dicionario(dados)
    dados_atualizados = atualizar_dados_com_fala(dados)
    if platform.system() == "Windows":
        # No Windows, geralmente os downloads estão no caminho do usuário
        download_path = os.path.join(os.environ["USERPROFILE"], "Downloads")
    else:
        # No Unix (Linux e macOS), geralmente os downloads estão no diretório do usuário
        download_path = os.path.join(os.environ["HOME"], "Downloads") 
    preencher_campos_pdf(caminho_arquivo, download_path+r'\teste.pdf', dados_atualizados)
    tk.messagebox.showwarning("Aviso", "Documento preenchido !!")
    botao1['state'] = tk.NORMAL


def thread_atualizacao_dados(valor): 
    thread = threading.Thread(target=iniciar_atualizacao_dados,args=(valor,)) 
    thread.start()

def abrir_pdf():
    caminho_arquivo = filedialog.askopenfilename(
        title="Selecione um arquivo PDF",
        filetypes=[("Arquivos PDF", "*.pdf")]
    )
    if caminho_arquivo:
        root.after(300, lambda: thread_atualizacao_dados(caminho_arquivo))   


def habilitar_calibra():
    global limiar
    global canal
    tk.messagebox.showwarning("Aviso", "Calibração em andamento, não fale pelos próximos 8 segundos !!!")
    fs = 44100  # Taxa de amostragem
    seconds = 8  # Duração da gravação
    recording = sd.rec(int(seconds * fs), samplerate=fs, channels=canal)
    sd.wait()  
    limiar = np.max(np.abs(recording))
    
    tk.messagebox.showwarning("Aviso", "Calibração realizada com sucesso !!!")
    bt_abrir['state'] = tk.NORMAL

def thread_calibra(): 
    thread = threading.Thread(target=habilitar_calibra) 
    thread.start()


root = tk.Tk() 
root.title("Preenchimento de PDF's")
root.configure(bg="#083f76")
root.geometry('750x450') 
label_var = StringVar()
label_var.set(" ")
label_var2 = StringVar()

# Carregar a imagem usando PIL
if platform.system() == "Windows":
        # No Windows, geralmente os downloads estão no caminho do usuário
        download_path = os.path.join(os.environ["USERPROFILE"], "Downloads")
else:
        # No Unix (Linux e macOS), geralmente os downloads estão no diretório do usuário
        download_path = os.path.join(os.environ["HOME"], "Downloads") 
imagem = Image.open(download_path+r"\Projeto (4).png")
imagem_tk = ImageTk.PhotoImage(imagem)
label_imagem = tk.Label(root, image=imagem_tk,borderwidth=0, highlightthickness=0)
label_imagem.place(x=0, y=0)

# lista de campos
texto_campos = tk.Label(root, text='Nome dos campos', font=("Helvetica", 14),bg="#083f76",fg="white", borderwidth=0, highlightthickness=0) 
texto_campos.pack(pady=5) 
listbox = tk.Listbox(root)
listbox.pack(expand=False)

canvas = tk.Canvas(root, width=100, height=100,bg="#083f76", borderwidth=0, highlightthickness=0) 
canvas.pack(pady=5) 
circulo = canvas.create_oval(25, 25, 75, 75, fill="gray")
label2 = tk.Label(root, textvariable=label_var2, font=("Helvetica", 14),bg="#083f76",fg="white", borderwidth=0, highlightthickness=0) 
label2.pack(pady=0) 
label = tk.Label(root, textvariable=label_var, font=("Helvetica", 14),bg="#083f76",fg="white", borderwidth=0, highlightthickness=0) 
label.pack(pady=5) 

# botoes
botao1 = tk.Button(root, text="Calibrar o microfone", command=thread_calibra)
botao1.pack(pady=10)
bt_abrir = tk.Button(root, text="Importar PDF", command=abrir_pdf,state=tk.DISABLED)
bt_abrir.pack() 

root.mainloop()

