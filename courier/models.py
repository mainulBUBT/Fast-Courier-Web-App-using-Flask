from datetime import datetime
from email.policy import default
from courier import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


@login_manager.user_loader
def user_loader(id):
    return User.query.get(id)


class User(db.Model,UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    mobile_number = db.Column(db.String(14))
    password_hash = db.Column(db.String(128))
    profile_image = db.Column(db.String(20), nullable=False, default="default_profile.png")
    join_date = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    roles =  db.Column(db.String(128))

    delivery_info = db.relationship('DeliveryInfo', backref='users', lazy=True)
    parcels = db.relationship('Parcel', backref='users', lazy=True)

    def __init__(self, email, username, mobile_number, password):
        self.email = email
        self.username = username
        self.mobile_number = mobile_number
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def change_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def __str__(self):
        return f'username: {self.username}'

    

class Merchant(db.Model):
    __tablename__ = "merchant"

    id = db.Column(db.Integer, primary_key=True)
    # profile_image = db.Column(
    #     db.String(20), nullable=False, default="default_profile.png")
    # email = db.Column(db.String(64), unique=True, index=True)
    # username = db.Column(db.String(64), unique=True, index=True)
    merchant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    pickup_address = db.Column(db.String(100))
    balance = db.Column(db.String(100))
    due_chare = db.Column(db.String(100))
    bkash_number = db.Column(db.String(11))
    bank_number = db.Column(db.String(40))
    # password_hash = db.Column(db.String(128))
    # join_date = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    
    # delivery_info = db.relationship('DeliveryInfo', backref='merchant', lazy=True)
    # parcels = db.relationship('Parcel', backref='merchant', lazy=True)

    # def __init__(self, email, username, password):
    #     self.email = email
    #     self.username = username
    #     self.password_hash = generate_password_hash(password)

    # def check_password(self, password):
    #     return check_password_hash(self.password_hash, password)

    # def __str__(self):
    #     return f'username: {self.username}'

class DeliveryInfo(db.Model):
    __tablename__ = "delivery_info"

    id = db.Column(db.Integer, primary_key=True)
    receiver_name = db.Column(db.String(100))
    delivery_area = db.Column(db.String(100))
    collectable_amount = db.Column(db.Integer)
    receiver_number = db.Column(db.String(50))
    receiver_address = db.Column(db.String(100))
    book_date = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    merchant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    parcels = db.relationship('Parcel', backref='delivery_info', lazy=True)


    def __init__(self, receiver_name,delivery_area, collectable_amount, receiver_number, receiver_address, merchant_id):
        self.receiver_name = receiver_name
        self.delivery_area = delivery_area
        self.collectable_amount = collectable_amount
        self.receiver_number = receiver_number
        self.receiver_address = receiver_address
        self.merchant_id = merchant_id
    
    def __repr__(self):
        return f"Delivery ID: {self.id} --- Name: {self.receiver_name} --- Date: {self.book_date} --- Area: {self.delivery_area} --- Amount: {self.collectable_amount} --- Number: {self.receiver_number} --- Address: {self.receiver_address}"

class Parcel(db.Model):
    __tablename__ = "parcel"

    deliveries  = db.relationship(DeliveryInfo)
    id = db.Column(db.Integer, primary_key=True)
    merchant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    delivery_id = db.Column(db.Integer, db.ForeignKey('delivery_info.id'), nullable=False)

    delivery_man = db.Column(db.String(50), default= 'Not Assigned', nullable=False)
    parcel_status = db.Column(db.String(50), default= 'Not pickup yet', nullable=False)
    charge = db.Column(db.String(50))
    due_charge = db.Column(db.String(50))
    user_balance = db.Column(db.String(50))
    pay_status = db.Column(db.String(50), default= 0, nullable=False)
    pay_method = db.Column(db.String(50), default= 0, nullable=False)
    parcel_date = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.utcnow)

    def __init__(self, merchant_id,delivery_id, parcel_status, charge, due_charge, user_balance):
        self.merchant_id = merchant_id
        self.delivery_id = delivery_id
        self.parcel_status = parcel_status
        self.charge = charge
        self.due_charge = due_charge
        self.user_balance = user_balance
        

    def __repr__(self):
        return f"Parcel ID: {self.id} --- Date: {self.parcel_date} --- Status: {self.parcel_status}"