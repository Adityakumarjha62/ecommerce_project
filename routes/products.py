from flask import Blueprint, request, jsonify
import mysql.connector

from config import Config


products_bp = Blueprint(
    "products",
    __name__,
    url_prefix="/api/products"
)


def get_db_connection():
    return mysql.connector.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DATABASE
    )


# GET all products
@products_bp.route("/", methods=["GET"])
def get_products():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        search = request.args.get("search", "").strip()

        if search:
            cursor.execute(
                """
                SELECT *
                FROM products
                WHERE status = 'active'
                AND (name LIKE %s OR description LIKE %s)
                ORDER BY created_at DESC
                """,
                (f"%{search}%", f"%{search}%")
            )
        else:
            cursor.execute(
                """
                SELECT *
                FROM products
                WHERE status = 'active'
                ORDER BY created_at DESC
                """
            )

        products = cursor.fetchall()

        return jsonify({
            "status": "success",
            "count": len(products),
            "products": products
        })

    finally:
        cursor.close()
        connection.close()


# GET single product
@products_bp.route("/<int:product_id>", methods=["GET"])
def get_product(product_id):

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT *
            FROM products
            WHERE id = %s
            AND status = 'active'
            """,
            (product_id,)
        )

        product = cursor.fetchone()

        if not product:
            return jsonify({
                "status": "error",
                "message": "Product not found"
            }), 404

        return jsonify({
            "status": "success",
            "product": product
        })

    finally:
        cursor.close()
        connection.close()


# ADD product
@products_bp.route("/", methods=["POST"])
def add_product():

    data = request.get_json(silent=True) or {}

    name = data.get("name", "").strip()
    description = data.get("description", "")
    price = data.get("price")
    discount = data.get("discount", 0)
    stock = data.get("stock", 0)
    image = data.get("image")
    category_id = data.get("category_id")

    if not name or price is None:
        return jsonify({
            "status": "error",
            "message": "Name and price are required"
        }), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO products
            (category_id, name, description, price, discount, stock, image)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                category_id,
                name,
                description,
                price,
                discount,
                stock,
                image
            )
        )

        connection.commit()

        return jsonify({
            "status": "success",
            "message": "Product added successfully",
            "product_id": cursor.lastrowid
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


# UPDATE product
@products_bp.route("/<int:product_id>", methods=["PUT"])
def update_product(product_id):

    data = request.get_json(silent=True) or {}

    name = data.get("name")
    description = data.get("description")
    price = data.get("price")
    discount = data.get("discount")
    stock = data.get("stock")
    image = data.get("image")
    category_id = data.get("category_id")
    status = data.get("status")

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            UPDATE products
            SET
                category_id = %s,
                name = %s,
                description = %s,
                price = %s,
                discount = %s,
                stock = %s,
                image = %s,
                status = %s
            WHERE id = %s
            """,
            (
                category_id,
                name,
                description,
                price,
                discount,
                stock,
                image,
                status,
                product_id
            )
        )

        connection.commit()

        if cursor.rowcount == 0:
            return jsonify({
                "status": "error",
                "message": "Product not found"
            }), 404

        return jsonify({
            "status": "success",
            "message": "Product updated successfully"
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


# DELETE product
@products_bp.route("/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            UPDATE products
            SET status = 'inactive'
            WHERE id = %s
            """,
            (product_id,)
        )

        connection.commit()

        if cursor.rowcount == 0:
            return jsonify({
                "status": "error",
                "message": "Product not found"
            }), 404

        return jsonify({
            "status": "success",
            "message": "Product deleted successfully"
        })

    finally:
        cursor.close()
        connection.close()