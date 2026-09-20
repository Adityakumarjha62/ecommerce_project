from flask import Blueprint, request, jsonify, session
import mysql.connector

from config import Config


orders_bp = Blueprint(
    "orders",
    __name__,
    url_prefix="/api/orders"
)


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_db_connection():

    return mysql.connector.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DATABASE
    )


# ==========================================
# CHECKOUT / CREATE ORDER
# ==========================================

@orders_bp.route("/checkout", methods=["POST"])
def checkout():

    user_id = session.get("user_id")

    if not user_id:

        return jsonify({
            "status": "error",
            "message": "Please login first"
        }), 401


    data = request.get_json()


    if not data:

        return jsonify({
            "status": "error",
            "message": "Request data is required"
        }), 400


    shipping_address = data.get("shipping_address")


    if not shipping_address or not shipping_address.strip():

        return jsonify({
            "status": "error",
            "message": "Shipping address is required"
        }), 400


    connection = get_db_connection()

    cursor = connection.cursor(dictionary=True)


    try:

        # ----------------------------------
        # GET USER CART
        # ----------------------------------

        cursor.execute(
            """
            SELECT id
            FROM cart
            WHERE user_id = %s
            """,
            (user_id,)
        )


        cart = cursor.fetchone()


        if not cart:

            return jsonify({
                "status": "error",
                "message": "Cart is empty"
            }), 400


        cart_id = cart["id"]


        # ----------------------------------
        # GET CART ITEMS
        # ----------------------------------

        cursor.execute(
            """
            SELECT
                cart_items.product_id,
                cart_items.quantity,
                products.name,
                products.price,
                products.stock
            FROM cart_items
            JOIN products
                ON cart_items.product_id = products.id
            WHERE cart_items.cart_id = %s
            """,
            (cart_id,)
        )


        items = cursor.fetchall()


        if not items:

            return jsonify({
                "status": "error",
                "message": "Cart is empty"
            }), 400


        # ----------------------------------
        # CALCULATE TOTAL
        # ----------------------------------

        total_amount = 0


        for item in items:

            if item["quantity"] <= 0:

                return jsonify({
                    "status": "error",
                    "message":
                        f"Invalid quantity for {item['name']}"
                }), 400


            if item["quantity"] > item["stock"]:

                return jsonify({
                    "status": "error",
                    "message":
                        f"Not enough stock for {item['name']}"
                }), 400


            total_amount += (
                float(item["price"])
                * item["quantity"]
            )


        # ----------------------------------
        # CREATE ORDER
        # ----------------------------------

        cursor.execute(
            """
            INSERT INTO orders
            (
                user_id,
                total_amount,
                status,
                shipping_address
            )
            VALUES (%s, %s, %s, %s)
            """,
            (
                user_id,
                total_amount,
                "confirmed",
                shipping_address.strip()
            )
        )


        order_id = cursor.lastrowid


        # ----------------------------------
        # CREATE ORDER ITEMS
        # ----------------------------------

        for item in items:

            cursor.execute(
                """
                INSERT INTO order_items
                (
                    order_id,
                    product_id,
                    quantity,
                    price
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    order_id,
                    item["product_id"],
                    item["quantity"],
                    item["price"]
                )
            )


            # ----------------------------------
            # UPDATE PRODUCT STOCK
            # ----------------------------------

            cursor.execute(
                """
                UPDATE products
                SET stock = stock - %s
                WHERE id = %s
                """,
                (
                    item["quantity"],
                    item["product_id"]
                )
            )


        # ----------------------------------
        # CLEAR CART
        # ----------------------------------

        cursor.execute(
            """
            DELETE FROM cart_items
            WHERE cart_id = %s
            """,
            (cart_id,)
        )


        connection.commit()


        return jsonify({

            "status": "success",

            "message":
                "Order placed successfully",

            "order_id":
                order_id,

            "total_amount":
                total_amount

        })


    except mysql.connector.Error as error:

        connection.rollback()


        return jsonify({

            "status": "error",

            "message":
                str(error)

        }), 500


    finally:

        cursor.close()

        connection.close()



# ==========================================
# GET MY ORDERS
# ==========================================

@orders_bp.route("/", methods=["GET"])
def get_orders():

    user_id = session.get("user_id")


    if not user_id:

        return jsonify({

            "status": "error",

            "message":
                "Please login first"

        }), 401


    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )


    try:

        cursor.execute(
            """
            SELECT
                id,
                total_amount,
                status,
                shipping_address,
                created_at,
                updated_at
            FROM orders
            WHERE user_id = %s
            ORDER BY created_at DESC
            """,
            (user_id,)
        )


        orders = cursor.fetchall()


        for order in orders:

            order["total_amount"] = float(
                order["total_amount"]
            )


            if order["created_at"]:

                order["created_at"] = (
                    order["created_at"]
                    .strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                )


            if order["updated_at"]:

                order["updated_at"] = (
                    order["updated_at"]
                    .strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                )


        return jsonify({

            "status": "success",

            "orders": orders

        })


    except mysql.connector.Error as error:

        return jsonify({

            "status": "error",

            "message":
                str(error)

        }), 500


    finally:

        cursor.close()

        connection.close()



# ==========================================
# GET ORDER DETAILS
# ==========================================

@orders_bp.route(
    "/<int:order_id>",
    methods=["GET"]
)
def get_order_details(order_id):

    user_id = session.get("user_id")


    if not user_id:

        return jsonify({

            "status": "error",

            "message":
                "Please login first"

        }), 401


    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )


    try:

        # ----------------------------------
        # GET ORDER
        # ----------------------------------

        cursor.execute(
            """
            SELECT
                id,
                total_amount,
                status,
                shipping_address,
                created_at,
                updated_at
            FROM orders
            WHERE id = %s
            AND user_id = %s
            """,
            (
                order_id,
                user_id
            )
        )


        order = cursor.fetchone()


        if not order:

            return jsonify({

                "status": "error",

                "message":
                    "Order not found"

            }), 404


        # ----------------------------------
        # GET ORDER PRODUCTS
        # ----------------------------------

        cursor.execute(
            """
            SELECT
                order_items.product_id,
                order_items.quantity,
                order_items.price,
                products.name,
                products.image
            FROM order_items
            JOIN products
                ON order_items.product_id = products.id
            WHERE order_items.order_id = %s
            """,
            (order_id,)
        )


        items = cursor.fetchall()


        # ----------------------------------
        # CALCULATE SUBTOTAL
        # ----------------------------------

        for item in items:

            item["price"] = float(
                item["price"]
            )


            item["subtotal"] = (
                item["price"]
                * item["quantity"]
            )


        # ----------------------------------
        # FORMAT ORDER
        # ----------------------------------

        order["total_amount"] = float(
            order["total_amount"]
        )


        if order["created_at"]:

            order["created_at"] = (
                order["created_at"]
                .strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            )


        if order["updated_at"]:

            order["updated_at"] = (
                order["updated_at"]
                .strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            )


        # ----------------------------------
        # RETURN ORDER DETAILS
        # ----------------------------------

        return jsonify({

            "status": "success",

            "order": order,

            "items": items

        })


    except mysql.connector.Error as error:

        return jsonify({

            "status": "error",

            "message":
                str(error)

        }), 500


    finally:

        cursor.close()

        connection.close()