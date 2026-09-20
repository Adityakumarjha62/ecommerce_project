from flask import Blueprint, request, jsonify, session
import mysql.connector

from config import Config


cart_bp = Blueprint(
    "cart",
    __name__,
    url_prefix="/api/cart"
)


def get_db_connection():

    return mysql.connector.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DATABASE
    )


# Get or Create User Cart
def get_user_cart(user_id):

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

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

        cursor.execute(
            """
            INSERT INTO cart (user_id)
            VALUES (%s)
            """,
            (user_id,)
        )

        connection.commit()

        cart_id = cursor.lastrowid

    else:

        cart_id = cart["id"]

    cursor.close()
    connection.close()

    return cart_id


# Add Product to Cart
@cart_bp.route("/add", methods=["POST"])
def add_to_cart():

    user_id = session.get("user_id")

    if not user_id:

        return jsonify({
            "status": "error",
            "message": "Please login first"
        }), 401


    data = request.get_json()

    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)


    if not product_id:

        return jsonify({
            "status": "error",
            "message": "Product ID is required"
        }), 400


    if quantity <= 0:

        return jsonify({
            "status": "error",
            "message": "Quantity must be greater than 0"
        }), 400


    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)


    # Check product
    cursor.execute(
        """
        SELECT id, name, price, stock
        FROM products
        WHERE id = %s
        AND status = 'active'
        """,
        (product_id,)
    )

    product = cursor.fetchone()


    if not product:

        cursor.close()
        connection.close()

        return jsonify({
            "status": "error",
            "message": "Product not found"
        }), 404


    # Check stock
    if product["stock"] < quantity:

        cursor.close()
        connection.close()

        return jsonify({
            "status": "error",
            "message": "Not enough stock"
        }), 400


    # Find user's cart
    cursor.execute(
        """
        SELECT id
        FROM cart
        WHERE user_id = %s
        """,
        (user_id,)
    )

    cart = cursor.fetchone()


    # Create cart if it doesn't exist
    if not cart:

        cursor.execute(
            """
            INSERT INTO cart (user_id)
            VALUES (%s)
            """,
            (user_id,)
        )

        cart_id = cursor.lastrowid

    else:

        cart_id = cart["id"]


    # Check existing product in cart
    cursor.execute(
        """
        SELECT id, quantity
        FROM cart_items
        WHERE cart_id = %s
        AND product_id = %s
        """,
        (cart_id, product_id)
    )

    existing_item = cursor.fetchone()


    if existing_item:

        new_quantity = existing_item["quantity"] + quantity


        if new_quantity > product["stock"]:

            cursor.close()
            connection.close()

            return jsonify({
                "status": "error",
                "message": "Quantity exceeds available stock"
            }), 400


        cursor.execute(
            """
            UPDATE cart_items
            SET quantity = %s
            WHERE id = %s
            """,
            (new_quantity, existing_item["id"])
        )

    else:

        cursor.execute(
            """
            INSERT INTO cart_items
            (cart_id, product_id, quantity)
            VALUES (%s, %s, %s)
            """,
            (cart_id, product_id, quantity)
        )


    connection.commit()

    cursor.close()
    connection.close()


    return jsonify({
        "status": "success",
        "message": "Product added to cart"
    })


# Get Cart
@cart_bp.route("/", methods=["GET"])
def get_cart():

    user_id = session.get("user_id")


    if not user_id:

        return jsonify({
            "status": "error",
            "message": "Please login first"
        }), 401


    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)


    cursor.execute(
        """
        SELECT
            cart_items.id AS cart_item_id,
            cart_items.product_id,
            cart_items.quantity,
            products.name,
            products.price,
            products.image,
            products.stock

        FROM cart_items

        JOIN cart
            ON cart_items.cart_id = cart.id

        JOIN products
            ON cart_items.product_id = products.id

        WHERE cart.user_id = %s
        """,
        (user_id,)
    )


    items = cursor.fetchall()


    total = 0


    for item in items:

        item["price"] = float(item["price"])

        item["subtotal"] = (
            item["price"] * item["quantity"]
        )

        total += item["subtotal"]


    cursor.close()
    connection.close()


    return jsonify({
        "status": "success",
        "items": items,
        "total": total
    })


# Remove Product From Cart
@cart_bp.route(
    "/remove/<int:cart_item_id>",
    methods=["DELETE"]
)
def remove_from_cart(cart_item_id):

    user_id = session.get("user_id")


    if not user_id:

        return jsonify({
            "status": "error",
            "message": "Please login first"
        }), 401


    connection = get_db_connection()
    cursor = connection.cursor()


    cursor.execute(
        """
        DELETE cart_items
        FROM cart_items

        JOIN cart
            ON cart_items.cart_id = cart.id

        WHERE cart_items.id = %s
        AND cart.user_id = %s
        """,
        (cart_item_id, user_id)
    )


    connection.commit()


    cursor.close()
    connection.close()


    return jsonify({
        "status": "success",
        "message": "Product removed from cart"
    })