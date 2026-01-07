import customtkinter as ctk
from tkinter import filedialog
import yt_dlp
import threading
import os
import re

class BLoadApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Локализация ---
        self.lang_data = {
            "English": {
                "header": "BLOAD",
                "subtitle": "Universal Media Downloader",
                "url_label": "PASTE VIDEO LINK",
                "paste": "Clipboard",
                "analyze": "ANALYZE",
                "quality_wait": "Waiting for link...",
                "save_to": "SAVE TO:",
                "download": "DOWNLOAD NOW",
                "status_ready": "Ready",
                "status_error": "Error!",
                "status_analyzing": "Analyzing...",
                "status_success": "Ready to download",
                "status_finish": "DONE!",
                "placeholder": "Paste link here..."
            },
            "Русский": {
                "header": "BLOAD",
                "subtitle": "Универсальный загрузчик",
                "url_label": "ВСТАВЬТЕ ССЫЛКУ",
                "paste": "Буфер",
                "analyze": "АНАЛИЗ",
                "quality_wait": "Ожидание ссылки...",
                "save_to": "СОХРАНИТЬ В:",
                "download": "СКАЧАТЬ",
                "status_ready": "Готов",
                "status_error": "Ошибка!",
                "status_analyzing": "Анализ...",
                "status_success": "Готово к загрузке",
                "status_finish": "ЗАВЕРШЕНО!",
                "placeholder": "Вставьте ссылку сюда..."
            },
            "Українська": {
                "header": "BLOAD",
                "subtitle": "Універсальний завантажувач",
                "url_label": "ВСТАВТЕ ПОСИЛАННЯ",
                "paste": "Буфер",
                "analyze": "АНАЛІЗ",
                "quality_wait": "Очікування посилання...",
                "save_to": "ЗБЕРЕГТИ В:",
                "download": "ЗАВАНТАЖИТИ",
                "status_ready": "Готово",
                "status_error": "Помилка!",
                "status_analyzing": "Аналіз...",
                "status_success": "Готово до завантаження",
                "status_finish": "ЗАВЕРШЕНО!",
                "placeholder": "Вставте посилання сюди..."
            }
        }
        self.current_lang = "English"

        # --- Настройки окна ---
        self.title("BLoad v2.2")
        self.geometry("700x800")
        self.minsize(600, 750)
        
        self.ffmpeg_path = os.path.join(os.getcwd(), "ffmpeg")
        self.formats_dict = {}

        # Сетка главного окна
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.setup_ui()
        self.update_ui_text()

    def setup_ui(self):
        # Переключатель языка
        self.lang_menu = ctk.CTkOptionMenu(
            self, values=list(self.lang_data.keys()), 
            command=self.change_language, width=100
        )
        self.lang_menu.set(self.current_lang)
        self.lang_menu.place(relx=0.98, rely=0.02, anchor="ne")

        # Header
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, pady=(40, 10), sticky="nsew")
        self.header_frame.grid_columnconfigure(0, weight=1)

        self.header_label = ctk.CTkLabel(self.header_frame, text="BLOAD", font=("Impact", 48), text_color="#3B8ED0")
        self.header_label.grid(row=0, column=0)
        self.subtitle = ctk.CTkLabel(self.header_frame, text="", font=("Arial", 14, "italic"), text_color="gray")
        self.subtitle.grid(row=1, column=0)

        # Content Card
        self.main_frame = ctk.CTkFrame(self, fg_color="#212121", corner_radius=20)
        self.main_frame.grid(row=1, column=0, padx=40, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.url_label = ctk.CTkLabel(self.main_frame, text="", font=("Arial", 12, "bold"))
        self.url_label.grid(row=0, column=0, pady=(20, 5))

        # Поле ввода с универсальными хоткеями
        self.url_entry = ctk.CTkEntry(self.main_frame, height=45, border_color="#3B8ED0", corner_radius=10)
        self.url_entry.grid(row=1, column=0, padx=30, sticky="ew")
        
        # Биндим универсальный обработчик клавиш (keycode 86=V, 65=A)
        self.url_entry.bind("<Key>", self.handle_universal_hotkeys)

        # Buttons
        self.btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.btn_frame.grid(row=2, column=0, pady=15)

        self.paste_btn = ctk.CTkButton(self.btn_frame, text="", width=120, height=35, fg_color="#333333", command=self.handle_paste)
        self.paste_btn.pack(side="left", padx=10)

        self.analyze_button = ctk.CTkButton(self.btn_frame, text="", width=180, height=35, font=("Arial", 13, "bold"), command=self.start_analysis)
        self.analyze_button.pack(side="left", padx=10)

        self.video_title_label = ctk.CTkLabel(self.main_frame, text="", font=("Arial", 14, "bold"), wraplength=500)
        self.video_title_label.grid(row=3, column=0, pady=10, padx=20)

        self.quality_var = ctk.StringVar()
        self.quality_menu = ctk.CTkOptionMenu(self.main_frame, variable=self.quality_var, values=[], height=40, state="disabled")
        self.quality_menu.grid(row=4, column=0, pady=10, padx=50, sticky="ew")

        # Path Selection
        self.path_container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.path_container.grid(row=5, column=0, pady=15, padx=30, sticky="ew")
        self.path_container.grid_columnconfigure(0, weight=1)
        
        self.save_path = ctk.StringVar(value=os.path.join(os.path.expanduser("~"), "Downloads"))
        self.path_entry = ctk.CTkEntry(self.path_container, textvariable=self.save_path, height=35)
        self.path_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        self.browse_btn = ctk.CTkButton(self.path_container, text="...", width=40, height=35, command=self.browse_folder)
        self.browse_btn.grid(row=0, column=1)

        # Progress
        self.progress_bar = ctk.CTkProgressBar(self.main_frame, height=12)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=6, column=0, pady=(20, 0), padx=30, sticky="ew")
        self.progress_label = ctk.CTkLabel(self.main_frame, text="", font=("Arial", 11))
        self.progress_label.grid(row=7, column=0, pady=(5, 10))

        # Download Button
        self.download_button = ctk.CTkButton(self.main_frame, text="", state="disabled", fg_color="#27ae60", font=("Arial", 20, "bold"), height=60, corner_radius=15, command=self.download_video)
        self.download_button.grid(row=8, column=0, pady=(20, 30), padx=50, sticky="ew")

        self.status_label = ctk.CTkLabel(self, text="", font=("Arial", 12))
        self.status_label.grid(row=2, column=0, pady=10)

    # --- ЛОГИКА ГОРЯЧИХ КЛАВИШ (Универсальная) ---
    def handle_universal_hotkeys(self, event):
        # Проверяем зажат ли Control (state & 4)
        if event.state & 4:
            if event.keycode == 86: # Клавиша V
                self.handle_paste()
                return "break"
            elif event.keycode == 65: # Клавиша A
                self.url_entry.select_range(0, 'end')
                self.url_entry.icursor('end')
                return "break"

    def handle_paste(self):
        try:
            clipboard = self.clipboard_get()
            self.url_entry.delete(0, 'end')
            self.url_entry.insert(0, clipboard)
        except:
            pass
        return "break"

    # --- СМЕНА ЯЗЫКА ---
    def change_language(self, new_lang):
        self.current_lang = new_lang
        self.update_ui_text()

    def update_ui_text(self):
        l = self.lang_data[self.current_lang]
        self.subtitle.configure(text=l["subtitle"])
        self.url_label.configure(text=l["url_label"])
        self.url_entry.configure(placeholder_text=l["placeholder"])
        self.paste_btn.configure(text=l["paste"])
        self.analyze_button.configure(text=l["analyze"])
        self.download_button.configure(text=l["download"])
        self.status_label.configure(text=l["status_ready"])
        if not self.formats_dict:
            self.quality_var.set(l["quality_wait"])

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder: self.save_path.set(folder)

    def start_analysis(self):
        url = self.url_entry.get()
        if not url: return
        self.update_status(self.lang_data[self.current_lang]["status_analyzing"], "white")
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start()
        threading.Thread(target=self.get_formats, args=(url,), daemon=True).start()

    def get_formats(self, url):
        try:
            ydl_opts = {
                'quiet': True, 
                'no_warnings': True,
                'cookiefile': 'cookies.txt',  # Используем куки
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'referer': url, # Сообщаем сайту, откуда мы пришли
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'Video')
                formats = info.get('formats', [])
                
                unique_res = {}
                for f in formats:
                    res = f.get('height')
                    if res and res >= 360:
                        label = f"{res}p ({f.get('ext')})"
                        if res not in unique_res:
                            unique_res[res] = {'label': label, 'id': f"bestvideo[height={res}]+bestaudio/best"}
                
                sorted_keys = sorted(unique_res.keys(), reverse=True)
                options = ["Best Quality / Авто"]
                self.formats_dict = {"Best Quality / Авто": "bestvideo+bestaudio/best"}
                
                for k in sorted_keys:
                    options.append(unique_res[k]['label'])
                    self.formats_dict[unique_res[k]['label']] = unique_res[k]['id']
                
                self.after(0, lambda: self.show_ui_after_analysis(options, title))
        except:
            self.after(0, lambda: self.update_status(self.lang_data[self.current_lang]["status_error"], "#e74c3c"))

    def show_ui_after_analysis(self, options, title):
        self.progress_bar.stop()
        self.progress_bar.configure(mode="determinate")
        self.video_title_label.configure(text=title[:100] + "..." if len(title)>100 else title)
        self.quality_menu.configure(values=options, state="normal")
        self.quality_var.set(options[0])
        self.download_button.configure(state="normal")
        self.update_status(self.lang_data[self.current_lang]["status_success"], "#27ae60")

    def download_video(self):
        url = self.url_entry.get()
        folder = self.save_path.get()
        format_id = self.formats_dict.get(self.quality_var.get())
        self.download_button.configure(state="disabled")

        def run_dl():
            try:
                opts = {
                    'format': format_id,
                    'outtmpl': f'{folder}/%(title)s [%(height)sp].%(ext)s',
                    'ffmpeg_location': self.ffmpeg_path,
                    'merge_output_format': 'mp4',
                    'progress_hooks': [self.progress_hook],
                    'overwrites': True,
                    # Добавляем обход защиты:
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                    'referer': url,
                }
                with yt_dlp.YoutubeDL(opts) as ydl:
                    ydl.download([url])
                self.after(0, lambda: self.update_status(self.lang_data[self.current_lang]["status_finish"], "#27ae60"))
            except Exception as e:
                print(f"Error: {e}")
                self.after(0, lambda: self.update_status(self.lang_data[self.current_lang]["status_error"], "#e74c3c"))
            finally:
                self.after(0, lambda: self.download_button.configure(state="normal"))

        threading.Thread(target=run_dl, daemon=True).start()

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            p = re.sub(r'\x1b\[[0-9;]*[mK]', '', d.get('_percent_str', '0%'))
            s = re.sub(r'\x1b\[[0-9;]*[mK]', '', d.get('_speed_str', 'N/A'))
            try:
                val = float(p.replace('%', '').strip()) / 100
                self.after(0, lambda: self.progress_bar.set(val))
                self.after(0, lambda: self.progress_label.configure(text=f"{p} | {s}"))
            except: pass

    def update_status(self, text, color="white"):
        self.status_label.configure(text=text, text_color=color)

if __name__ == "__main__":
    app = BLoadApp()
    app.mainloop()