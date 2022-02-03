from burgerzilla import db
from datetime import datetime


class Customer(db.Model):
    __table_args__ = {"schema": "bzschema"}
    __tablename__ = 'customer'
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(length=50), nullable=False)
    customer_surname = db.Column(db.String(length=50), nullable=False)
    customer_username = db.Column(db.String(length=50), unique=True, nullable=False)
    customer_email = db.Column(db.String(length=50), unique=True, nullable=False)
    customer_password = db.Column(db.String(length=50), nullable=False)
    customer_address = db.Column(db.String(length=120), nullable=False)
    customer_order = db.relationship('Order', backref='c_order', lazy='dynamic')

    # def __init__(self, customer_name, customer_surname, customer_username, customer_email, customer_password,
    #              customer_address):
    #     self.customer_name = customer_name
    #     self.customer_surname = customer_surname
    #     self.customer_username = customer_username
    #     self.customer_email = customer_email
    #     self.customer_password = customer_password
    #     self.customer_address = customer_address

    def __repr__(self):
        return "<Customer(customer_name={}, customer_surname={}, customer_username={}, customer_email={}, customer_address={})>".format(
            self.customer_name, self.customer_surname, self.customer_username, self.customer_email,
            self.customer_address)


class Owner(db.Model):
    __table_args__ = {"schema": "bzschema"}
    __tablename__ = 'owner'
    id = db.Column(db.Integer, primary_key=True)
    owner_name = db.Column(db.String(length=50), nullable=False)
    owner_surname = db.Column(db.String(length=50), nullable=False)
    owner_username = db.Column(db.String(length=50), unique=True, nullable=False)
    owner_email = db.Column(db.String(length=50), unique=True, nullable=False)
    owner_password = db.Column(db.String(length=50), nullable=False)
    owner_address = db.Column(db.String(length=120), nullable=False)
    restaurant_owner = db.relationship('Restaurant', backref='restaurant', lazy='dynamic')

    # def __init__(self, owner_name, owner_surname, owner_username, owner_email, owner_password, owner_address):
    #     self.owner_name = owner_name
    #     self.owner_surname = owner_surname
    #     self.owner_username = owner_username
    #     self.owner_email = owner_email
    #     self.owner_password = owner_password
    #     self.owner_address = owner_address

    def __repr__(self):
        return "<Owner(owner_name={}, owner_surname={}, owner_username={}, owner_email={}, owner_address={})>".format(
            self.owner_name, self.owner_surname, self.owner_username, self.owner_email, self.owner_address)


class Restaurant(db.Model):
    __table_args__ = {"schema": "bzschema"}
    __tablename__ = 'restaurant'
    id = db.Column(db.Integer, primary_key=True)
    restaurant_name = db.Column(db.String(length=50), unique=True, nullable=False)
    restaurant_menu = db.relationship('Menu', backref='menu', lazy='dynamic')
    restaurant_owner = db.Column(db.String(length=50), db.ForeignKey('bzschema.owner.owner_username'))
    restaurant_order = db.relationship('Order', backref='r_order', lazy='dynamic')

    # def __init__(self, restaurant_name):
    #     self.restaurant_name = restaurant_name

    def __repr__(self):
        return "<Restaurant(restaurant_name={})>".format(self.restaurant_name)


class Menu(db.Model):
    __table_args__ = {"schema": "bzschema"}
    __tablename__ = 'menu'
    id = db.Column(db.Integer, primary_key=True)
    product = db.Column(db.String(length=50), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(length=100), nullable=False)
    image = db.Column(db.String(length=120), nullable=False)
    restaurant_menu = db.Column(db.String(length=50), db.ForeignKey('bzschema.restaurant.restaurant_name'))

    # def __init__(self, product, price, description, image):
    #     self.product = product
    #     self.price = price
    #     self.description = description
    #     self.image = image

    def __repr__(self):
        return "<Menu(product={}, price={}, description={}, image={})>".format(self.product, self.price,
                                                                               self.description, self.image)


class Order(db.Model):
    __table_args__ = {"schema": "bzschema"}
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    order_name = db.Column(db.String(length=50), nullable=False)
    order_price = db.Column(db.Integer, nullable=False)
    order_quantity = db.Column(db.Integer, nullable=False)
    order_accept_cancel = db.Column(db.Integer, nullable=False, default=0)
    order_status = db.Column(db.String(length=50), nullable=False)
    order_timestamp = db.Column(db.String(length=25), default=datetime.utcnow().strftime('%m/%d/%Y - %H:%M:%S'))
    order_restaurant = db.Column(db.String(length=200), db.ForeignKey('bzschema.restaurant.restaurant_name'))
    order_customer = db.Column(db.String(length=200), db.ForeignKey('bzschema.customer.customer_username'))

    # def __init__(self, order_name, order_price, order_quantity, order_accept_cancel, order_status):
    #     self.order_name = order_name
    #     self.order_price = order_price
    #     self.order_quantity = order_quantity
    #     self.order_accept_cancel = order_accept_cancel
    #     self.order_status = order_status

    def __repr__(self):
        return "<Order(order_name={}, order_price={}, order_quantity={}, order_accept_cancel={}, order_status={})>".format(
            self.order_name, self.order_price, self.order_quantity, self.order_accept_cancel, self.order_status)
