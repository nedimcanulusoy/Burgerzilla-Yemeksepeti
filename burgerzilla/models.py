from burgerzilla import db
from datetime import datetime, timedelta, timezone
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    __table_args__ = {"schema": "bzschema"}
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(length=50), nullable=False)
    surname = db.Column(db.String(length=50), nullable=False)
    username = db.Column(db.String(length=50), unique=True, nullable=False)
    email = db.Column(db.String(length=50), unique=True, nullable=False)
    password_hash = db.Column(db.String(length=128), nullable=False)
    address = db.Column(db.String(length=120), nullable=False)
    order = db.relationship('Order', backref='c_order', lazy='dynamic')
    restaurant_id = db.Column(db.Integer, db.ForeignKey('bzschema.restaurant.id'))

    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute")

    @password.setter
    def password(self, password_hash):
        self.password_hash = generate_password_hash(password_hash)

    def verify_password(self, attempted_password):
        return check_password_hash(self.password_hash, attempted_password)


    def __repr__(self):
        return "<User(name={}, surname={}, username={}, email={}, address={}, restaurant_id={})>".format(
            self.name, self.surname, self.username, self.email,
            self.address, self.restaurant_id)


class Restaurant(db.Model):
    __table_args__ = {"schema": "bzschema"}
    __tablename__ = 'restaurant'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(length=50), unique=True, nullable=False)
    restaurant_menu = db.relationship('Menu', backref='menu', lazy='dynamic')
    restaurant_user = db.relationship('User', backref='user', lazy='dynamic')
    restaurant_order = db.relationship('Order', backref='r_order', lazy='dynamic')

    def __repr__(self):
        return "<Restaurant(id={}, name={})>".format(self.id, self.name)


class Menu(db.Model):
    __table_args__ = {"schema": "bzschema"}
    __tablename__ = 'menu'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(length=50), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(length=100), nullable=False)
    image = db.Column(db.String(length=120), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('bzschema.restaurant.id'))
    menuid = db.relationship('Order_Menu', backref='menuid', lazy='dynamic')

    def __repr__(self):
        return "<Menu(product={}, price={}, description={}, image={}, restaurant_menu={})>".format(self.product,
                                                                                                   self.price,
                                                                                                   self.description,
                                                                                                   self.image,
                                                                                                   self.restaurant_menu)


class Order(db.Model):
    __table_args__ = {"schema": "bzschema"}
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(length=50), nullable=False)
    timestamp = db.Column(db.String(length=25), default=datetime.utcnow().strftime('%m/%d/%Y - %H:%M:%S'))
    restaurant_id = db.Column(db.Integer, db.ForeignKey('bzschema.restaurant.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('bzschema.user.id'))
    orderid = db.relationship('Order_Menu', backref='orderid', lazy='dynamic')

    def __repr__(self):
        return "<Order(status={}, user_id={})>".format(self.status, self.user_id)


class Order_Menu(db.Model):
    __table_args__ = {"schema": "bzschema"}
    __tablename__ = 'order_menu'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer(), db.ForeignKey('bzschema.order.id'))
    menu_id = db.Column(db.Integer(), db.ForeignKey('bzschema.menu.id'))

    def __repr__(self):
        return "<Order_Menu(id={},order_id={},menu_id={})>".format(self.id, self.order_id, self.menu_id)

class TokenBlocklist(db.Model):
    __table_args__ = {"schema": "bzschema"}
    __tablename__ = 'token_block_list'
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)