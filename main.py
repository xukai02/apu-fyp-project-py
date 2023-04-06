from flask import Flask, Response, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
from azure.storage.blob import BlobServiceClient

import sqlite3

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
print(basedir)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir,'db.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir,'test_database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

connect_str='DefaultEndpointsProtocol=https;AccountName=fyptest;AccountKey=ayyZvGIYSC+XkNPlZxRAV1MK6XBaDiHOFurrDFhpJm2P/4w/qx3wlvTa3wffGSP84CxFPks/vfYc+AStYqLUxw==;EndpointSuffix=core.windows.net'
container_name='photos'

blob_service_client = BlobServiceClient.from_connection_string(connect_str)
try:
    container_client = blob_service_client.get_container_client(container_name)
    container_client.get_container_properties()
except Exception as ex:
    container_client = blob_service_client.create_container(container_name)

@app.route('/viewphoto')
def view_photo():
    return '''
    <h1>upload photo</h1>
    <form method="post" action="/uploadphotos"
        enctype="multipart/form-data">
        <input type="file" name="photo" multiple/>
        <input type="submit"/>
    </form>'''

@app.route('/displayphoto')
def display_photo():
    photo = []
    blob_list = container_client.list_blobs()
    for blob in blob_list:
        photo.append(blob.name)
        blob_client=container_client.get_blob_client(blob.name)
        url = blob_client.url
    return jsonify(photo)

@app.route("/display/<name>")
def display(name):
    blob_client = container_client.get_blob_client(name)
    stream = blob_client.download_blob().readall()
    print(stream[0:500])
    return Response(stream, mimetype="image/jpeg")


@app.route('/uploadphotos',methods=['POST'])
def upload_photos():
    filenames=""
    for file in request.files.getlist("photo"):
        filenames += file.filename + " "
        try:
            container_client.upload_blob(file.filename,file)
            filenames += file.filename + "<br/>"
        except Exception as ex:
            print(ex)
            print("Ignore duplicate files")
    return "Upload" + filenames

class TodoItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    is_executed = db.Column(db.Boolean)

    def __init__(self, name, is_executed):
        self.name = name
        self.is_executed = is_executed

    def to_dict(self):
        return {
            'id':self.id,
            'name':self.name,
            'is_executed': self.is_executed
        }


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    address = db.relationship('Address')
    # address = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            # 'address': self.address
        }
    

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'image': self.image,
            'user_id': self.user_id
        }
    
class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product = db.relationship('Product')
    quantity = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            'id':self.id,
            'user_id':self.user_id,
            'product_id':self.product_id,
            'product':self.product.to_dict(),
            'quantity':self.quantity
        }

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    address_id=db.Column(db.Integer,db.ForeignKey('address.id'),nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    products = db.relationship('Product', secondary='order_product')
    status = db.Column(db.String(25),nullable=False)

    def to_dict(self):
        return {
            'id':self.id,
            'user_id':self.user_id,
            'address_id':self.address_id,
            'total_price':self.total_price,
            'products':[{
                'id':product.id,
                'name': product.name,
                'description': product.description,
                'price': product.price,
                'image': product.image,
                'user_id': product.user_id,
                'quantity':order_product.quantity
            } for product, order_product in zip(self.products,OrderProduct.query.filter_by(order_id=self.id).all())],
            # 'products':[product.to_dict() for product in self.products],
            'status':self.status
        }

class OrderProduct(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

class Rate(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    user = db.relationship('User')
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'),nullable=False)
    rate = db.Column(db.Integer,nullable=False)
    review = db.Column(db.String(255),nullable=True)
    # file = db.Column(db.String(500),nullable=True) # image/video
    reply_id = db.Column(db.Integer,db.ForeignKey('reply.id'),nullable=True)
    reply = db.relationship('Reply')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user':self.user.to_dict(),
            'product_id': self.product_id,
            'rate':self.rate,
            'review':self.review,
            'reply_id':self.reply_id,
            'reply':self.reply.to_dict() if self.reply else None
        }

class Reply(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    reply = db.Column(db.String(255),nullable=False)
    # rate_id = db.Column(db.Integer,db.ForeignKey('rate.id'),nullable=False)

    def to_dict(self):
        return {
            'id':self.id,
            'reply':self.reply,
            # 'rate_id':self.rate_id
        }

class Address(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    unit_number = db.Column(db.String(50),nullable=False)
    street = db.Column(db.String(50),nullable=False)
    city = db.Column(db.String(50),nullable=False)
    postal_code = db.Column(db.String(5),nullable=False)
    state = db.Column(db.String(50),nullable=False)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)

    def to_dict(self):
        return {
            'id':self.id,
            'unit_number':self.unit_number,
            'street':self.street,
            'city':self.city,
            'postal_code':self.postal_code,
            'state':self.state,
            'user_id':self.user_id
        }

@app.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    data_address = data.get('address')
    if(User.query.filter_by(email=data['email']).all()):
        return jsonify("email exist")
    user = User(name=data['name'],email=data['email'],password=data['password'])
    db.session.add(user)
    db.session.commit()
    if(data_address):
        create_address(user.id,data_address)
    return jsonify(user.to_dict())

def create_address(user_id,address_data):
    address = Address(
        unit_number=address_data['unit_number'],
        street=address_data['street'],
        city=address_data['city'],
        postal_code=address_data['postal_code'],
        state=address_data['state'],
        user_id=user_id
        )
    db.session.add(address)
    db.session.commit()
    return address
    

@app.route('/address/add/<user_id>',methods=['POST'])
def add_address(user_id):
    data = request.get_json()
    address = create_address(user_id,data)
    return jsonify(address.to_dict())

@app.route('/address/view/<user_id>',methods=['GET'])
def view(user_id):
    addressList = Address.query.filter_by(user_id=user_id).all()
    return jsonify([address.to_dict() for address in addressList])

@app.route('/address/update/<id>',methods=['POST'])
def put(id):
    data = request.get_json()
    address = Address.query.get_or_404(id)
    address.unit_number = data['unit_number']
    address.street = data['street']
    address.city = data['city']
    address.postal_code = data['postal_code']
    address.state = data['state']
    db.session.commit()
    return jsonify(address.to_dict())

@app.route('/address/delete/<id>',methods=['DELETE','POST'])
def delete(id):
    address = Address.query.get_or_404(id)
    db.session.delete(address)
    db.session.commit()
    return '',204

@app.route('/product/view',methods=['GET'])
def product_view():
    products = Product.query.all()
    return jsonify([product.to_dict() for product in products])

@app.route('/product/search/<id>',methods=['GET'])
def product_search(id):
    product = Product.query.get_or_404(id)
    return jsonify(product.to_dict())

@app.route('/product/add/<user_id>',methods=["POST"])
def product_add(user_id):
    data = request.get_json()
    product = Product(
        name=data['name'],
        description=data['description'],
        price=data['price'],
        image=data['image'],
        user_id=user_id
    )
    db.session.add(product)
    db.session.commit()
    return jsonify(product.to_dict())

@app.route('/product/update/<id>',methods=['PUT','POST'])
def product_update(id):
    product = Product.query.get_or_404(id)
    data = request.get_json()
    product.name = data['name']
    product.description = data['description']
    product.price = data['price']
    product.image=data['image']
    db.session.commit()
    return jsonify(product.to_dict())

@app.route('/product/delete/<id>',methods=['DELETE','POST'])
def product_delete(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return '',204

@app.route('/order/view',methods=['GET'])
def order_view():
    orders = Order.query.all()
    return jsonify([order.to_dict() for order in orders])

@app.route('/order/search/<id>',methods=['GET'])
def order_search():
    order = Order.query.get_or_404(id)
    return jsonify(order.to_dict())

@app.route('/order/add/<user_id>',methods=['POST'])
def order_add(user_id):
    data = request.get_json()
    order = Order(
        user_id=user_id,
        address_id=data['address_id'],
        total_price=data['total_price'],
        status=data['status']
    )
    db.session.add(order)
    db.session.commit()
    orderproduct_add(order.id)
    return jsonify(order.to_dict())

def orderproduct_add(order_id):
    orderproducts = []
    data=request.get_json()
    orderproduct_data = data['order_product']
    for orderproduct in orderproduct_data:
        orderproducts.append(OrderProduct(
            order_id=order_id,
            product_id=orderproduct['product']['id'],
            quantity=orderproduct['quantity']
        ))
    db.session.add_all(orderproducts)
    db.session.commit()

@app.route('/order/update/<id>',methods=['PUT','POST'])
def order_update(id):
    order = Order.query.get_or_404(id)
    data = request.get_json()
    order.status = data['status']
    db.session.commit()
    return jsonify(order.to_dict())

@app.route('/order/delete/<id>',methods=['DELETE','POST'])
def order_delete(id):
    order = Order.query.get_or_404(id)
    order_products = OrderProduct.query.filter_by(order_id=order.id).all()
    db.session.delete(order)
    for order_product in order_products:
        db.session.delete(order_product)
    db.session.commit()
    return '',204

@app.route('/cart/view/<user_id>',methods=['GET'])
def cart_view(user_id):
    carts = Cart.query.filter_by(user_id=user_id).all()
    return jsonify([cart.to_dict() for cart in carts])

@app.route('/cart/search/<id>',methods=['GET'])
def cart_search(id):
    cart = Product.query.get_or_404(id)
    return jsonify(cart.to_dict())

@app.route('/cart/add/<user_id>',methods=['POST'])
def cart_add(user_id):
    data = request.get_json()
    cart = Cart.query.filter_by(user_id=user_id,product_id=data['product_id']).first()
    if(cart):
        cart.quantity = data['quantity']
    else:
        cart = Cart(
            user_id = user_id,
            product_id = data['product_id'],
            quantity = data['quantity']
        )
        db.session.add(cart)
    db.session.commit()
    return jsonify(cart.to_dict())

@app.route('/cart/update/<id>',methods=['PUT','POST'])
def cart_update(id):
    data = request.get_json()
    cart = Cart.query.get_or_404(id)
    cart.quantity = data['quantity']
    db.session.commit()
    return jsonify(cart.to_dict())

@app.route('/cart/delete/<id>',methods=['DELETE','POST'])
def cart_delete(id):
    cart = Cart.query.get_or_404(id)
    db.session.delete(cart)
    db.session.commit()
    return "",204

@app.route('/rate/view/<product_id>',methods=['GET'])
def rate_view(product_id):
    rateList = Rate.query.filter_by(product_id=product_id).all()
    return jsonify([rate.to_dict() for rate in rateList])

@app.route('/rate/search/<id>',methods=['GET'])
def rate_search(id):
    rate = Rate.query.get_or_404(id)
    return jsonify(rate.to_dict())

@app.route('/rate/add/<user_id>',methods=['POST'])
def rate_add(user_id):
    data = request.get_json()
    rate = Rate(
        user_id=user_id,
        product_id=data['product_id'],
        rate = data['rate'],
        review=data.get('review'),
    )
    db.session.add(rate)
    db.session.commit()
    return jsonify(rate.to_dict())

@app.route('/rate/update/<id>',methods=['PUT','POST'])
def rate_update(id):
    data=request.get_json()
    rate=Rate.query.get_or_404(id)
    rate.rate=data['rate']
    rate.review = data['review']
    db.session.commit()
    return jsonify(rate.to_dict())

@app.route('/rate/delete/<id>',methods=['DELETE','POST'])
def rate_delete(id):
    rate = Rate.query.get_or_404(id)
    if(rate.reply_id):
        reply = Reply.query.get_or_404(rate.reply_id)
        db.session.delete(reply)
    db.session.delete(rate)
    db.session.commit()
    return '', 204

@app.route('/reply/view/<rate_id>',methods=['GET'])
def reply_view(rate_id):
    reply = Rate.query.filter_by(id=rate_id).first().reply
    if(reply):
        return jsonify(reply.to_dict())
    else:
        return ''

@app.route('/reply/search/<id>',methods=['GET'])
def reply_search(id):
    reply = Reply.query.get_or_404(id)
    return jsonify(reply.to_dict())

@app.route('/reply/add/<rate_id>',methods=['POST'])
def reply_add(rate_id):
    rate = Rate.query.get_or_404(rate_id)
    data=request.get_json()
    if(rate.reply_id and rate.reply_id!=""):
        reply_update(rate.reply_id)
    else:
        reply = Reply(
            reply = data['reply']
        )
        db.session.add(reply)
        db.session.commit()
        rate.reply_id = reply.id
        db.session.commit()
    return jsonify(rate.to_dict())

@app.route('/reply/update/<id>',methods=['PUT','POST'])
def reply_update(id):
    data = request.get_json()
    reply = Reply.query.get_or_404(id)
    reply.reply = data['reply']
    db.session.commit()
    return jsonify(reply.to_dict())

@app.route('/reply/delete/<id>',methods=['DELETE','POST'])
def reply_delete(id):
    reply = Reply.query.get_or_404(id)
    db.session.delete(reply)
    rate = Rate.query.filter_by(reply_id=id).first()
    rate.reply_id = None
    db.session.commit()
    return '',204

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    user = User(name=data['name'], email=data['email'], password=data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201

@app.route("/",methods=['GET'])
def home():
    return jsonify({'msg':"Welcome"})

@app.route('/todo',methods=['POST'])
def add_todo():
    data=request.get_json()
    name = request.json['name']
    is_executed = request.json['is_executed']

    todo = TodoItem(name,is_executed)
    db.session.add(todo)
    db.session.commit()
    return jsonify(todo.to_dict()),201
    conn = sqlite3.connect('test_database.db')
    c=conn.cursor()
    c.execute('''
        INSERT INTO TodoSchema(name,is_executed) VALUES (?,?)
    ''',(name,is_executed))

    conn.commit()

    new_todo_item = TodoItem(name,is_executed)
    # db.session.add(new_todo_item)
    # db.session.commit()

    return todo_schema.jsonify(new_todo_item)


@app.route('/todo',methods=['GET'])
def get_todo():
    todos=TodoItem.query.all()
    return jsonify([todo.to_dict() for todo in todos])
    conn = sqlite3.connect('test_database.db')
    c=conn.cursor()
    c.execute('''SELECT * FROM TodoSchema''')
    return jsonify(c.fetchall())

@app.route('/todo/<id>',methods=['PUT','PATCH'])
def execute_todo(id):
    todo = TodoItem.query.get(id)
    db.session.commit()
    return jsonify(todo)
    conn = sqlite3.connect('test_database.db')
    c=conn.cursor()
    c.execute('''SELECT * FROM TodoSchema WHERE id=?''',(id))
    return jsonify(c.fetchall())


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True,port=5000)