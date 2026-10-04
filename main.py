import re
import os
import hashlib
from pymongo.errors import DuplicateKeyError
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import PyMongoError
import tkinter as tk
from tkinter import messagebox

users_collection = db['users']
users_collection.create_index('email', unique=True)
users_collection.create_index('phone', unique=True)

current_user = None 

def hash_password(password, salt=None):
    salt or os.urandom(16)
    h = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100_000)
    return salt.hex(), h.hex()

def normalize_phone(phone):
    return re.sub(r"[^\d+]", "", phone)

def update_user_label():
    if current_user:
        user_label.config(text=f'user{current_user["email"]}')
        login_btn.pack_forget()
        register_btn.pack_forget()
        logout_btn.pack(side='left', padx=5)
    else:
        user_label.config(text='вы не вели пароль')
        logout_btn.pack_forget()
        login_btn.pack(side='left', padx=5)
        register_btn.pack(side='left', padx=5)

def logout():
    global current_user
    current_user = None      
# =========================
# MONGODB
# =========================

URL = "mongodb+srv://theodoreilyin_db_user:QciU8Ktbm5gaQob8@cluster0.v2xydoz.mongodb.net/?appName=Cluster0"

try:
    client = MongoClient(
        URL,
        serverSelectionTimeoutMS=5000
    )

    client.admin.command("ping")

    db = client["food_delivery"]
    orders_collection = db["orders"]

    print("MongoDB подключен")

except PyMongoError as e:
    print("Ошибка подключения к MongoDB:", e)
    orders_collection = None


# =========================
# РЕСТОРАНЫ И МЕНЮ
# =========================

restaurants = {
    "🍔 Burger House": [
        ("Чизбургер", 150),
        ("Гамбургер", 130),
        ("Картошка фри", 80),
        ("Кола", 40)
    ],

    "🍕 Pizza House": [
        ("Пицца Пепперони", 250),
        ("Пицца Маргарита", 220),
        ("Сырные палочки", 120),
        ("Кола", 40)
    ],

    "🍣 Sushi House": [
        ("Филадельфия", 300),
        ("Калифорния", 280),
        ("Суши с лососем", 200),
        ("Имбирь", 30)
    ]
}


# =========================
# КОРЗИНА
# =========================

cart = []


# =========================
# ПОКАЗ МЕНЮ
# =========================

def show_menu(restaurant):

    # Очищаем старое меню
    for widget in menu_frame.winfo_children():
        widget.destroy()

    # Заголовок ресторана
    title = tk.Label(
        menu_frame,
        text=restaurant,
        font=("Arial", 18, "bold")
    )
    title.pack(pady=10)

    # Товары
    for food, price in restaurants[restaurant]:

        row = tk.Frame(menu_frame)
        row.pack(
            fill="x",
            padx=20,
            pady=5
        )

        food_label = tk.Label(
            row,
            text=f"{food} - {price} грн",
            font=("Arial", 13)
        )
        food_label.pack(side="left")

        button = tk.Button(
            row,
            text="Добавить",
            command=lambda f=food, p=price: add_to_cart(f, p)
        )
        button.pack(side="right")


# =========================
# ДОБАВЛЕНИЕ В КОРЗИНУ
# =========================

def add_to_cart(food, price):

    cart.append((food, price))

    messagebox.showinfo(
        "Корзина",
        f"{food} добавлен в корзину"
    )

    update_cart()


# =========================
# ОБНОВЛЕНИЕ КОРЗИНЫ
# =========================

def update_cart():

    cart_list.delete(
        0,
        tk.END
    )

    total = 0

    for food, price in cart:

        cart_list.insert(
            tk.END,
            f"{food} - {price} грн"
        )

        total += price

    total_label.config(
        text=f"Итого: {total} грн"
    )


# =========================
# ОФОРМЛЕНИЕ ЗАКАЗА
# =========================

def make_order():

    if not cart:

        messagebox.showwarning(
            "Ошибка",
            "Корзина пуста"
        )

        return

    total = sum(
        price
        for food, price in cart
    )

    # Список товаров для MongoDB
    order_items = []

    for food, price in cart:

        order_items.append({
            "food": food,
            "price": price
        })

    # Данные заказа
    order = {
        "items": order_items,
        "total": total,
        "status": "готовится",
        "created_at": datetime.now()
    }

    # Сохраняем в MongoDB
    if orders_collection is not None:

        try:

            orders_collection.insert_one(order)

            print("Заказ сохранён в MongoDB")

        except PyMongoError as e:

            print(
                "Ошибка сохранения заказа:",
                e
            )

            messagebox.showerror(
                "Ошибка",
                "Не удалось сохранить заказ в MongoDB"
            )

            return

    # Сообщение пользователю
    messagebox.showinfo(
        "Заказ оформлен",
        f"Заказ успешно оформлен!\n\n"
        f"Сумма: {total} грн\n"
        f"Статус: готовится 🍳"
    )

    # Очищаем корзину
    cart.clear()

    update_cart()


# =========================
# ГЛАВНОЕ ОКНО
# =========================

root = tk.Tk()

root.title("Food Delivery App")

root.geometry("900x600")

root.resizable(
    False,
    False
)


# =========================
# HEADER
# =========================

header = tk.Frame(root)

header.pack(
    fill="x",
    pady=15
)


title = tk.Label(
    header,
    text="Food Delivery",
    font=("Arial", 24, "bold")
)

title.pack()


subtitle = tk.Label(
    header,
    text="Добро пожаловать в наш ресторан!",
    font=("Arial", 14)
)

subtitle.pack()


# =========================
# MAIN FRAME
# =========================

main_frame = tk.Frame(root)

main_frame.pack(
    fill="both",
    expand=True
)


# =========================
# РЕСТОРАНЫ
# =========================

restaurants_frame = tk.LabelFrame(
    main_frame,
    text="Рестораны",
    font=("Arial", 12, "bold")
)

restaurants_frame.pack(
    side="left",
    fill="y",
    padx=10,
    pady=10
)


for restaurant in restaurants:

    button = tk.Button(
        restaurants_frame,
        text=restaurant,
        width=20,
        command=lambda r=restaurant: show_menu(r)
    )

    button.pack(
        padx=10,
        pady=7
    )


# =========================
# МЕНЮ
# =========================

menu_frame = tk.LabelFrame(
    main_frame,
    text="Меню",
    font=("Arial", 12, "bold")
)

menu_frame.pack(
    side="left",
    fill="both",
    expand=True,
    padx=10,
    pady=10
)


# =========================
# КОРЗИНА
# =========================

cart_frame = tk.LabelFrame(
    main_frame,
    text="Корзина",
    font=("Arial", 12, "bold")
)

cart_frame.pack(
    side="right",
    fill="y",
    padx=10,
    pady=10
)


cart_list = tk.Listbox(
    cart_frame,
    width=28,
    height=15,
    font=("Arial", 11)
)

cart_list.pack(
    padx=10,
    pady=10
)


total_label = tk.Label(
    cart_frame,
    text="Итого: 0 грн",
    font=("Arial", 14, "bold")
)

total_label.pack(
    pady=10
)


order_button = tk.Button(
    cart_frame,
    text="Оформить заказ",
    font=("Arial", 12, "bold"),
    command=make_order
)

order_button.pack(
    padx=10,
    pady=10
)


# =========================
# ПОКАЗЫВАЕМ ПЕРВОЕ МЕНЮ
# =========================

show_menu("🍔 Burger House")


# =========================
# ЗАПУСК
# =========================

root.mainloop()