# ecommerce_project – Advanced E-Commerce Platform

ShopSphere is a full-stack e-commerce web application built using Python, Flask, MySQL, HTML, CSS and JavaScript.

The project provides a complete shopping workflow including user authentication, product browsing, shopping cart, checkout, wishlist, order management and an admin panel.

---

## 🚀 Features

### 👤 User Features

- User Registration
- User Login
- User Logout
- User Profile
- Product Browsing
- Product Details
- Product Search
- Category Filtering
- Shopping Cart
- Add Product to Cart
- Remove Product from Cart
- Stock Validation
- Wishlist
- Checkout
- Shipping Address
- Order Placement
- Order History
- Order Details

### 🛠️ Admin Features

- Admin Authentication
- Admin Dashboard
- Product Management
- Add Product
- Edit Product
- Delete Product
- User Management
- View Users
- Change User Role
- Delete Users
- Order Management
- View Orders
- View Order Details
- Update Order Status
- Sales Statistics
- Stock Monitoring

---

## 🛒 Order Status

Orders can have the following statuses:

- Pending
- Confirmed
- Processing
- Shipped
- Delivered
- Cancelled

---

## 💻 Technology Stack

### Frontend

- HTML5
- CSS3
- JavaScript

### Backend

- Python
- Flask

### Database

- MySQL

### API

- REST API

---

## 📁 Project Structure

```text
ShopSphere/
│
├── app.py
├── config.py
├── requirements.txt
├── README.md
│
├── routes/
│   ├── auth.py
│   ├── products.py
│   ├── cart.py
│   ├── orders.py
│   ├── admin.py
│   └── wishlist.py
│
├── templates/
│   ├── login.html
│   ├── register.html
│   ├── home.html
│   ├── dashboard.html
│   ├── cart.html
│   ├── checkout.html
│   ├── orders1.html
│   ├── order_details.html
│   ├── profile.html
│   ├── wishlist.html
│   ├── product_details.html
│   │
│   └── admin/
│       ├── products.html
│       ├── users.html
│       └── orders2.html
│
└── static/
    ├── css/
    ├── js/
    └── images/
        ├── Backpack.jpg
        ├── default.jpg
        ├── gaming_mouse.jpg
        ├── headphones.jpg
        ├── keyboard.jpg
        ├── laptop.jpg
        ├── mobile.jpg
        └── watch.jpg