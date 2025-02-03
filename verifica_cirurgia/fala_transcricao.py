import whisper
import sounddevice as sd
import numpy as np
import wavio
import time
import librosa


# variaveis globais
model = whisper.load_model("medium")
limiar = 0.05
amplitude = 0.015


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



def reconhecer_comando():
    global limiar
    global canal
    global amplitude
    fs = 44100  # Taxa de amostragem
    seconds = 7 # Duração da gravação
    sinal = 12
            
    d = time.time()
    print("Diga algo:")

    recording = sd.rec(int(seconds * fs), samplerate=fs, channels=canal)
    sd.wait()  # Espera até que a gravação esteja finalizada
    print(limiar)
    print(np.max(np.abs(recording)))

   
    wavio.write("comando.wav", recording, fs, sampwidth=2)
    snr_value = calculate_snr_speech("comando.wav")
    rms, pitch, spectral_centroid = analyze_audio("comando.wav")
    print(snr_value,rms,pitch,spectral_centroid)

    if snr_value > sinal and pitch > 100 and rms >= amplitude and spectral_centroid > 1500:
           
            
            result = model.transcribe("comando.wav",fp16=False,language="pt") # configuração sem gpu 
            comando = result["text"]
            with open('registro-fala.txt', 'a',encoding='utf-8') as arquivo: 
                arquivo.write(comando + '\n')
    else:
            comando = ' '

    
    print(comando)
    print(f'tempo {time.time() - d}')
    
    return comando

def atualizar_dados_com_fala():
    while True:
               
        comando = reconhecer_comando()

        if 'preencher' in comando.lower():
            
            break
        


def habilitar_calibra():
    global limiar
    global canal
    global amplitude
    fs = 44100  # Taxa de amostragem
    seconds = 7  # Duração da gravação
    print('Fale: calibrando o microfone')
    recording2 = sd.rec(int(seconds * fs), samplerate=fs, channels=canal)
    sd.wait()
    print('fim da calibralção')  
    limiar = np.max(np.abs(recording2))
    wavio.write("comando2.wav", recording2, fs, sampwidth=2)
    rms2, pitch, spectral_centroid = analyze_audio("comando2.wav")
    print(rms2)
    if rms2 > 0.02:
        amplitude = 0.02
    else:
        amplitude = rms2
    

habilitar_calibra()
atualizar_dados_com_fala()
