'''
import pyaudio
import wave
import os
import threading
import tkinter as tk
from tkinter import messagebox

class AudioRecorderThread(threading.Thread):
    def __init__(self, filename, indicator_label):
        super(AudioRecorderThread, self).__init__()
        self.filename = filename
        self.indicator_label = indicator_label
        self.stop_event = threading.Event()

    def run(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=44100,
                        input=True,
                        frames_per_buffer=1024)

        frames = []

        while not self.stop_event.is_set():
            data = stream.read(1024)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(self.filename, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(44100)
        wf.writeframes(b''.join(frames))
        wf.close()

    def stop_recording(self):
        self.stop_event.set()
i = 1
#
recorder = False
#
def start_recording():
    global recorder
    global filename
    global i
    if recorder:
        messagebox.showinfo("Informativo", "Já havia gravação em andamento.")
    else:
        while os.path.exists(f'output{i}.wav' ):
            i += 1
        filename = f'output{i}.wav'
        indicator_label.config(text="Recording: ON", bg="red")  # Change indicator appearance
        recorder = AudioRecorderThread(filename, indicator_label)
        recorder.start()

def stop_recording():
    global recorder
    global filename
    if recorder:
        recorder.stop_recording()
        recorder.join()
        indicator_label.config(text="Recording: OFF", bg="green")  # Change indicator appearance
        messagebox.showinfo("Informativo", f'Áudio salvo como "{filename}".')
        #tk.messagebox.showinfo("Information", "Textinho")
        recorder = False
    else:
        messagebox.showinfo("Informativo", "Não havia gravação em andamento.")



root = tk.Tk()
root.title("Audio Recorder")
root.geometry("300x150")

start_button = tk.Button(root, text="Start Recording", command=start_recording)
stop_button = tk.Button(root, text="Stop Recording", command=stop_recording)

indicator_label = tk.Label(root, text="Recording: OFF", bg="green")

start_button.pack()
stop_button.pack()
indicator_label.pack()

root.mainloop()
'''











'''
import os
import pyaudio
import wave
import threading
import tkinter as tk
from tkinter import simpledialog, messagebox

class AudioRecorderThread(threading.Thread):
    def __init__(self, filename, indicator_label):
        super(AudioRecorderThread, self).__init__()
        self.filename = filename
        self.indicator_label = indicator_label
        self.stop_event = threading.Event()

    def run(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=44100,
                        input=True,
                        frames_per_buffer=1024)

        frames = []

        while not self.stop_event.is_set():
            data = stream.read(1024)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(self.filename, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(44100)
        wf.writeframes(b''.join(frames))
        wf.close()

    def stop_recording(self):
        self.stop_event.set()

recorder = None
filename = None

def start_recording():
    global recorder
    global filename
    if recorder:
        messagebox.showinfo("Informativo", "Já havia gravação em andamento.")
    else:
        filename = simpledialog.askstring("Save As", "Enter the filename (without extension):")
        if filename:
            filename = filename + ".wav"
            if os.path.exists(filename):
                messagebox.showerror("Erro", f'O arquivo "{filename}" já existe.')
            else:
                indicator_label.config(text="Recording: ON", bg="red")  # Change indicator appearance
                recorder = AudioRecorderThread(filename, indicator_label)
                recorder.start()
        else:
            messagebox.showinfo("Informativo", "Gravação cancelada.")

def stop_recording():
    global recorder
    global filename
    if recorder:
        recorder.stop_recording()
        recorder.join()
        indicator_label.config(text="Recording: OFF", bg="green")  # Change indicator appearance
        #messagebox.showinfo("Informativo", f'Áudio salvo como "{filename}".')
        recorder = None
    else:
        messagebox.showinfo("Informativo", "Não havia gravação em andamento.")

root = tk.Tk()
root.title("Audio Recorder")
root.geometry("300x150")

start_button = tk.Button(root, text="Start Recording", command=start_recording)
stop_button = tk.Button(root, text="Stop Recording", command=stop_recording)

indicator_label = tk.Label(root, text="Recording: OFF", bg="green")

start_button.pack()
stop_button.pack()
indicator_label.pack()

root.mainloop()
'''

import os
import pyaudio
import wave
import threading
import tkinter as tk
from tkinter import simpledialog, messagebox

class AudioRecorderThread(threading.Thread):
    def __init__(self, filename, indicator_label):
        super(AudioRecorderThread, self).__init__()
        self.filename = filename
        self.indicator_label = indicator_label
        self.frames = []
        self.stop_event = threading.Event()

    def run(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=44100,
                        input=True,
                        frames_per_buffer=1024)

        while not self.stop_event.is_set():
            data = stream.read(1024)
            self.frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

    def save_recording(self, new_filename):
        wf = wave.open(new_filename, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
        wf.setframerate(44100)
        wf.writeframes(b''.join(self.frames))
        wf.close()

    def stop_recording(self):
        self.stop_event.set()

recorder = None

def start_recording():
    global recorder
    if recorder:
        messagebox.showinfo("Informativo", "Já havia gravação em andamento.")
    else:
        indicator_label.config(text="Gravação: ON", bg="red")  # Change indicator appearance
        recorder = AudioRecorderThread(None, indicator_label)
        recorder.start()

def stop_recording():
    global recorder
    if recorder:
        recorder.stop_recording()
        recorder.join()
        indicator_label.config(text="Gravação: OFF", bg="green")  # Change indicator appearance

        # Prompt the user for a filename after recording
        new_filename = simpledialog.askstring("Salvar como", "Digite o nome do arquivo (sem a extensão):")
        if new_filename:
            new_filename = new_filename + ".wav"
            if os.path.exists(new_filename):
                messagebox.showerror("Erro", f'O arquivo "{new_filename}" já existe.')
            else:
                recorder.save_recording(new_filename)
                messagebox.showinfo("Informativo", f'Áudio salvo como "{new_filename}".')
        else:
            messagebox.showinfo("Informativo", "Gravação descartada.")

        recorder = None
    else:
        messagebox.showinfo("Informativo", "Não havia gravação em andamento.")

root = tk.Tk()
root.title("Audio Recorder")
root.geometry("300x150")

start_button = tk.Button(root, text="Começar Gravação", command=start_recording)
stop_button = tk.Button(root, text="Parar Gravação", command=stop_recording)

indicator_label = tk.Label(root, text="Gravação: OFF", bg="green")

start_button.pack()
stop_button.pack()
indicator_label.pack()

root.mainloop()

