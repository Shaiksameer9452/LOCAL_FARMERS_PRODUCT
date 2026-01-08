from flask import Flask, render_template, request, redirect, session,url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret"

def get_db():
    conn = sqlite3.connect("store.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def home():
    db = get_db()
    products = db.execute("SELECT * FROM products").fetchall()
    return render_template("home.html", products=products)

@app.route("/product/<int:product_id>")
def product_details(product_id):
    db = get_db()
    product = db.execute(
        "SELECT * FROM products WHERE id = ?",
        (product_id,)
    ).fetchone()

    if product is None:
        return "Product not found", 404
    return render_template("product_details.html", product=product)


@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        db = get_db()
        db.execute(
            "INSERT INTO users (username,email,password,role) VALUES (?,?,?,?)",
            (
                request.form["username"],
                request.form["email"],
                generate_password_hash(request.form["password"]),
                request.form["role"]
            )
        )
        db.commit()
        return redirect("/login")
    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE email=?",
            (request.form["email"],)
        ).fetchone()

        if user and check_password_hash(user["password"], request.form["password"]):
            session["user_id"] = user["id"]
            session["role"] = user["role"]
            return redirect("/products")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/products")
def products():
    db = get_db()
    products = db.execute("SELECT * FROM products").fetchall()
    return render_template("products.html", products=products)

@app.route("/add_to_cart/<int:product_id>")
def add_to_cart(product_id):
    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("login"))

    db = get_db()

    # Check if product already in cart
    item = db.execute(
        "SELECT * FROM cart WHERE user_id = ? AND product_id = ?",
        (user_id, product_id)
    ).fetchone()

    if item:
        # Increase quantity
        db.execute(
            "UPDATE cart SET quantity = quantity + 1 WHERE id = ?",
            (item["id"],)
        )
    else:
        # Insert new item
        db.execute(
            "INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, ?)",
            (user_id, product_id, 1)
        )

    db.commit()
    return redirect(url_for("view_cart"))


@app.route("/farmer/dashboard", methods=["GET","POST"])
def farmer_dashboard():
    if session.get("role") != "farmer":
        return redirect("/login")

    db = get_db()

    if request.method == "POST":
        db.execute(
            "INSERT INTO products (name,price,quantity,farmer_id) VALUES (?,?,?,?)",
            (
                request.form["name"],
                request.form["price"],
                request.form["quantity"],
                session["user_id"]
            )
        )
        db.commit()

    products = db.execute(
        "SELECT * FROM products WHERE farmer_id=?",
        (session["user_id"],)
    ).fetchall()

    return render_template("farmer_dashboard.html", products=products)

@app.route("/orders")
def orders():
    if "user_id" not in session:
        return redirect("/login")

    db = get_db()
    orders = db.execute("""
        SELECT products.name, orders.quantity, orders.status
        FROM orders
        JOIN products ON products.id = orders.product_id
        WHERE orders.user_id = ?
    """, (session["user_id"],)).fetchall()

    return render_template("orders.html", orders=orders)

@app.route("/cart")
def view_cart():
    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("login"))

    db = get_db()
    cart_items = db.execute("""
        SELECT cart.id, products.name, products.price, cart.quantity
        FROM cart
        JOIN products ON cart.product_id = products.id
        WHERE cart.user_id = ?
    """, (user_id,)).fetchall()

    return render_template("cart.html", cart_items=cart_items)

@app.route("/place_order")
def place_order():
    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("login"))

    db = get_db()

    # Get cart items
    cart_items = db.execute("""
        SELECT cart.product_id, cart.quantity, products.price
        FROM cart
        JOIN products ON cart.product_id = products.id
        WHERE cart.user_id = ?
    """, (user_id,)).fetchall()

    if not cart_items:
        return redirect(url_for("view_cart"))

    # Calculate total price
    total_price = sum(item["price"] * item["quantity"] for item in cart_items)

    # Create order
    cursor = db.execute("""
        INSERT INTO orders (user_id, total_price, status, created_at)
        VALUES (?, ?, ?, ?)
    """, (user_id, total_price, "pending", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    order_id = cursor.lastrowid

    # Insert order items
    for item in cart_items:
        db.execute("""
            INSERT INTO order_items (order_id, product_id, quantity, price)
            VALUES (?, ?, ?, ?)
        """, (order_id, item["product_id"], item["quantity"], item["price"]))
        db.execute("""
            UPDATE products
            SET quantity = quantity - ?
            WHERE id = ?
        """, (item["quantity"], item["product_id"]))

    # Clear cart
    db.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
    db.commit()

    return redirect(url_for("order_success"))

@app.route("/order_success")
def order_success():
    return render_template("order_success.html")

@app.route("/my_orders")
def my_orders():
    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("login"))

    db = get_db()

    orders = db.execute("""
        SELECT 
            orders.id AS order_id,
            orders.created_at,
            orders.status,
            products.name AS product_name,
            order_items.quantity,
            order_items.price
        FROM orders
        JOIN order_items ON orders.id = order_items.order_id
        JOIN products ON order_items.product_id = products.id
        WHERE orders.user_id = ?
        ORDER BY orders.created_at DESC
    """, (user_id,)).fetchall()

    return render_template("my_orders.html", orders=orders)



@app.route("/debug-db")
def debug_db():
    db = get_db()
    tables = db.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()
    return str(tables)

@app.route("/debug-products")
def debug_products():
    db = get_db()
    return str(db.execute("SELECT * FROM products").fetchall())

@app.route("/farmer/orders")
def farmer_orders():
    farmer_id = session.get("user_id")

    if not farmer_id:
        return redirect(url_for("login"))

    db = get_db()

    orders = db.execute("""
        SELECT 
            orders.id AS order_id,
            orders.created_at,
            orders.status,
            products.name AS product_name,
            order_items.quantity,
            order_items.price,
            users.username AS customer_name
        FROM order_items
        JOIN orders ON order_items.order_id = orders.id
        JOIN products ON order_items.product_id = products.id
        JOIN users ON orders.user_id = users.id
        WHERE products.farmer_id = ?
        ORDER BY orders.created_at DESC
    """, (farmer_id,)).fetchall()
    return render_template("farmer_orders.html", orders=orders)

@app.route("/admin_orders")
def admin_orders():
    if session.get("role") != "admin":
        return "Access denied", 403

    db = get_db()
    orders = db.execute("""
        SELECT 
            orders.id AS order_id,
            orders.created_at,
            orders.status,
            orders.total_price,
            users.username AS customer_name
        FROM orders
        JOIN users ON orders.user_id = users.id
        ORDER BY orders.created_at DESC
    """).fetchall()

    return render_template("admin_orders.html", orders=orders)

@app.route("/admin/update_order/<int:order_id>/<string:new_status>")
def admin_update_order(order_id, new_status):
    if session.get("role") != "admin":
        return "Access denied", 403

    db = get_db()
    db.execute(
        "UPDATE orders SET status = ? WHERE id = ?",
        (new_status, order_id)
    )
    db.commit()
    return redirect(url_for("admin_orders"))


@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        db = get_db()

        user = db.execute(
            "SELECT * FROM users WHERE username = ? AND email = ? AND password = ?",
            (username, email, password)
        ).fetchone()   # 🔥 THIS IS REQUIRED

        if user:
            session["user_id"] = user["id"]
            session["role"] = user["role"]

            # ✅ redirect admin to admin_orders
            if user["role"] == "admin":
                return redirect(url_for("admin_orders"))
            else:
                return redirect(url_for("home"))

        return "Invalid email or password"

    return render_template("admin_login.html")
@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))

if __name__ == "__main__":
    app.run(debug=True)
