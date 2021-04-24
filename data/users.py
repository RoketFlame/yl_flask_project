import datetime
import sqlalchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from functions import make_creation_date
from .db_session import SqlAlchemyBase
from sqlalchemy import orm
from sqlalchemy.orm import backref

subscribes_to_user = sqlalchemy.Table('subscribes_user_to_user', SqlAlchemyBase.metadata,
                                           sqlalchemy.Column('user_by_id', sqlalchemy.Integer,
                                                             sqlalchemy.ForeignKey('users.id')),
                                           sqlalchemy.Column('user_to_id', sqlalchemy.Integer,
                                                             sqlalchemy.ForeignKey('users.id'))
                                           )


class User(UserMixin, SqlAlchemyBase):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    about = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String,
                              index=True, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.String,
                                     default=make_creation_date(), nullable=True)

    avatar = sqlalchemy.Column(sqlalchemy.BLOB)

    subscribes_to_community = orm.relationship('Community', secondary='subscribes_user_to_community', backref=backref('subscribers', lazy='dynamic'))
    subscribers = orm.relationship('User',
                                   secondary='subscribes_user_to_user',
                                   primaryjoin=(subscribes_to_user.c.user_to_id == id),
                                   secondaryjoin=(subscribes_to_user.c.user_by_id == id),
                                   backref=backref('subscribes_to_user', lazy='dynamic'),
                                   lazy='dynamic'
                                   )
    news = orm.relation("News", back_populates='user')
    communities = orm.relation('Community', back_populates='creator')


    def __repr__(self):
        return f'{__class__.__name__} {self.id} {self.name} {self.email}'

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def make_json(self):
        result = {}
        result['id'] = self.id
        result['name'] = self.name
        return result
