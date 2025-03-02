from datetime import datetime
from app.database import db
from sqlalchemy import func, Enum as SQLAlchemyEnum
from enum import Enum




class UserType(Enum):
    SUPERADMIN = 'SUPERADMIN'
    ADMIN = "ADMIN"
    USER='USER'


class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    phone_number = db.Column(db.String(50))
    user_type = db.Column(SQLAlchemyEnum(UserType, name='usertype'))
    is_active = db.Column(db.Boolean, default=True)
    is_visible = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())




class Color(db.Model):
    __tablename__ = 'colors'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    
    

class Item(db.Model):
    __tablename__ = 'items'
    
    id = db.Column(db.Integer, primary_key=True)
    # quantity = db.Column(db.Integer)
    price = db.Column(db.Float)
    name = db.Column(db.String)
    color_id = db.Column(db.Integer, db.ForeignKey('colors.id'))
    
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())



class ItemImage(db.Model):
    __tablename__ = 'item_images'
    
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'))
    url = db.Column(db.String)
    
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id= db.Column(db.Integer, db.ForeignKey('users.id'))
    quantity = db.Column(db.Integer)
    total = db.Column(db.Float)
    item = db.Column(db.String)
    color = db.Column(db.String)
    address = db.Column(db.String)
    size = db.Column(db.String)
    
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())