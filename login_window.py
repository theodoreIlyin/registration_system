import tkinter as tk
from tkinter import messagebox
from pymongo.errors import PyMongoError

import auth
import database

def open_login(root, on_succes):
    win = tk.Toplevel(root)
    win.title("Вход")
    win.geometry("350x250")
    win.resizable(False,False)
    win.grab_set()

    tk.Label(win, text="Почта или телефон", font=("Arial",11)).pack(pady=(15,0))
    login_entry = tk.Entry(win, width=30)
    login_entry.pack()

    tk.Label(win, text="Пароль", font=("Arial",11)).pack(pady=(10,0))
    pass_entry = tk.Entry(win, width=30, show="*")
    pass_entry.pack()

    def submit():
        if database.users_collection is None:
            messagebox.showerror("Ошибка", "Нет подключения к базе данных", parent=win)
            return

        try:
            user = auth.authenticate(login_entry.get(), pass_entry.get())
        except PyMongoError as e:
            messagebox.showerror("Ошибка", f"Ошибка базы данных:\n{e}", parent=win)
            return

        if user is not None:
            auth.login(user)
            win.destroy()
            on_succes()
        else:
            messagebox.showerror("Ошибка", "Неверная почта/телефон или пароль", parent=win)

    tk.Button(win, text="Войти", font=("Arial", 12, "bold"), command=submit).pack(pady=20)