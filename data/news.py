import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class News(SqlAlchemyBase):
    __tablename__ = 'news'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    is_private = sqlalchemy.Column(sqlalchemy.Boolean, default=True)

    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))

    is_published_by_community = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    community_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('communities.id'),
                                     default=None, nullable=True)

    user = orm.relation('User')
    community = orm.relation('Community')
    categories = orm.relation("Category",
                              secondary="association",
                              backref="news")
