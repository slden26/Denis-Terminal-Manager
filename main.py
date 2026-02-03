import customtkinter as ctk
import subprocess
import json
import os
import sys
from tkinter import messagebox

# --- ПУТИ (ПОРТАТИВНАЯ СТРУКТУРА) ---
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

WT_PATH = os.path.join(BASE_DIR, "terminal", "wt.exe")
SSH_PATH = os.path.join(BASE_DIR, "ssh", "ssh.exe")
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
ICON_PATH = os.path.join(BASE_DIR, "icon.ico")
CALC_PATH = os.path.join(BASE_DIR, "calc", "calc1.exe")
NP_PATH = os.path.join(BASE_DIR, "notepad++", "notepad++.exe") # Убедись, что папка называется 'notepad'

# --- ФУНКЦИИ ЛОГИКИ ---
def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return []
    return []

def save_config(data):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def launch(target, ctype):
    if not os.path.exists(WT_PATH):
        messagebox.showerror("Ошибка", f"Не найден terminal/wt.exe в:\n{BASE_DIR}")
        return

    if ctype == "SSH":
        if not target:
            # Если поле пустое, просто открываем новую вкладку терминала
            cmd = f'"{WT_PATH}" -w 0 new-tab --title "Terminal" cmd.exe'
        else:
            if not os.path.exists(SSH_PATH):
                messagebox.showerror("Ошибка", f"Не найден ssh/ssh.exe в:\n{BASE_DIR}")
                return
            cmd = f'"{WT_PATH}" -w 0 new-tab --title "{target}" "{SSH_PATH}" {target}'
    elif ctype == "PowerShell":
        cmd = f'"{WT_PATH}" -w 0 new-tab --title "PS" powershell.exe'
    else:
        cmd = f'"{WT_PATH}" -w 0 new-tab --title "CMD" cmd.exe'

    try:
        subprocess.Popen(cmd, shell=True)
    except Exception as e:
        messagebox.showerror("Ошибка запуска", str(e))

# --- ИНТЕРФЕЙС ---
ctk.set_appearance_mode("dark")
app = ctk.CTk()
app.title("Denis Terminal Manager")

# Функция центрирования
def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")

# Вызываем центрирование (вместо обычной строки app.geometry)
center_window(app, 500, 450)
app.resizable(False, False) # Запрет изменения размера

# Установка иконки окна
if os.path.exists(ICON_PATH):
    try:
        app.iconbitmap(ICON_PATH)
    except: pass

# Фиксированный размер и запрет на изменение
app.geometry("500x450")
app.resizable(False, False)

# Установка иконки окна
if os.path.exists(ICON_PATH):
    try:
        app.iconbitmap(ICON_PATH)
    except: pass

bookmarks = load_config()

# --- ОБНОВЛЕННЫЕ ФУНКЦИИ ЗАПУСКА ---
def open_calc():
    if os.path.exists(CALC_PATH):
        subprocess.Popen(CALC_PATH)
    else:
        messagebox.showerror("Ошибка", f"Не найден калькулятор в:\n{CALC_PATH}")

def open_notepad():
    if os.path.exists(NP_PATH):
        subprocess.Popen(NP_PATH)
    else:
        messagebox.showerror("Ошибка", f"Не найден Notepad++ в:\n{NP_PATH}")

# Панель быстрых кнопок
fast_f = ctk.CTkFrame(app, fg_color="transparent")
fast_f.pack(pady=10, padx=20, fill="x")
ctk.CTkButton(fast_f, text="CMD", width=80, command=lambda: launch("", "CMD")).pack(side="left", padx=2, expand=True)
ctk.CTkButton(fast_f, text="PowerShell", width=80, command=lambda: launch("", "PowerShell")).pack(side="left", padx=2, expand=True)
ctk.CTkButton(fast_f, text="Calc", width=80, fg_color="#555555", command=open_calc).pack(side="left", padx=2, expand=True)
ctk.CTkButton(fast_f, text="Notepad++", width=80, fg_color="#555555", command=open_notepad).pack(side="left", padx=2, expand=True)
# Кнопку Quick SSH лучше ставить в конец, так как ей нужен ip_entry
ctk.CTkButton(fast_f, text="Quick SSH", width=100, fg_color="#27ae60", command=lambda: launch(ip_entry.get().strip(), "SSH")).pack(side="left", padx=2, expand=True)

# Блок добавления SSH закладок
in_f = ctk.CTkFrame(app)
in_f.pack(pady=5, padx=20, fill="x")
name_entry = ctk.CTkEntry(in_f, placeholder_text="Название (напр. Роутер)", width=210)
name_entry.grid(row=0, column=0, padx=10, pady=10)
ip_entry = ctk.CTkEntry(in_f, placeholder_text="Адрес / IP", width=210)
ip_entry.grid(row=0, column=1, padx=10, pady=10)

def add_bookmark():
    name, addr = name_entry.get().strip(), ip_entry.get().strip()
    if name and addr:
        bookmarks.append({"name": name, "address": addr, "type": "SSH"})
        save_config(bookmarks); render_bookmarks()
        name_entry.delete(0, 'end'); ip_entry.delete(0, 'end')

ctk.CTkButton(in_f, text="Сохранить закладку", command=add_bookmark).grid(row=1, column=0, columnspan=2, pady=(0, 5), sticky="ew", padx=5)

# Список закладок с прокруткой
scroll_frame = ctk.CTkScrollableFrame(app, label_text="Закладки")
scroll_frame.pack(pady=10, padx=20, fill="both", expand=True)

def render_bookmarks():
    for w in scroll_frame.winfo_children(): w.destroy()
    for i, bm in enumerate(bookmarks):
        f = ctk.CTkFrame(scroll_frame)
        f.pack(pady=2, fill="x")
        
        # Кнопка запуска
        btn_text = f"{bm['name']} ({bm['type']})"
        ctk.CTkButton(f, text=btn_text, anchor="w", height=30,
                      command=lambda b=bm: launch(b["address"], b["type"])).pack(side="left", padx=5, pady=2, fill="x", expand=True)
        
        # Кнопка удаления
        ctk.CTkButton(f, text="X", width=30, height=30, fg_color="#a11d1d", hover_color="#7a1515",
                      command=lambda idx=i: (bookmarks.pop(idx), save_config(bookmarks), render_bookmarks())).pack(side="right", padx=5)

render_bookmarks()
app.mainloop()