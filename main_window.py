import tkinter as tk
from tkinter import messagebox
from pymongo.errors import PyMongoError

import auth
import database
import orders
import state
from menu_data import restaurants
from login_window import open_login
from register_window import open_register


def build_app():
    root = tk.Tk()
    root.title("Food Delivery App")
    root.geometry("900x600")
    root.resizable(False, False)

    # ---------- функции, которым нужны виджеты ----------
    def update_user_label():
        if state.current_user:
            user_label.config(text=f"👤 {state.current_user['name']}")
            login_btn.pack_forget()
            register_btn.pack_forget()
            logout_btn.pack(side="left", padx=5)
        else:
            user_label.config(text="Вы не вошли")
            logout_btn.pack_forget()
            login_btn.pack(side="left", padx=5)
            register_btn.pack(side="left", padx=5)

    def do_logout():
        auth.logout()
        update_user_label()

    def update_cart():
        cart_list.delete(0, tk.END)
        for food, price in state.cart:
            cart_list.insert(tk.END, f"{food} - {price} грн")
        total_label.config(text=f"Итого: {orders.cart_total()} грн")

    def add_to_cart(food, price):
        orders.add_to_cart(food, price)
        messagebox.showinfo("Корзина", f"{food} добавлен в корзину")
        update_cart()

    def show_menu(restaurant):
        for widget in menu_frame.winfo_children():
            widget.destroy()

        tk.Label(menu_frame, text=restaurant, font=("Arial", 18, "bold")).pack(pady=10)

        for food, price in restaurants[restaurant]:
            row = tk.Frame(menu_frame)
            row.pack(fill="x", padx=20, pady=5)
            tk.Label(row, text=f"{food} - {price} грн", font=("Arial", 13)).pack(side="left")
            tk.Button(
                row, text="Добавить",
                command=lambda f=food, p=price: add_to_cart(f, p),
            ).pack(side="right")

    def make_order():
        if not state.cart:
            messagebox.showwarning("Ошибка", "Корзина пуста")
            return
        if state.current_user is None:
            messagebox.showwarning("Ошибка", "Войдите или зарегистрируйтесь, чтобы оформить заказ")
            open_login(root, update_user_label)
            return
        if database.orders_collection is None:
            messagebox.showerror("Ошибка", "Нет подключения к базе данных")
            return

        try:
            total = orders.create_order()
        except PyMongoError as e:
            print("Ошибка сохранения заказа:", e)
            messagebox.showerror("Ошибка", "Не удалось сохранить заказ в MongoDB")
            return

        messagebox.showinfo(
            "Заказ оформлен",
            f"Заказ успешно оформлен!\n\nСумма: {total} грн\nСтатус: готовится 🍳",
        )
        update_cart()

    # ---------- шапка ----------
    header = tk.Frame(root)
    header.pack(fill="x", pady=15)
    tk.Label(header, text="Food Delivery", font=("Arial", 24, "bold")).pack()
    tk.Label(header, text="Добро пожаловать в наш ресторан!", font=("Arial", 14)).pack()

    auth_frame = tk.Frame(header)
    auth_frame.pack(pady=5)
    user_label = tk.Label(auth_frame, text="Вы не вошли", font=("Arial", 11))
    user_label.pack(side="left", padx=10)
    login_btn = tk.Button(auth_frame, text="Войти", command=lambda: open_login(root, update_user_label))
    register_btn = tk.Button(auth_frame, text="Регистрация", command=lambda: open_register(root))
    logout_btn = tk.Button(auth_frame, text="Выйти", command=do_logout)

    # ---------- основная часть ----------
    main_frame = tk.Frame(root)
    main_frame.pack(fill="both", expand=True)

    restaurants_frame = tk.LabelFrame(main_frame, text="Рестораны", font=("Arial", 12, "bold"))
    restaurants_frame.pack(side="left", fill="y", padx=10, pady=10)
    for r in restaurants:
        tk.Button(
            restaurants_frame, text=r, width=20,
            command=lambda r=r: show_menu(r),
        ).pack(padx=10, pady=7)

    menu_frame = tk.LabelFrame(main_frame, text="Меню", font=("Arial", 12, "bold"))
    menu_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

    cart_frame = tk.LabelFrame(main_frame, text="Корзина", font=("Arial", 12, "bold"))
    cart_frame.pack(side="right", fill="y", padx=10, pady=10)
    cart_list = tk.Listbox(cart_frame, width=28, height=15, font=("Arial", 11))
    cart_list.pack(padx=10, pady=10)
    total_label = tk.Label(cart_frame, text="Итого: 0 грн", font=("Arial", 14, "bold"))
    total_label.pack(pady=10)
    tk.Button(
        cart_frame, text="Оформить заказ",
        font=("Arial", 12, "bold"), command=make_order,
    ).pack(padx=10, pady=10)

    update_user_label()
    show_menu("🍔 Burger House")
    return root