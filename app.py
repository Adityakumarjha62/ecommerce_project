# from flask import Flask, jsonify
# import mysql.connector
# from config import Config

# app = Flask(__name__)
# app.config.from_object(Config)


# def get_db_connection():
#     connection = mysql.connector.connect(
#         host=app.config["MYSQL_HOST"],
#         user=app.config["MYSQL_USER"],
#         password=app.config["MYSQL_PASSWORD"],
#         database=app.config["MYSQL_DATABASE"]
#     )

#     return connection


# @app.route("/")
# def home():
#     return jsonify({
#         "message": "E-Commerce API is running",
#         "status": "success"
#     })


# @app.route("/api/test-db")
# def test_database():
#     try:
#         connection = get_db_connection()
#         cursor = connection.cursor()

#         cursor.execute("SELECT DATABASE()")
#         database = cursor.fetchone()

#         cursor.close()
#         connection.close()

#         return jsonify({
#             "status": "success",
#             "message": "MySQL connected successfully",
#             "database": database[0]
#         })

#     except mysql.connector.Error as error:
#         return jsonify({
#             "status": "error",
#             "message": str(error)
#         }), 500


# if __name__ == "__main__":
#     app.run(debug=True)



# from flask import Flask, jsonify


# from flask import Flask, jsonify, render_template
# import mysql.connector

# from config import Config
# from routes.auth import auth_bp
# from routes.products import products_bp
# from routes.cart import cart_bp

# app = Flask(__name__)

# app.config.from_object(Config)

# app.register_blueprint(auth_bp)

# app.register_blueprint(products_bp)

# app.register_blueprint(cart_bp)

# @app.route("/home")
# def home_page():
#     return render_template("home.html")

# def get_db_connection():

#     connection = mysql.connector.connect(
#         host=app.config["MYSQL_HOST"],
#         user=app.config["MYSQL_USER"],
#         password=app.config["MYSQL_PASSWORD"],
#         database=app.config["MYSQL_DATABASE"]
#     )

#     return connection


# @app.route("/")
# def home():

#     return jsonify({
#         "message": "E-Commerce API is running",
#         "status": "success"
#     })
# @app.route("/register")
# def register_page():
#     return render_template("register.html")


# @app.route("/login")
# def login_page():
#     return render_template("login.html")

# @app.route("/home")
# def home_page():
#     return render_template("home.html")

# @app.route("/api/test-db")
# def test_database():

#     try:

#         connection = get_db_connection()
#         cursor = connection.cursor()

#         cursor.execute("SELECT DATABASE()")

#         database = cursor.fetchone()

#         cursor.close()
#         connection.close()

#         return jsonify({
#             "status": "success",
#             "message": "MySQL connected successfully",
#             "database": database[0]
#         })

#     except mysql.connector.Error as error:

#         return jsonify({
#             "status": "error",
#             "message": str(error)
#         }), 500


# if __name__ == "__main__":
#     app.run(debug=True)



# from operator import add

from flask import Flask, jsonify, render_template
import mysql.connector
import os

from config import Config
from routes.auth import auth_bp
from routes.products import products_bp
from routes.cart import cart_bp
from routes.orders import orders_bp
from routes.admin import admin_bp
from routes.wishlist import wishlist_bp



app = Flask(__name__)

app.config.from_object(Config)


# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(products_bp)
app.register_blueprint(cart_bp)
app.register_blueprint(orders_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(wishlist_bp)


# Database Connection
def get_db_connection():

    connection = mysql.connector.connect(
        host=app.config["MYSQL_HOST"],
        user=app.config["MYSQL_USER"],
        password=app.config["MYSQL_PASSWORD"],
        database=app.config["MYSQL_DATABASE"]
    )

    return connection


# Home API
@app.route("/")
def home():

    return jsonify({
        "message": "E-Commerce API is running",
        "status": "success"
    })


# Register Page
@app.route("/register")
def register_page():

    return render_template("register.html")


# Login Page
@app.route("/login")
def login_page():

    return render_template("login.html")


# Home Page
@app.route("/home")
def home_page():

    return render_template("home.html")

@app.route("/dashboard")
def dashboard_page():
    return render_template("dashboard.html")


@app.route("/admin/dashboard")
def admin_dashboard_page():
    return render_template("dashboard.html")

@app.route("/cart")
def cart_page():
    return render_template("cart.html")

@app.route("/checkout")
def checkout_page():
    return render_template("checkout.html")

# ==============================
# Orders Page
# ==============================
@app.route("/orders")
def orders_page():
    return render_template("orders1.html")


# Profile Page
@app.route("/profile")
def profile_page():
    return render_template("profile.html")


@app.route("/admin/products")
def admin_products_page():

    return render_template(
        "admin/products.html"
    )


@app.route("/admin/orders")
def admin_orders_page():

    return render_template(
        "admin/orders2.html"
    )

@app.route("/admin/users")
def admin_users_page():
    return render_template("admin/users.html")

@app.route("/order-details/<int:order_id>")
def order_details_page(order_id):
    return render_template(
        "order_details.html",
        order_id=order_id
    )

@app.route("/wishlist")
def wishlist_page():
    return render_template("wishlist.html")

@app.route("/product/<int:product_id>")
def product_details_page(product_id):
    return render_template(
        "product_details.html",
        product_id=product_id
    )    

# Test Database
@app.route("/api/test-db")
def test_database():

    try:

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT DATABASE()")

        database = cursor.fetchone()

        cursor.close()
        connection.close()

        return jsonify({
            "status": "success",
            "message": "MySQL connected successfully",
            "database": database[0]
        })

    except mysql.connector.Error as error:

        return jsonify({
            "status": "error",
            "message": str(error)
        }), 500


# if __name__ == "__main__":

#     app.run(debug=True)

# if __name__ == "__main__":
#     import webbrowser
#     from threading import Timer

#     def open_browser():
#         webbrowser.open("http://127.0.0.1:5000/login")

#     Timer(1, open_browser).start()

    # app.run(debug=True, use_reloader=False)

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False,
        use_reloader=False
    )    
# git add app.py
# git commit -m "Fix Railway deployment port"
# git push