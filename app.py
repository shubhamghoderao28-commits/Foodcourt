from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-only-change-me")

# In-memory sample data for practice. Data resets whenever the server restarts.
MENU = [
    {"id": 1, "name": "Paneer Tikka Wrap", "category": "Wraps", "price": 179, "description": "Smoky paneer, crunchy vegetables, mint sauce.", "emoji": "🌯", "available": True},
    {"id": 2, "name": "Classic Veg Burger", "category": "Burgers", "price": 149, "description": "Crispy veg patty, lettuce, tomato, house sauce.", "emoji": "🍔", "available": True},
    {"id": 3, "name": "Margherita Pizza", "category": "Pizza", "price": 249, "description": "Mozzarella, basil, and rich tomato sauce.", "emoji": "🍕", "available": True},
    {"id": 4, "name": "Masala Dosa", "category": "Indian", "price": 129, "description": "Golden dosa with potato masala and chutneys.", "emoji": "🥞", "available": True},
    {"id": 5, "name": "Hakka Noodles", "category": "Asian", "price": 189, "description": "Wok-tossed noodles with vegetables.", "emoji": "🍜", "available": True},
    {"id": 6, "name": "Chocolate Brownie", "category": "Desserts", "price": 99, "description": "Warm chocolate brownie with a fudgy centre.", "emoji": "🍫", "available": True},
    {"id": 7, "name": "Mango Lassi", "category": "Drinks", "price": 89, "description": "Chilled yoghurt drink with mango.", "emoji": "🥭", "available": True},
    {"id": 8, "name": "French Fries", "category": "Sides", "price": 99, "description": "Golden fries with a pinch of seasoning.", "emoji": "🍟", "available": True},
]
ORDERS = []
NEXT_ORDER_ID = 1001


def get_cart():
    """Return cart stored in the user's session as {menu_item_id: quantity}."""
    return session.setdefault("cart", {})


def cart_details():
    cart = get_cart()
    lines = []
    for item in MENU:
        qty = int(cart.get(str(item["id"]), 0))
        if qty > 0:
            lines.append({**item, "quantity": qty, "line_total": qty * item["price"]})
    subtotal = sum(line["line_total"] for line in lines)
    delivery_fee = 0 if subtotal == 0 or subtotal >= 499 else 35
    return lines, subtotal, delivery_fee, subtotal + delivery_fee


@app.get("/")
def home():
    featured = [item for item in MENU if item["id"] in (1, 3, 4, 6)]
    return render_template("index.html", featured=featured)


@app.get("/menu")
def menu_page():
    category = request.args.get("category", "").strip()
    search = request.args.get("q", "").strip().lower()
    items = MENU
    if category:
        items = [item for item in items if item["category"].lower() == category.lower()]
    if search:
        items = [item for item in items if search in item["name"].lower() or search in item["description"].lower()]
    categories = sorted({item["category"] for item in MENU})
    return render_template("menu.html", items=items, categories=categories, selected_category=category, search=search)


@app.get("/cart")
def cart_page():
    lines, subtotal, delivery_fee, total = cart_details()
    return render_template("cart.html", lines=lines, subtotal=subtotal, delivery_fee=delivery_fee, total=total)


@app.get("/orders")
def orders_page():
    return render_template("orders.html", orders=list(reversed(ORDERS)))


@app.get("/api/menu")
def api_menu():
    """GET /api/menu?category=Pizza&q=margherita"""
    category = request.args.get("category", "").strip().lower()
    query = request.args.get("q", "").strip().lower()
    items = MENU
    if category:
        items = [x for x in items if x["category"].lower() == category]
    if query:
        items = [x for x in items if query in x["name"].lower() or query in x["description"].lower()]
    return jsonify({"count": len(items), "items": items})


@app.get("/api/menu/<int:item_id>")
def api_menu_item(item_id):
    item = next((x for x in MENU if x["id"] == item_id), None)
    if not item:
        return jsonify({"error": "Menu item not found"}), 404
    return jsonify(item)


@app.get("/api/cart")
def api_get_cart():
    lines, subtotal, delivery_fee, total = cart_details()
    return jsonify({"items": lines, "subtotal": subtotal, "delivery_fee": delivery_fee, "total": total})


@app.post("/api/cart")
def api_add_to_cart():
    """POST JSON: {\"item_id\": 1, \"quantity\": 1}"""
    data = request.get_json(silent=True) or request.form
    try:
        item_id = int(data.get("item_id", 0))
        quantity = int(data.get("quantity", 1))
    except (TypeError, ValueError):
        return jsonify({"error": "item_id and quantity must be integers"}), 400
    item = next((x for x in MENU if x["id"] == item_id), None)
    if not item:
        return jsonify({"error": "Menu item not found"}), 404
    if quantity < 1 or quantity > 20:
        return jsonify({"error": "quantity must be between 1 and 20"}), 400
    cart = dict(get_cart())
    key = str(item_id)
    cart[key] = min(int(cart.get(key, 0)) + quantity, 99)
    session["cart"] = cart
    return jsonify({"message": f'{item["name"]} added to cart', "cart": cart}), 201


@app.patch("/api/cart/<int:item_id>")
def api_update_cart_item(item_id):
    """PATCH JSON: {\"quantity\": 3}; quantity 0 removes the item."""
    if not any(x["id"] == item_id for x in MENU):
        return jsonify({"error": "Menu item not found"}), 404
    data = request.get_json(silent=True) or {}
    try:
        quantity = int(data.get("quantity", 1))
    except (TypeError, ValueError):
        return jsonify({"error": "quantity must be an integer"}), 400
    if not 0 <= quantity <= 99:
        return jsonify({"error": "quantity must be between 0 and 99"}), 400
    cart = dict(get_cart())
    if quantity == 0:
        cart.pop(str(item_id), None)
    else:
        cart[str(item_id)] = quantity
    session["cart"] = cart
    lines, subtotal, delivery_fee, total = cart_details()
    return jsonify({"items": lines, "subtotal": subtotal, "delivery_fee": delivery_fee, "total": total})


@app.delete("/api/cart/<int:item_id>")
def api_remove_cart_item(item_id):
    cart = dict(get_cart())
    cart.pop(str(item_id), None)
    session["cart"] = cart
    lines, subtotal, delivery_fee, total = cart_details()
    return jsonify({"message": "Item removed", "items": lines, "subtotal": subtotal, "delivery_fee": delivery_fee, "total": total})


@app.post("/api/checkout")
def api_checkout():
    global NEXT_ORDER_ID
    lines, subtotal, delivery_fee, total = cart_details()
    if not lines:
        return jsonify({"error": "Your cart is empty"}), 400
    data = request.get_json(silent=True) or request.form
    customer_name = str(data.get("customer_name", "Guest")).strip()[:80] or "Guest"
    address = str(data.get("address", "Pickup")).strip()[:240] or "Pickup"
    order = {
        "id": NEXT_ORDER_ID,
        "customer_name": customer_name,
        "address": address,
        "items": lines,
        "subtotal": subtotal,
        "delivery_fee": delivery_fee,
        "total": total,
        "status": "Confirmed",
        "created_at": datetime.now().strftime("%d %b %Y, %I:%M %p"),
    }
    NEXT_ORDER_ID += 1
    ORDERS.append(order)
    session["cart"] = {}
    return jsonify({"message": "Order placed successfully", "order": order}), 201


@app.post("/checkout")
def checkout_form():
    # HTML forms should return to the cart if it is empty.
    if not cart_details()[0]:
        return redirect(url_for("cart_page"))
    # Form submissions use the same checkout logic; redirect to order history.
    api_checkout()
    return redirect(url_for("orders_page"))


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "food-ordering-practice-api"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
