from datetime import datetime

import database
import state


def add_to_cart(food, price):
    state.cart.append((food, price))


def cart_total():
    return sum(price for _, price in state.cart)

def create_order():
    user = state.current_user
    total = cart_total()

    order = {
        "user_id": user["_id"],
        "customer": user["name"],
        "email": user["email"],
        "phone": user["phone"],
        "items": [{"food": f, "price": p} for f, p in state.cart],
        "total": total,
        "status": "готовится",
        "created_at": datetime.now(),
    }
    database.orders_collection.insert_one(order)
    state.cart.clear()
    return total
