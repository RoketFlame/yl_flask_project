import datetime
import sqlalchemy

from sqlalchemy import orm
from .db_session import SqlAlchemyBase

subscribes_to_community = sqlalchemy.Table('subscribes_user_to_community', SqlAlchemyBase.metadata,
                                           sqlalchemy.Column('user', sqlalchemy.Integer,
                                                             sqlalchemy.ForeignKey('users.id')),
                                           sqlalchemy.Column('community', sqlalchemy.Integer,
                                                             sqlalchemy.ForeignKey('communities.id'))
                                           )

class Community(SqlAlchemyBase):
    __tablename__ = 'communities'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)

    is_private = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
    creator_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))

    subscribers = orm.relation('User', secondary='subscribes_user_to_community', backref='community')
    creator = orm.relation('User')
    news = orm.relation("News", back_populates='community')

