# main_transcription_input.py
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from android.permissions import request_permissions, Permission
from jnius import autoclass
import os
import requests
import threading

class AudioTranscriptionApp(App):
    def build(self):
        Window.clearcolor = (0.95, 0.95, 0.95, 1)

        self.access_token = None
        self.cert_file = self.ensure_cert_file('certificado', 'ca_cert.pem')

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.text_input = TextInput(hint_text='Sua transcrição aparecerá aqui...',
                                     multiline=True, font_size=18)
        layout.add_widget(self.text_input)

        self.transcribe_btn = Button(text='Gravar e Transcrever', size_hint=(1, 0.2),
                                     background_color=(0.2, 0.6, 0.9, 1))
        self.transcribe_btn.bind(on_press=self.thread_transcribe_audio)
        layout.add_widget(self.transcribe_btn)

        request_permissions([Permission.RECORD_AUDIO, Permission.WRITE_EXTERNAL_STORAGE])
        self.login()

        return layout

    def ensure_cert_file(self, dir_name, file_name):
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), dir_name)
        os.makedirs(path, exist_ok=True)
        return os.path.join(path, file_name)

    def login(self):
        url = "https://processarpdffalatex.zapto.org/login"
        payload = {'username': 'Fala-texto', 'password': 'Transcrição_de_fala_em_texto_api'}
        response = requests.post(url, json=payload, verify=self.cert_file)
        if response.status_code == 200:
            self.access_token = response.json().get('access_token')

    def thread_transcribe_audio(self, instance):
        threading.Thread(target=self.transcribe_audio, daemon=True).start()

    def transcribe_audio(self):
        MediaRecorder = autoclass('android.media.MediaRecorder')
        AudioSource = autoclass('android.media.MediaRecorder$AudioSource')
        OutputFormat = autoclass('android.media.MediaRecorder$OutputFormat')
        AudioEncoder = autoclass('android.media.MediaRecorder$AudioEncoder')
        Environment = autoclass('android.os.Environment')

        recorder = MediaRecorder()
        recorder.setAudioSource(AudioSource.MIC)
        recorder.setOutputFormat(OutputFormat.MPEG_4)
        recorder.setAudioEncoder(AudioEncoder.AAC)
        recorder.setAudioSamplingRate(44100)

        audio_file_path = os.path.join(
            Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS).getAbsolutePath(),
            "audio_transcription.mp4")
        recorder.setOutputFile(audio_file_path)
        recorder.prepare()
        recorder.start()

        threading.Event().wait(7)
        recorder.stop()
        recorder.release()

        with open(audio_file_path, 'rb') as f:
            files = {'file': f.read()}

        headers = {'Authorization': f'Bearer {self.access_token}'}
        url = "https://processarpdffalatex.zapto.org/transcricao"
        response = requests.post(url, files=files, headers=headers, verify=self.cert_file)

        if response.status_code == 200:
            result = response.json()
            if 'text' in result:
                self.text_input.text = result['text']

if __name__ == '__main__':
    AudioTranscriptionApp().run()
