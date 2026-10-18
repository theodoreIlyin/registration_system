import tkinter as tk
from tkinter import messagebox
from pymongo.errors import PyMongoError, DuplicateKeyError

import auth
import database


def open_register(root):
    win = tk.Toplevel(root)
    win.title("Регистрация")
    win.geometry("350x380")
    win.resizable(False, False)
    win.grab_set()

    fields = {}
    for label, key, secret in [
        ("Имя", "name", False),
        ("Почта", "email", False),
        ("Телефон (+380...)", "phone", False),
        ("Пароль", "password", True),
        ("Повторите пароль", "password2", True),
    ]:
        tk.Label(win, text=label, font=("Arial", 11)).pack(pady=(8, 0))
        entry = tk.Entry(win, width=30, show="*" if secret else "")
        entry.pack()
        fields[key] = entry

    def submit():
        name = fields["name"].get().strip()
        email = fields['email'].get().strip().lower()
        phone = auth.normalize_phone(fields['phone'].get())
        password = fields["password"].get()
        password2 = fields["password2"].get()

        error = auth.validate_registration(name, email, phone, password, password2)
        if error:
            messagebox.showwarning("Ошибка", error, parent=win)
            return
        if database.users_collection is None:
            messagebox.showerror("Ошибка", "Нет подключения к базе данных", parent=win)
            return

        try:
            auth.register_user(name, email, phone, password)
        except DuplicateKeyError:
            messagebox.showerror("Ошибка", "Такая почта или телефон уже зарегистрированы", parent=win)
            return
        except PyMongoError as e:
            messagebox.showerror("Ошибка", f"Ошибка базы данных:\n{e}", parent=win)
            return

        messagebox.showinfo("Готово", "Регистрация прошла успешно! Теперь войдите.", parent=win)
        win.destroy()

    tk.Button(win, text="Зарегистрироваться", font=("Arial", 12, "bold"), command=submit).pack(pady=20)
