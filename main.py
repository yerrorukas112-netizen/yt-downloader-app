from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.utils import platform
import threading
import os

Window.clearcolor = (0.059, 0.090, 0.161, 1)


class YTDownloaderApp(App):

    def build(self):
        self.title = "YT Downloader Pro"
        self.is_downloading = False

        root = BoxLayout(orientation='vertical', padding=20, spacing=12)

        title = Label(
            text="[b]YT Downloader Pro[/b]",
            markup=True,
            font_size=28,
            size_hint_y=None,
            height=50,
            color=(0.39, 0.40, 0.95, 1)
        )
        root.add_widget(title)

        subtitle = Label(
            text="Descarga videos y audio de YouTube",
            font_size=14,
            size_hint_y=None,
            height=30,
            color=(0.58, 0.64, 0.72, 1)
        )
        root.add_widget(subtitle)

        url_label = Label(
            text="URL del video:",
            font_size=14,
            size_hint_y=None,
            height=30,
            halign='left',
            color=(0.95, 0.96, 0.98, 1)
        )
        url_label.bind(size=url_label.setter('text_size'))
        root.add_widget(url_label)

        self.url_input = TextInput(
            hint_text="https://www.youtube.com/watch?v=...",
            multiline=False,
            size_hint_y=None,
            height=50,
            font_size=14,
            background_color=(0.15, 0.20, 0.34, 1),
            foreground_color=(1, 1, 1, 1),
            hint_text_color=(0.4, 0.4, 0.5, 1),
            cursor_color=(0.39, 0.40, 0.95, 1),
            padding=[12, 12]
        )
        root.add_widget(self.url_input)

        type_label = Label(
            text="Tipo de descarga:",
            font_size=14,
            size_hint_y=None,
            height=30,
            halign='left',
            color=(0.95, 0.96, 0.98, 1)
        )
        type_label.bind(size=type_label.setter('text_size'))
        root.add_widget(type_label)

        self.type_spinner = Spinner(
            text='Video MP4 (720p)',
            values=[
                'Video MP4 (1080p)',
                'Video MP4 (720p)',
                'Video MP4 (480p)',
                'Video MP4 (360p)',
                'Audio M4A (mejor)',
                'Audio M4A (128kbps)',
            ],
            size_hint_y=None,
            height=50,
            font_size=14,
            background_color=(0.15, 0.20, 0.34, 1),
            color=(1, 1, 1, 1)
        )
        root.add_widget(self.type_spinner)

        self.progress = ProgressBar(
            max=100,
            value=0,
            size_hint_y=None,
            height=25
        )
        root.add_widget(self.progress)

        self.status_label = Label(
            text="Listo para descargar",
            font_size=13,
            size_hint_y=None,
            height=40,
            color=(0.58, 0.64, 0.72, 1),
            halign='center'
        )
        self.status_label.bind(size=self.status_label.setter('text_size'))
        root.add_widget(self.status_label)

        btn_layout = BoxLayout(size_hint_y=None, height=60, spacing=10)

        self.download_btn = Button(
            text="DESCARGAR",
            font_size=16,
            bold=True,
            background_color=(0.06, 0.73, 0.51, 1),
            color=(1, 1, 1, 1)
        )
        self.download_btn.bind(on_press=self.start_download)
        btn_layout.add_widget(self.download_btn)

        self.cancel_btn = Button(
            text="CANCELAR",
            font_size=16,
            bold=True,
            background_color=(0.94, 0.27, 0.27, 1),
            color=(1, 1, 1, 1),
            disabled=True
        )
        self.cancel_btn.bind(on_press=self.cancel_download)
        btn_layout.add_widget(self.cancel_btn)

        root.add_widget(btn_layout)

        info = Label(
            text="Los archivos se guardan en la carpeta Download",
            font_size=11,
            size_hint_y=None,
            height=30,
            color=(0.39, 0.45, 0.55, 1)
        )
        root.add_widget(info)

        self.cancel_flag = False
        return root

    def get_download_dir(self):
        if platform == 'android':
            paths = [
                '/storage/emulated/0/Download',
                '/sdcard/Download',
                os.path.join(os.path.expanduser('~'), 'Download'),
            ]
            for p in paths:
                if os.path.exists(p):
                    return p
            os.makedirs(paths[0], exist_ok=True)
            return paths[0]
        return os.path.join(os.path.expanduser('~'), 'Downloads')

    def get_ydl_opts(self):
        selected = self.type_spinner.text
        download_dir = self.get_download_dir()
        outtmpl = os.path.join(download_dir, '%(title)s.%(ext)s')

        opts = {
            'outtmpl': outtmpl,
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
            'progress_hooks': [self.on_progress],
        }

        if '1080p' in selected:
            opts['format'] = 'bestvideo[height<=1080]+bestaudio/best[height<=1080]/best'
            opts['merge_output_format'] = 'mp4'
        elif '720p' in selected:
            opts['format'] = 'bestvideo[height<=720]+bestaudio/best[height<=720]/best'
            opts['merge_output_format'] = 'mp4'
        elif '480p' in selected:
            opts['format'] = 'bestvideo[height<=480]+bestaudio/best[height<=480]/best'
            opts['merge_output_format'] = 'mp4'
        elif '360p' in selected:
            opts['format'] = 'bestvideo[height<=360]+bestaudio/best[height<=360]/best'
            opts['merge_output_format'] = 'mp4'
        elif 'mejor' in selected:
            opts['format'] = 'bestaudio/best'
        elif '128' in selected:
            opts['format'] = 'bestaudio[abr<=128]/bestaudio/best'

        return opts

    def start_download(self, instance):
        url = self.url_input.text.strip()
        if not url:
            self.set_status("Ingresa una URL primero", (0.94, 0.27, 0.27, 1))
            return

        if 'youtube.com' not in url and 'youtu.be' not in url:
            self.set_status("URL no valida de YouTube", (0.94, 0.27, 0.27, 1))
            return

        if self.is_downloading:
            return

        self.is_downloading = True
        self.cancel_flag = False
        self.download_btn.disabled = True
        self.cancel_btn.disabled = False
        self.progress.value = 0
        self.set_status("Iniciando descarga...", (0.96, 0.62, 0.04, 1))

        threading.Thread(target=self.download_worker, args=(url,), daemon=True).start()

    def download_worker(self, url):
        try:
            import yt_dlp
            opts = self.get_ydl_opts()

            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])

            if not self.cancel_flag:
                Clock.schedule_once(lambda dt: self.on_complete())

        except Exception as e:
            err = str(e)[:100]
            Clock.schedule_once(lambda dt: self.on_error(err))

    def on_progress(self, d):
        if self.cancel_flag:
            raise Exception("Cancelado por el usuario")

        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
            downloaded = d.get('downloaded_bytes', 0)
            speed = d.get('speed') or 0

            if total > 0:
                pct = int((downloaded / total) * 100)
                speed_mb = speed / (1024 * 1024) if speed else 0
                msg = f"Descargando... {pct}% ({speed_mb:.1f} MB/s)"
                Clock.schedule_once(lambda dt, p=pct, m=msg: self.update_progress(p, m))

        elif d['status'] == 'finished':
            Clock.schedule_once(lambda dt: self.set_status(
                "Procesando archivo...", (0.96, 0.62, 0.04, 1)))

    def update_progress(self, pct, msg):
        self.progress.value = pct
        self.set_status(msg, (0.58, 0.64, 0.72, 1))

    def on_complete(self):
        self.progress.value = 100
        self.set_status("Descarga completada!", (0.06, 0.73, 0.51, 1))
        self.download_btn.disabled = False
        self.cancel_btn.disabled = True
        self.is_downloading = False

        popup = Popup(
            title='Completado',
            content=Label(text='El archivo se guardo en\nla carpeta Download',
                         font_size=16, halign='center'),
            size_hint=(0.8, 0.3)
        )
        popup.open()

    def on_error(self, err):
        self.set_status(f"Error: {err}", (0.94, 0.27, 0.27, 1))
        self.download_btn.disabled = False
        self.cancel_btn.disabled = True
        self.is_downloading = False

    def cancel_download(self, instance):
        self.cancel_flag = True
        self.set_status("Cancelando...", (0.96, 0.62, 0.04, 1))

    def set_status(self, text, color):
        self.status_label.text = text
        self.status_label.color = color


if __name__ == '__main__':
    YTDownloaderApp().run()
