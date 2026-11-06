import tkinter as tk
from tkinter import filedialog, messagebox, font

class SpeedReaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RSVP Speed Reader")
        self.root.geometry("800x550")
        self.root.minsize(550, 420)

        self.words = []
        self.current_index = 0
        self.is_running = False
        self.timer_id = None

        self.bpm_var = tk.IntVar(value=250)
        self.font_family_var = tk.StringVar(value="Courier New")
        self.font_size_var = tk.IntVar(value=38)
        self.theme_var = tk.StringVar(value="dark")

        self.themes = {
            "dark": {
                "bg": "#000000",
                "fg": "#FFFFFF",
                "panel": "#0A0A0A",
                "border": "#333333",
                "active_bg": "#222222",
                "active_fg": "#FFFFFF"
            },
            "light": {
                "bg": "#FFFFFF",
                "fg": "#000000",
                "panel": "#F4F4F4",
                "border": "#CCCCCC",
                "active_bg": "#E0E0E0",
                "active_fg": "#000000"
            }
        }

        self._create_menu()
        self._create_widgets()
        self._apply_theme()
        self._load_default_text()

    def _create_menu(self):
        self.menubar = tk.Menu(self.root)

        file_menu = tk.Menu(self.menubar, tearoff=0)
        file_menu.add_command(label="Открыть TXT...", command=self.load_from_file)
        file_menu.add_command(label="Редактор текста", command=self.open_text_input_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)
        self.menubar.add_cascade(label="Файл", menu=file_menu)

        view_menu = tk.Menu(self.menubar, tearoff=0)
        view_menu.add_radiobutton(
            label="Тёмная тема (Ч/Б)", variable=self.theme_var, value="dark", command=self._apply_theme
        )
        view_menu.add_radiobutton(
            label="Светлая тема (Б/Ч)", variable=self.theme_var, value="light", command=self._apply_theme
        )
        view_menu.add_separator()

        size_menu = tk.Menu(view_menu, tearoff=0)
        size_menu.add_command(label="Компактное (600x450)", command=lambda: self.set_window_size(600, 450))
        size_menu.add_command(label="Стандартное (800x550)", command=lambda: self.set_window_size(800, 550))
        size_menu.add_command(label="Широкое (1024x700)", command=lambda: self.set_window_size(1024, 700))
        size_menu.add_command(label="Задать вручную...", command=self.open_custom_size_dialog)
        view_menu.add_cascade(label="Размер окна", menu=size_menu)
        self.menubar.add_cascade(label="Вид", menu=view_menu)

        help_menu = tk.Menu(self.menubar, tearoff=0)
        help_menu.add_command(label="О программе", command=self.show_about)
        self.menubar.add_cascade(label="Справка", menu=help_menu)

        self.root.config(menu=self.menubar)

    def _create_widgets(self):
        self.display_frame = tk.Frame(self.root)
        self.display_frame.pack(expand=True, fill=tk.BOTH, padx=25, pady=25)

        self.word_label = tk.Label(
            self.display_frame,
            text="ГОТОВ",
            anchor="center",
            justify="center"
        )
        self.word_label.pack(expand=True, fill=tk.BOTH)

        self.progress_label = tk.Label(
            self.display_frame,
            text="0 / 0",
            font=("Consolas", 10)
        )
        self.progress_label.pack(side=tk.BOTTOM, pady=5)

        self.control_frame = tk.Frame(self.root, bd=1, relief=tk.SOLID)
        self.control_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=25, pady=(0, 25))

        btn_row = tk.Frame(self.control_frame)
        btn_row.pack(fill=tk.X, padx=12, pady=10)

        self.btn_start = tk.Button(btn_row, text="▶ СТАРТ", width=12, command=self.toggle_reading, relief=tk.FLAT, bd=1)
        self.btn_start.pack(side=tk.LEFT, padx=4)

        self.btn_reset = tk.Button(btn_row, text="⟲ СБРОС", width=10, command=self.reset_reading, relief=tk.FLAT, bd=1)
        self.btn_reset.pack(side=tk.LEFT, padx=4)

        self.btn_paste = tk.Button(btn_row, text="✎ ВСТАВИТЬ ТЕКСТ", command=self.open_text_input_dialog, relief=tk.FLAT, bd=1)
        self.btn_paste.pack(side=tk.RIGHT, padx=4)

        self.btn_file = tk.Button(btn_row, text="📂 ФАЙЛ", width=10, command=self.load_from_file, relief=tk.FLAT, bd=1)
        self.btn_file.pack(side=tk.RIGHT, padx=4)

        settings_row = tk.Frame(self.control_frame)
        settings_row.pack(fill=tk.X, padx=12, pady=(0, 12))

        self.lbl_bpm = tk.Label(settings_row, text="Темп (BPM):", font=("Consolas", 10))
        self.lbl_bpm.pack(side=tk.LEFT, padx=(4, 2))

        self.bpm_scale = tk.Scale(
            settings_row, from_=60, to=1000, orient=tk.HORIZONTAL,
            variable=self.bpm_var, showvalue=True, length=160, bd=0, highlightthickness=0
        )
        self.bpm_scale.pack(side=tk.LEFT, padx=6)

        self.lbl_font = tk.Label(settings_row, text="Шрифт:", font=("Consolas", 10))
        self.lbl_font.pack(side=tk.LEFT, padx=(14, 2))

        available_fonts = ["Courier New", "Consolas", "Arial", "Times New Roman", "Verdana", "Georgia"]
        self.font_menu = tk.OptionMenu(settings_row, self.font_family_var, *available_fonts, command=self._update_font)
        self.font_menu.config(relief=tk.FLAT, bd=1, highlightthickness=0)
        self.font_menu.pack(side=tk.LEFT, padx=4)

        self.lbl_size = tk.Label(settings_row, text="Размер:", font=("Consolas", 10))
        self.lbl_size.pack(side=tk.LEFT, padx=(14, 2))

        self.size_spin = tk.Spinbox(
            settings_row, from_=16, to=96, textvariable=self.font_size_var,
            width=4, command=self._update_font, relief=tk.FLAT, bd=1
        )
        self.size_spin.bind("<Return>", lambda e: self._update_font())
        self.size_spin.pack(side=tk.LEFT, padx=4)

        self._update_font()

    def _update_font(self, *args):
        try:
            size = int(self.font_size_var.get())
            if size < 10 or size > 150:
                raise ValueError("Размер шрифта вне допустимого диапазона.")
            family = self.font_family_var.get()
            self.word_label.config(font=(family, size, "bold"))
        except (ValueError, tk.TclError):
            self.font_size_var.set(38)
            self.word_label.config(font=(self.font_family_var.get(), 38, "bold"))

    def _apply_theme(self):
        try:
            t = self.themes[self.theme_var.get()]
            self.root.config(bg=t["bg"])
            self.display_frame.config(bg=t["bg"])
            self.word_label.config(bg=t["bg"], fg=t["fg"])
            self.progress_label.config(bg=t["bg"], fg=t["fg"])

            self.control_frame.config(bg=t["panel"], highlightbackground=t["border"], highlightcolor=t["border"])
            for child in self.control_frame.winfo_children():
                child.config(bg=t["panel"])
                for widget in child.winfo_children():
                    w_type = widget.winfo_class()
                    if w_type in ("Button", "Menubutton"):
                        widget.config(
                            bg=t["bg"], fg=t["fg"],
                            activebackground=t["active_bg"], activeforeground=t["active_fg"],
                            highlightbackground=t["border"]
                        )
                    elif w_type == "Label":
                        widget.config(bg=t["panel"], fg=t["fg"])
                    elif w_type == "Scale":
                        widget.config(bg=t["panel"], fg=t["fg"], troughcolor=t["bg"], activebackground=t["active_bg"])
                    elif w_type == "Spinbox":
                        widget.config(bg=t["bg"], fg=t["fg"], buttonbackground=t["panel"], insertbackground=t["fg"])

            self.font_menu["menu"].config(bg=t["bg"], fg=t["fg"], activebackground=t["active_bg"], activeforeground=t["active_fg"])
        except Exception as e:
            messagebox.showerror("Ошибка темы", f"Не удалось применить цветовую схему:\n{e}")

    def _load_default_text(self):
        sample = (
            "Скорочтение методом быстрой последовательной визуальной презентации "
            "позволяет подавить внутреннюю артикуляцию и устранить движения глаз по строке. "
            "Слова выводятся в одну фиксированную точку с заданным ритмом BPM. "
            "Загрузите собственный текстовый файл или вставьте текст через встроенный редактор."
        )
        self._process_text(sample)

    def _process_text(self, raw_text):
        try:
            if not raw_text or not raw_text.strip():
                raise ValueError("Текст пуст. Введите или загрузите хотя бы одно слово.")
            self.pause_reading()
            self.words = raw_text.split()
            self.current_index = 0
            self._update_display()
        except ValueError as ve:
            messagebox.showwarning("Пустой текст", str(ve))
        except Exception as e:
            messagebox.showerror("Ошибка обработки", f"Непредвиденная ошибка при разборе текста:\n{e}")

    def _update_display(self):
        total = len(self.words)
        if total == 0:
            self.word_label.config(text="НЕТ ТЕКСТА")
            self.progress_label.config(text="0 / 0")
            return

        if self.current_index < total:
            self.word_label.config(text=self.words[self.current_index])
            self.progress_label.config(text=f"{self.current_index + 1} / {total}  ({self.bpm_var.get()} BPM)")
        else:
            self.word_label.config(text="КОНЕЦ")
            self.progress_label.config(text=f"{total} / {total}")
            self.pause_reading()

    def toggle_reading(self):
        if self.is_running:
            self.pause_reading()
        else:
            self.start_reading()

    def start_reading(self):
        try:
            if not self.words:
                raise RuntimeError("Сначала загрузите или вставьте текст для чтения.")
            if self.current_index >= len(self.words):
                self.current_index = 0
            self.is_running = True
            self.btn_start.config(text="⏸ ПАУЗА")
            self._schedule_next_word()
        except Exception as e:
            messagebox.showwarning("Внимание", str(e))

    def pause_reading(self):
        self.is_running = False
        self.btn_start.config(text="▶ СТАРТ")
        if self.timer_id is not None:
            try:
                self.root.after_cancel(self.timer_id)
            except Exception:
                pass
            self.timer_id = None

    def reset_reading(self):
        self.pause_reading()
        self.current_index = 0
        self._update_display()

    def _schedule_next_word(self):
        if not self.is_running:
            return
        try:
            bpm = max(1, int(self.bpm_var.get()))
            delay_ms = int(60000 / bpm)
        except (ValueError, ZeroDivisionError, tk.TclError):
            delay_ms = 250

        self._update_display()
        if self.current_index < len(self.words):
            self.current_index += 1
            self.timer_id = self.root.after(delay_ms, self._schedule_next_word)
        else:
            self.pause_reading()

    def load_from_file(self):
        self.pause_reading()
        filepath = filedialog.askopenfilename(
            title="Выберите текстовый файл",
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
        )
        if not filepath:
            return
        try:
            content = None
            for enc in ("utf-8", "cp1251", "latin-1"):
                try:
                    with open(filepath, "r", encoding=enc) as f:
                        content = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            if content is None:
                raise IOError("Не удалось распознать кодировку файла.")
            self._process_text(content)
        except Exception as e:
            messagebox.showerror("Ошибка чтения файла", f"Не удалось загрузить файл:\n{e}")

    def open_text_input_dialog(self):
        self.pause_reading()
        t = self.themes[self.theme_var.get()]

        dialog = tk.Toplevel(self.root)
        dialog.title("Загрузка текста")
        dialog.geometry("520x380")
        dialog.config(bg=t["bg"])
        dialog.transient(self.root)
        dialog.grab_set()

        lbl = tk.Label(dialog, text="Вставьте или введите текст ниже:", bg=t["bg"], fg=t["fg"], font=("Consolas", 10))
        lbl.pack(anchor="w", padx=15, pady=(15, 5))

        text_area = tk.Text(
            dialog, wrap=tk.WORD, bg=t["panel"], fg=t["fg"],
            insertbackground=t["fg"], font=("Consolas", 11), relief=tk.SOLID, bd=1
        )
        text_area.pack(expand=True, fill=tk.BOTH, padx=15, pady=5)
        if self.words:
            text_area.insert("1.0", " ".join(self.words))

        def apply_input():
            raw = text_area.get("1.0", tk.END)
            self._process_text(raw)
            dialog.destroy()

        btn_apply = tk.Button(
            dialog, text="ПРИМЕНИТЬ", command=apply_input,
            bg=t["bg"], fg=t["fg"], activebackground=t["active_bg"], activeforeground=t["active_fg"],
            relief=tk.SOLID, bd=1, width=15
        )
        btn_apply.pack(pady=12)

    def set_window_size(self, width, height):
        try:
            w, h = int(width), int(height)
            if w < 550 or h < 420:
                raise ValueError("Минимально допустимый размер окна: 550x420 пикселей.")
            self.root.geometry(f"{w}x{h}")
        except Exception as e:
            messagebox.showerror("Ошибка размера окна", str(e))

    def open_custom_size_dialog(self):
        t = self.themes[self.theme_var.get()]
        dialog = tk.Toplevel(self.root)
        dialog.title("Размер окна")
        dialog.geometry("280x160")
        dialog.resizable(False, False)
        dialog.config(bg=t["bg"])
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text="Ширина (px):", bg=t["bg"], fg=t["fg"]).grid(row=0, column=0, padx=15, pady=12, sticky="e")
        w_entry = tk.Entry(dialog, width=10, bg=t["panel"], fg=t["fg"], insertbackground=t["fg"])
        w_entry.insert(0, str(self.root.winfo_width()))
        w_entry.grid(row=0, column=1, padx=10, pady=12)

        tk.Label(dialog, text="Высота (px):", bg=t["bg"], fg=t["fg"]).grid(row=1, column=0, padx=15, pady=5, sticky="e")
        h_entry = tk.Entry(dialog, width=10, bg=t["panel"], fg=t["fg"], insertbackground=t["fg"])
        h_entry.insert(0, str(self.root.winfo_height()))
        h_entry.grid(row=1, column=1, padx=10, pady=5)

        def apply_custom_size():
            try:
                w = int(w_entry.get().strip())
                h = int(h_entry.get().strip())
                self.set_window_size(w, h)
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Ошибка ввода", "Введите целые числа для ширины и высоты.", parent=dialog)

        btn = tk.Button(
            dialog, text="ОК", width=10, command=apply_custom_size,
            bg=t["bg"], fg=t["fg"], relief=tk.SOLID, bd=1
        )
        btn.grid(row=2, column=0, columnspan=2, pady=15)

    def show_about(self):
        messagebox.showinfo(
            "О программе",
            "RSVP Speed Reader\n\n"
            "Тренажер скорочтения с установкой темпа в BPM.\n"
            "Поддерживает загрузку TXT, прямой ввод текста,\n"
            "выбор шрифта и монохромные темы оформления."
        )

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = SpeedReaderApp(root)
        root.mainloop()
    except Exception as fatal_err:
        messagebox.showerror("Критическая ошибка", f"Сбой запуска приложения:\n{fatal_err}")