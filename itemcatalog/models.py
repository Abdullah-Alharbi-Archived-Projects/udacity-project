from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, sessionmaker, backref
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from __main__ import engine, login_manager
from passlib.apps import custom_app_context as pwd_context
from flask_login import UserMixin

Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

# check these please
# about the login_manager.user_loader:
# https://flask-login.readthedocs.io/en/latest/#how-it-works
# about the UserMixin:
# https://flask-login.readthedocs.io/en/latest/#flask_login.UserMixin
# about dynamic relationship:
# https://docs.sqlalchemy.org/en/rel_1_2/orm/collections.html#dynamic-relationship-loaders
# sqlalchemy tutorial:
# https://docs.sqlalchemy.org/en/latest/orm/tutorial.html


@login_manager.user_loader
def load_user(user_id):
    return session.query(User).filter_by(id=user_id).first()


class User(Base, UserMixin):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(77), unique=True, nullable=False)
    avatar = Column(String(50), default="default.jpg",  nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    categories = relationship('Category', backref='author', lazy='dynamic')

    def hash_password(self, password):
        self.password = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password)

    def __repr__(self):
        return "User<'{}', '{}', '{}'>".format(self.username, self.email,
                                               self.avatar)

    @property
    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "avatar": self.avatar,
            "created_at": self.created_at
        }


class Category(Base):
    __tablename__ = "category"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    items = relationship('Item', backref='category', lazy='dynamic')

    def __repr__(self):
        return "Category<'{}', '{}', '{}'>".format(self.name, self.user_id,
                                                   self.id)

    @property
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "user_id": self.user_id,
            "created_at": self.created_at
        }


class Item(Base):
    __tablename__ = "item"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=False)
    category_id = Column(Integer, ForeignKey("category.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    items = relationship('Category', backref=backref('item', lazy='dynamic'))

    def __repr__(self):
        return "Item<'{}', '{}', '{}'>".format(self.name, self.created_at,
                                               self.id)

    @property
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category_id": self.category_id,
            "created_at": self.created_at
        }


# this will create the database
Base.metadata.create_all(engine)
