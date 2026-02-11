E‑Commerce API
A RESTful backend service built with Flask, SQLAlchemy, and MySQL, supporting full CRUD operations for Customers, Products, and Orders, including multi‑item order workflows.


+----------------+        1        M        +----------------+       M        M       +----------------+
|    Customer    |--------------------------|     Orders     |------------------------|    Products    |
+----------------+                           +----------------+                        +----------------+
| id (PK)        |                           | id (PK)        |                        | id (PK)        |
| name           |                           | order_date     |                        | product_name   |
| email          |                           | customer_id FK |                        | price          |
| address        |                           +----------------+                        +----------------+
+----------------+                                   |
                                                     |
                                                     |
                                          +----------------------+
                                          |   Order_Products     |
                                          +----------------------+
                                          | order_id (FK)        |
                                          | product_id (FK)      |
                                          +----------------------+

🚀 Features
Full CRUD operations for Customers, Products, and Orders
Many‑to‑many relationship between Orders and Products
Input validation using Marshmallow schemas
SQLAlchemy ORM with clean relational models
Add/remove products from orders
Error handling for invalid IDs and malformed requests
SQL echo logging for debugging
Modular, maintainable code structure

🛠️ Tech Stack
Backend: Flask, SQLAlchemy, Marshmallow
Database: MySQL
Language: Python
Tools: Postman, SQLAlchemy Core/ORM

📦 Installation & Setup

1. Clone the repository
git clone <your-repo-url>
cd ecommerce-api

2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows

3. Install dependencies
pip install -r requirements.txt

4. Configure your database
Update your MySQL connection string in app.config:
python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://<user>:<password>@localhost/ecommerce_api'

5. Run the application
python app.py

📘 API Endpoints
Customers
Method	Endpoint	Description

GET	/customers	Get all customers
GET	/customers/	Get a customer by ID
POST	/customers	Create a new customer
PUT	/customers/	Update a customer
DELETE	/customers/	Delete a customer

Products
Method	Endpoint	Description

GET	/products	Get all products
GET	/products/	Get a product by ID
POST	/products	Create a product
PUT	/products/	Update a product
DELETE	/products/	Delete a product

Orders
Method	Endpoint	Description

POST	/orders	Create an order
GET	/orders	Get all orders
GET	/orders/	Get an order by ID
DELETE	/orders/	Delete an order

Order Items
Method	Endpoint	Description

PUT	/orders//add_product/	Add product to order
DELETE	/orders//remove_product/	Remove product from order
GET	/orders//products	Get all products in an order
GET	/orders/customer/	Get all orders for a customer

📂 Project Structure
Code
ecommerce-api/
│── app.py
│── models/
│── schemas/
│── requirements.txt
│── README.md
