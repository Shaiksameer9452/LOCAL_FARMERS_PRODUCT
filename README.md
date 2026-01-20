#  Local Farmers Product Store  #

#  Project Overview

Local Farmers Product Store is a web-based e-commerce application that connects local farmers directly with customers. The platform allows farmers to add products, customers to browse and purchase fresh vegetables, and admins to manage and approve orders. The project is built using Flask, SQLite, HTML, CSS, and Jinja templates.

This system removes intermediaries and promotes fair pricing, transparency, and accessibility for local farmers.

---

# Features

# User Roles
The application supports three types of users:

# 1. Customer
- Register and login
- View available products with images
- Add products to cart
- Place orders
- View order history and order status

# 2. Farmer
- Login and access farmer dashboard
- Add products (images auto-assigned from master products)
- View orders related to their products

# 3. Admin
- Secure admin login
- View all customer orders
- Approve or cancel orders
- Manage order status

---

##  Application Flow

1. User registers and logs in
2. Customer browses products and adds them to cart
3. Customer places an order (status: pending)
4. Admin reviews and approves or cancels the order
5. Farmer and customer can view order status

---

##  Image Handling Logic

- Product images are stored only once as **master products**
- When a farmer adds a product, the system automatically assigns the image based on the product name
- No duplicate image uploads are required
- A default image is used if no match is found

---

# Database Structure (ERD Summary)

# Tables Used:
- **users** – stores user details and roles
- **products** – stores product details and images
- **cart** – stores temporary cart items
- **orders** – stores order summary
- **order_items** – stores individual items per order

---

# Technologies Used

- **Backend:** Python, Flask
- **Frontend:** HTML, CSS
- **Templating Engine:** Jinja2
- **Database:** SQLite
- **Authentication:** Session-based login
- **Security:** Password hashing using Werkzeug

---

# How to Run the Project

1. Clone the repository or download the source code
2. Install required packages:
   ```bash
   pip install flask

# my project repo
local_farmers_product_store/
│
├── app.py
├── store.db
├── README.md
│
├── templates/
│   ├── layout.html
│   ├── home.html
│   ├── login.html
│   ├── register.html
│   ├── products.html
│   ├── product_details.html
│   ├── cart.html
│   ├── my_orders.html
│   ├── farmer_dashboard.html
│   ├── farmer_orders.html
│   ├── admin_orders.html
│   └── admin_login.html
│
├── static/
│   ├── style.css
│   └── images/
│       └── *.jpg

# CS50 Compliance

Uses Flask framework

Implements CRUD operations

Uses a relational database

Includes user authentication and authorization

Demonstrates a real-world e-commerce workflow

Author

Sameer Shaik
CS50 Project