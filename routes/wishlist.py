from flask import Blueprint, jsonify, session
import mysql.connector

from config import Config


# ==========================================
# WISHLIST BLUEPRINT
# ==========================================

wishlist_bp = Blueprint(
    "wishlist",
    __name__,
    url_prefix="/api/wishlist"
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
# ADD PRODUCT TO WISHLIST
# ==========================================

@wishlist_bp.route("/add/<int:product_id>", methods=["POST"])
def add_to_wishlist(product_id):

    user_id = session.get("user_id")


    if not user_id:

        return jsonify({

            "status": "error",

            "message": "Please login first"

        }), 401


    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)


    try:

        # Check product
        cursor.execute("""
            SELECT
                id,
                name,
                price,
                image,
                status
            FROM products
            WHERE id = %s
            AND status = 'active'
        """, (product_id,))


        product = cursor.fetchone()


        if not product:

            return jsonify({

                "status": "error",

                "message": "Product not found"

            }), 404


        # Check existing wishlist item
        cursor.execute("""
            SELECT id
            FROM wishlist
            WHERE user_id = %s
            AND product_id = %s
        """, (
            user_id,
            product_id
        ))


        existing_item = cursor.fetchone()


        if existing_item:

            return jsonify({

                "status": "error",

                "message":
                    "Product already in wishlist"

            }), 409


        # Add to wishlist
        cursor.execute("""
            INSERT INTO wishlist
            (user_id, product_id)
            VALUES (%s, %s)
        """, (
            user_id,
            product_id
        ))


        connection.commit()


        return jsonify({

            "status": "success",

            "message":
                "Product added to wishlist"

        }), 201


    except mysql.connector.Error as error:

        connection.rollback()


        return jsonify({

            "status": "error",

            "message": str(error)

        }), 500


    finally:

        cursor.close()
        connection.close()


# ==========================================
# GET MY WISHLIST
# ==========================================

@wishlist_bp.route("/", methods=["GET"])
def get_wishlist():

    user_id = session.get("user_id")


    if not user_id:

        return jsonify({

            "status": "error",

            "message": "Please login first"

        }), 401


    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)


    try:

        cursor.execute("""
            SELECT

                wishlist.id AS wishlist_id,

                products.id AS product_id,

                products.name,

                products.description,

                products.price,

                products.discount,

                products.stock,

                products.image,

                products.status

            FROM wishlist

            JOIN products
                ON wishlist.product_id =
                   products.id

            WHERE wishlist.user_id = %s

            ORDER BY wishlist.id DESC
        """, (user_id,))


        items = cursor.fetchall()


        for item in items:

            item["price"] = float(
                item["price"]
            )

            item["discount"] = float(
                item["discount"]
            )


        return jsonify({

            "status": "success",

            "wishlist": items,

            "count": len(items)

        })


    except mysql.connector.Error as error:

        return jsonify({

            "status": "error",

            "message": str(error)

        }), 500


    finally:

        cursor.close()
        connection.close()


# ==========================================
# REMOVE FROM WISHLIST
# ==========================================

@wishlist_bp.route(
    "/remove/<int:product_id>",
    methods=["DELETE"]
)
def remove_from_wishlist(product_id):

    user_id = session.get("user_id")


    if not user_id:

        return jsonify({

            "status": "error",

            "message": "Please login first"

        }), 401


    connection = get_db_connection()
    cursor = connection.cursor()


    try:

        cursor.execute("""
            DELETE FROM wishlist
            WHERE user_id = %s
            AND product_id = %s
        """, (
            user_id,
            product_id
        ))


        if cursor.rowcount == 0:

            return jsonify({

                "status": "error",

                "message":
                    "Product not found in wishlist"

            }), 404


        connection.commit()


        return jsonify({

            "status": "success",

            "message":
                "Product removed from wishlist"

        })


    except mysql.connector.Error as error:

        connection.rollback()


        return jsonify({

            "status": "error",

            "message": str(error)

        }), 500


    finally:

        cursor.close()
        connection.close()


# ==========================================
# CHECK WISHLIST
# ==========================================

@wishlist_bp.route(
    "/check/<int:product_id>",
    methods=["GET"]
)
def check_wishlist(product_id):

    user_id = session.get("user_id")


    if not user_id:

        return jsonify({

            "status": "error",

            "message": "Please login first"

        }), 401


    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)


    try:

        cursor.execute("""
            SELECT id
            FROM wishlist
            WHERE user_id = %s
            AND product_id = %s
        """, (
            user_id,
            product_id
        ))


        item = cursor.fetchone()


        return jsonify({

            "status": "success",

            "in_wishlist":
                item is not None

        })


    except mysql.connector.Error as error:

        return jsonify({

            "status": "error",

            "message": str(error)

        }), 500


    finally:

        cursor.close()
        connection.close()