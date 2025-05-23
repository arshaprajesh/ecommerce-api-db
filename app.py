
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from flask_marshmallow import Marshmallow
from datetime import date
from typing import List
from marshmallow import ValidationError, fields
from sqlalchemy import select, delete




app = Flask(__name__) 
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:CK123indb#1@localhost/ecommerce_api'
app.config['SQLALCHEMY_ECHO'] = True  # Enable SQL echo

class Base(DeclarativeBase):
    pass 

db = SQLAlchemy(app, model_class=Base)
ma = Marshmallow(app)


#====================== MODELS ==============================================

class Customer(Base):
    __tablename__ = 'Customer'

   
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(225), nullable=False)
    email: Mapped[str] = mapped_column(db.String(225))
    address: Mapped[str] = mapped_column(db.String(225))
    
    orders: Mapped[List["Orders"]] = db.relationship(back_populates='customer') 


order_products = db.Table(
    "Order_Products",
    Base.metadata,
    db.Column('order_id', db.ForeignKey('orders.id')),
    db.Column('product_id', db.ForeignKey('products.id'))
)


class Orders(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key=True)
    order_date: Mapped[date] = mapped_column(db.Date, nullable=False)
   
    customer_id: Mapped[int] = mapped_column(db.ForeignKey('Customer.id'))
   
    customer: Mapped['Customer'] = db.relationship(back_populates='orders')
   
    products: Mapped[List['Products']] = db.relationship(secondary=order_products, back_populates="orders")

class Products(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_name: Mapped[str] = mapped_column(db.String(255), nullable=False )
    price: Mapped[float] = mapped_column(db.Float, nullable=False)

    orders: Mapped[List['Orders']] = db.relationship(secondary=order_products, back_populates="products")


with app.app_context():
#    db.drop_all() 
    db.create_all() 




#============================ SCHEMAS ==================================

class CustomerSchema(ma.SQLAlchemyAutoSchema): 
    class Meta:
        model = Customer

class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Products

class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Orders
        include_fk = True #Need this because Auto Schemas don't automatically recognize foreign keys (customer_id)


customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many= True)

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)


@app.route('/')
def home():
    return "Home"

#=============== API ROUTES: Customer CRUD==================

#Get all customers using a GET method
@app.route("/customers", methods=['GET'])
def get_customers():
    query = select(Customer)
    result = db.session.execute(query).scalars() #Exectute query, and convert row objects into scalar objects (python useable)
    customers = result.all() #packs objects into a list
    return customers_schema.jsonify(customers),200

#Get Specific customer using id GET method
@app.route("/customers/<int:id>", methods=['GET'])
def get_customer(id):
    
    query = select(Customer).where(Customer.id == id)
    result = db.session.execute(query).scalars().first() #first() grabs the first object return

    if result is None:
        return jsonify({"Error": "Customer not found"}), 404
    
    return customer_schema.jsonify(result),20

#Creating customers with POST request
@app.route("/customers", methods=["POST"])
def add_customer():

    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    new_customer = Customer(name=customer_data['name'], email=customer_data['email'], address=customer_data['address'])
    db.session.add(new_customer)
    db.session.commit()

    return jsonify({"Message": "New Customer added successfully",
                    "customer": customer_schema.dump(new_customer)}), 201

# Update a user by ID

@app.route('/customers/<int:id>', methods=['PUT'])
def update_customer(id):
    customer = db.session.get(Customer, id)

    if not customer:
        return jsonify({"message": "Invalid customer id"}), 400
    
    try:
        customer_data = customer_schema.load(request.json)
        print("customer data",customer_data)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    customer.name = customer_data['name']
    customer.email = customer_data['email']
    customer.address = customer_data['address']

    db.session.commit()
    return customer_schema.jsonify(customer), 200

#Delete a user by ID

@app.route('/customers/<int:id>', methods=['DELETE'])
def delete_customer(id):
    customer = db.session.get(Customer, id)

    if not customer:
        return jsonify({"message": "Invalid customer id"}), 400
    
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": f"successfully deleted customer {id}"}), 200

#=============== API ROUTES: Products CRUD==================

##Creating products with POST request

@app.route('/products', methods=['POST'])
def create_product():
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_product = Products(product_name=product_data['product_name'], price=product_data['price'])
    db.session.add(new_product)
    db.session.commit()

    return jsonify({"Messages": "New Product added!",
                    "product": product_schema.dump(new_product)}), 201
    
#Get all products using a GET method

@app.route("/products", methods=['GET'])
def get_products():
    query = select(Products)
    result = db.session.execute(query).scalars() #Exectute query, and convert row objects into scalar objects (python useable)
    products = result.all() #packs objects into a list
    return products_schema.jsonify(products)
    
#Get Specific product using GET method using id

@app.route("/products/<int:id>", methods=['GET'])
def get_product(id):
    
    query = select(Products).where(Products.id == id)
    result = db.session.execute(query).scalars().first() #first() grabs the first object return

    if result is None:
        return jsonify({"Error": "product not found"}), 404
    
    return product_schema.jsonify(result),20


# Update a product by ID

@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    product = db.session.get(Products, id)

    if not product:
        return jsonify({"message": "Invalid product id"}), 400
    
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    product.product_name = product_data['product_name']
    product.price = product_data['price']
   

    db.session.commit()
    return product_schema.jsonify(product), 200

#Delete a product by ID

@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = db.session.get(Products, id)

    if not product:
        return jsonify({"message": "Invalid product id"}), 400
    
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": f"succefully deleted product {id}"}), 200

#=============== API ROUTES: Order Operations ==================

#CREATE an ORDER
@app.route('/orders', methods=['POST'])
def add_order():
    try:
        order_data = order_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    # Retrieve the customer by its id.
    customer = db.session.get(Customer, order_data['customer_id'])
    
    # Check if the customer exists.
    if customer:
        new_order = Orders(order_date=order_data['order_date'], customer_id = order_data['customer_id'])

        db.session.add(new_order)
        db.session.commit()

        return jsonify({"Message": "New Order Placed!",
                        "order": order_schema.dump(new_order)}), 201
    else:
        return jsonify({"message": "Invalid customer id"}), 400
    
    
    
    #Get all order using a GET method

@app.route("/orders", methods=['GET'])
def get_orders():
    query = select(Orders)
    result = db.session.execute(query).scalars() #Exectute query, and convert row objects into scalar objects (python useable)
    orders = result.all() #packs objects into a list
    return orders_schema.jsonify(orders)
    
#Get Specific product using GET method using id

@app.route("/orders/<int:id>", methods=['GET'])
def get_order(id):
    
    query = select(Orders).where(Orders.id == id)
    result = db.session.execute(query).scalars().first() #first() grabs the first object return

    if result is None:
        return jsonify({"Error": "order not found"}), 404
    
    return order_schema.jsonify(result),20


#Delete a order by ID

@app.route('/orders/<int:id>', methods=['DELETE'])
def delete_ordder(id):
    order = db.session.get(Orders, id)

    if not order:
        return jsonify({"message": "Invalid order id"}), 400
    
    db.session.delete(order)
    db.session.commit()
    return jsonify({"message": f"succefully deleted order {id}"}), 200 


#==============================================================================
#ADD product ITEM TO ORDER
@app.route('/orders/<int:order_id>/add_product/<int:product_id>', methods=['PUT'])
def add_product(order_id, product_id):
    order = db.session.get(Orders, order_id) #can use .get when querying using Primary Key
    product = db.session.get(Products, product_id)

    if order and product: #check to see if both exist
        if product not in order.products: 
            order.products.append(product) 
            db.session.commit() 
            return jsonify({"Message": "Successfully added item to order."}), 200
        else:#Product is in order.products
            return jsonify({"Message": "Item is already included in this order."}), 400
    else:#order or product does not exist
        return jsonify({"Message": "Invalid order id or product id."}), 400


#REMOVE PRODUCT FROM AN ORDER
@app.route('/orders/<order_id>/remove_product/<product_id>', methods=['DELETE'])
def remove_product (order_id, product_id):
    order = db.session.get(Orders, order_id) 
    product = db.session.get(Products, product_id)
    if product not in order.products:
        return jsonify({"message": "Invalid product id"}), 400

    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": f"succefully deleted product {product_id} from {order_id}"}), 200



 #Get all orders for a customer
@app.route("/orders/customer/<customer_id>",methods=['GET']) 

def get_customer_order(customer_id): 

    customer=db.session.get(Customer,customer_id) 

    return orders_schema.jsonify(customer.orders), 200 

#Get all products for an order

@app.route('/orders/<int:order_id>/products', methods=['GET'])
def get_order_product(order_id):
    order = db.session.get(Orders, order_id)
    return products_schema.jsonify(order.products), 200 


if __name__ == '__main__':
    app.run(debug=True)