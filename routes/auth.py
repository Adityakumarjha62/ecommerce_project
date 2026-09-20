from flask import Blueprint, request, jsonify, session
import mysql.connector

from config import Config
from models.user import hash_password, verify_password


# ==========================================
# AUTH BLUEPRINT
# ==========================================

auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/api/auth"
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
# REGISTER
# ==========================================

@auth_bp.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    if not data:

        return jsonify({
            "status": "error",
            "message": "Request data is required"
        }), 400


    name = data.get("name")
    email = data.get("email")
    password = data.get("password")


    # Validation

    if not name or not email or not password:

        return jsonify({
            "status": "error",
            "message": "Name, email and password are required"
        }), 400


    if len(password) < 6:

        return jsonify({
            "status": "error",
            "message": "Password must be at least 6 characters"
        }), 400


    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)


    try:

        # Check existing user

        cursor.execute(
            """
            SELECT id
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        existing_user = cursor.fetchone()


        if existing_user:

            return jsonify({
                "status": "error",
                "message": "Email already registered"
            }), 409


        # Hash password

        hashed_password = hash_password(password)


        # Insert user

        cursor.execute(
            """
            INSERT INTO users
            (name, email, password)
            VALUES (%s, %s, %s)
            """,
            (
                name.strip(),
                email.strip(),
                hashed_password
            )
        )


        connection.commit()


        return jsonify({
            "status": "success",
            "message": "Registration successful"
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
# LOGIN
# ==========================================

@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.get_json()


    if not data:

        return jsonify({
            "status": "error",
            "message": "Request data is required"
        }), 400


    email = data.get("email")
    password = data.get("password")


    if not email or not password:

        return jsonify({
            "status": "error",
            "message": "Email and password are required"
        }), 400


    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)


    try:

        cursor.execute(
            """
            SELECT
                id,
                name,
                email,
                password,
                role
            FROM users
            WHERE email = %s
            """,
            (email.strip(),)
        )


        user = cursor.fetchone()


        if not user:

            return jsonify({
                "status": "error",
                "message": "Invalid email or password"
            }), 401


        # Verify password

        if not verify_password(
            password,
            user["password"]
        ):

            return jsonify({
                "status": "error",
                "message": "Invalid email or password"
            }), 401


        # Create session

        session["user_id"] = user["id"]

        session["user_name"] = user["name"]

        session["user_email"] = user["email"]

        session["user_role"] = user["role"]


        return jsonify({

            "status": "success",

            "message": "Login successful",

            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "role": user["role"]
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



# ==========================================
# LOGOUT
# ==========================================

@auth_bp.route("/logout", methods=["POST"])
def logout():

    session.clear()


    return jsonify({

        "status": "success",

        "message": "Logout successful"

    })



# ==========================================
# GET MY PROFILE
# ==========================================

@auth_bp.route("/profile", methods=["GET"])
def get_profile():

    user_id = session.get("user_id")


    if not user_id:

        return jsonify({

            "status": "error",

            "message": "Please login first"

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
                name,
                email,
                role,
                created_at
            FROM users
            WHERE id = %s
            """,
            (user_id,)
        )


        user = cursor.fetchone()


        if not user:

            return jsonify({

                "status": "error",

                "message": "User not found"

            }), 404


        # Convert datetime to string

        if user["created_at"]:

            user["created_at"] = (
                user["created_at"]
                .strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            )


        return jsonify({

            "status": "success",

            "user": user

        })


    except mysql.connector.Error as error:

        return jsonify({

            "status": "error",

            "message": str(error)

        }), 500


    finally:

        cursor.close()

        connection.close()