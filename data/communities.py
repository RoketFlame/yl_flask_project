import datetime
import sqlalchemy

from sqlalchemy import orm
from .db_session import SqlAlchemyBase


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

    # association_table = sqlalchemy.Table(
    #     'subscribe_user_to_community',
    #     SqlAlchemyBase.metadata,
    #     sqlalchemy.Column('id_by_user', sqlalchemy.Integer,
    #                       sqlalchemy.ForeignKey('users.id')),
    #     sqlalchemy.Column('id_to_community', sqlalchemy.Integer,
    #                       sqlalchemy.ForeignKey('communities.id')))

    creator = orm.relation('User')
    news = orm.relation("News", back_populates='community')

