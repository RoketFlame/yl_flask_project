import datetime
import sqlalchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class User(UserMixin, SqlAlchemyBase):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    about = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String,
                              index=True, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now, nullable=True)

    avatar = sqlalchemy.Column(sqlalchemy.BLOB)

    news = orm.relation("News", back_populates='user')
    communities = orm.relation('Community', back_populates='creator')

    # subscribe_user_to_user = sqlalchemy.Table(
    #     'subscribe_user_to_user',
    #     SqlAlchemyBase.metadata,
    #     sqlalchemy.Column('id_by_user', sqlalchemy.Integer,
    #                       sqlalchemy.ForeignKey('users.id')),
    #     sqlalchemy.Column('id_to_user', sqlalchemy.Integer,
    #                       sqlalchemy.ForeignKey('users.id'))
    # )

    def __repr__(self):
        return f'{__class__.__name__} {self.id} {self.name} {self.email}'

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    # def is_subscribe_to_user(self, id_to_user):
    #     return id_to_user in [user.to_user.id for user in self.user_subscribes]

    # def is_subscribe_to_community(self, id_to_community):
    #     return id_to_community in [community.to_community.id for community in self.community_subscribes]