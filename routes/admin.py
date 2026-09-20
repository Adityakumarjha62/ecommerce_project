from flask import Blueprint, jsonify, request, session
import mysql.connector

from config import Config


# =========================================================
# ADMIN BLUEPRINT
# =========================================================

admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/api/admin"
)


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_db_connection():

    connection = mysql.connector.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DATABASE
    )

    return connection


# =========================================================
# CHECK ADMIN
# =========================================================

def check_admin():

    user_id = session.get("user_id")
    user_role = session.get("user_role")

    if not user_id:
        return False, "Please login first."

    if user_role != "admin":
        return False, "Admin access required."

    return True, "Admin verified."


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@admin_bp.route("/dashboard", methods=["GET"])
def dashboard():

    is_admin, message = check_admin()

    if not is_admin:
        return jsonify({
            "status": "error",
            "message": message
        }), 403

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT COUNT(*) AS total_users
            FROM users
        """)
        total_users = cursor.fetchone()["total_users"]


        cursor.execute("""
            SELECT COUNT(*) AS total_products
            FROM products
            WHERE status = 'active'
        """)
        total_products = cursor.fetchone()["total_products"]


        cursor.execute("""
            SELECT COUNT(*) AS total_orders
            FROM orders
        """)
        total_orders = cursor.fetchone()["total_orders"]


        cursor.execute("""
            SELECT
                COALESCE(SUM(total_amount), 0) AS total_sales
            FROM orders
            WHERE status != 'cancelled'
        """)
        total_sales = cursor.fetchone()["total_sales"]


        cursor.execute("""
            SELECT COUNT(*) AS pending_orders
            FROM orders
            WHERE status = 'pending'
        """)
        pending_orders = cursor.fetchone()["pending_orders"]


        cursor.execute("""
            SELECT COUNT(*) AS low_stock_products
            FROM products
            WHERE stock <= 10
            AND status = 'active'
        """)
        low_stock_products = cursor.fetchone()["low_stock_products"]


        return jsonify({
            "status": "success",

            "dashboard": {
                "total_users": total_users,
                "total_products": total_products,
                "total_orders": total_orders,
                "total_sales": float(total_sales or 0),
                "pending_orders": pending_orders,
                "low_stock_products": low_stock_products
            }
        })


    except mysql.connector.Error as error:

        return jsonify({
            "status": "error",
            "message": str(error)
        }), 500


    finally:

        cursor.close()
        connection.close()


# =========================================================
# GET ALL USERS
# =========================================================

@admin_bp.route("/users", methods=["GET"])
def get_users():

    is_admin, message = check_admin()

    if not is_admin:
        return jsonify({
            "status": "error",
            "message": message
        }), 403


    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                id,
                name,
                email,
                role
            FROM users
            ORDER BY id DESC
        """)

        users = cursor.fetchall()


        return jsonify({
            "status": "success",
            "users": users
        })


    except mysql.connector.Error as error:

        return jsonify({
            "status": "error",
            "message": str(error)
        }), 500


    finally:

        cursor.close()
        connection.close()


# =========================================================
# CHANGE USER ROLE
# =========================================================

@admin_bp.route(
    "/users/<int:user_id>/role",
    methods=["PUT"]
)
def update_user_role(user_id):

    is_admin, message = check_admin()

    if not is_admin:
        return jsonify({
            "status": "error",
            "message": message
        }), 403


    # Prevent changing your own role
    if user_id == session.get("user_id"):

        return jsonify({
            "status": "error",
            "message": "You cannot change your own role."
        }), 400


    data = request.get_json()


    if not data or "role" not in data:

        return jsonify({
            "status": "error",
            "message": "Role is required."
        }), 400


    new_role = data["role"]


    allowed_roles = [
        "user",
        "admin"
    ]


    if new_role not in allowed_roles:

        return jsonify({
            "status": "error",
            "message": "Invalid role."
        }), 400


    connection = get_db_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            UPDATE users
            SET role = %s
            WHERE id = %s
        """, (
            new_role,
            user_id
        ))


        if cursor.rowcount == 0:

            connection.rollback()

            return jsonify({
                "status": "error",
                "message": "User not found."
            }), 404


        connection.commit()


        return jsonify({
            "status": "success",
            "message": "User role updated successfully."
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


# =========================================================
# DELETE USER
# =========================================================

@admin_bp.route(
    "/users/<int:user_id>",
    methods=["DELETE"]
)
def delete_user(user_id):

    is_admin, message = check_admin()

    if not is_admin:
        return jsonify({
            "status": "error",
            "message": message
        }), 403


    # Prevent deleting yourself
    if user_id == session.get("user_id"):

        return jsonify({
            "status": "error",
            "message": "You cannot delete your own account."
        }), 400


    connection = get_db_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            DELETE FROM users
            WHERE id = %s
        """, (user_id,))


        if cursor.rowcount == 0:

            connection.rollback()

            return jsonify({
                "status": "error",
                "message": "User not found."
            }), 404


        connection.commit()


        return jsonify({
            "status": "success",
            "message": "User deleted successfully."
        })


    except mysql.connector.Error as error:

        connection.rollback()

        return jsonify({
            "status": "error",
            "message":
                "User cannot be deleted because existing orders or other records may depend on this user."
        }), 409


    finally:

        cursor.close()
        connection.close()


# =========================================================
# GET ALL ORDERS
# =========================================================

@admin_bp.route("/orders", methods=["GET"])
def get_orders():

    is_admin, message = check_admin()

    if not is_admin:
        return jsonify({
            "status": "error",
            "message": message
        }), 403


    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                o.id,
                o.user_id,

                u.name AS customer_name,
                u.email AS customer_email,

                o.total_amount,
                o.status,
                o.shipping_address,
                o.created_at

            FROM orders o

            LEFT JOIN users u
                ON o.user_id = u.id

            ORDER BY o.id DESC
        """)

        orders = cursor.fetchall()


        for order in orders:

            if order.get("created_at"):
                order["created_at"] = str(
                    order["created_at"]
                )

            if order.get("total_amount") is not None:
                order["total_amount"] = float(
                    order["total_amount"]
                )


        return jsonify({
            "status": "success",
            "orders": orders
        })


    except mysql.connector.Error as error:

        return jsonify({
            "status": "error",
            "message": str(error)
        }), 500


    finally:

        cursor.close()
        connection.close()


# =========================================================
# GET SINGLE ORDER
# =========================================================

@admin_bp.route(
    "/orders/<int:order_id>",
    methods=["GET"]
)
def get_order(order_id):

    is_admin, message = check_admin()

    if not is_admin:
        return jsonify({
            "status": "error",
            "message": message
        }), 403


    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                o.id,
                o.user_id,

                u.name AS customer_name,
                u.email AS customer_email,

                o.total_amount,
                o.status,
                o.shipping_address,
                o.created_at,
                o.updated_at

            FROM orders o

            LEFT JOIN users u
                ON o.user_id = u.id

            WHERE o.id = %s

        """, (order_id,))


        order = cursor.fetchone()


        if not order:

            return jsonify({
                "status": "error",
                "message": "Order not found."
            }), 404


        if order.get("created_at"):
            order["created_at"] = str(
                order["created_at"]
            )


        if order.get("updated_at"):
            order["updated_at"] = str(
                order["updated_at"]
            )


        if order.get("total_amount") is not None:
            order["total_amount"] = float(
                order["total_amount"]
            )


        return jsonify({
            "status": "success",
            "order": order
        })


    except mysql.connector.Error as error:

        return jsonify({
            "status": "error",
            "message": str(error)
        }), 500


    finally:

        cursor.close()
        connection.close()


# =========================================================
# UPDATE ORDER STATUS
# =========================================================

@admin_bp.route(
    "/orders/<int:order_id>/status",
    methods=["PUT"]
)
def update_order_status(order_id):

    is_admin, message = check_admin()

    if not is_admin:
        return jsonify({
            "status": "error",
            "message": message
        }), 403


    data = request.get_json()


    if not data or "status" not in data:

        return jsonify({
            "status": "error",
            "message": "Order status is required."
        }), 400


    new_status = data["status"]


    allowed_statuses = [
        "pending",
        "confirmed",
        "processing",
        "shipped",
        "delivered",
        "cancelled"
    ]


    if new_status not in allowed_statuses:

        return jsonify({
            "status": "error",
            "message": "Invalid order status."
        }), 400


    connection = get_db_connection()
    cursor = connection.cursor()


    try:

        cursor.execute("""
            UPDATE orders
            SET status = %s
            WHERE id = %s
        """, (
            new_status,
            order_id
        ))


        if cursor.rowcount == 0:

            connection.rollback()

            return jsonify({
                "status": "error",
                "message": "Order not found."
            }), 404


        connection.commit()


        return jsonify({
            "status": "success",
            "message":
                "Order status updated successfully."
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