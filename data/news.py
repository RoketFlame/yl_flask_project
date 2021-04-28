import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from functions import make_creation_date
from .db_session import SqlAlchemyBase


class News(SqlAlchemyBase):
    __tablename__ = 'news'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.String,
                                     default=make_creation_date())
    is_private = sqlalchemy.Column(sqlalchemy.Boolean, default=True)

    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    is_published_by_community = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    community_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('communities.id'),
                                     default=None, nullable=True)
    picture = sqlalchemy.Column(sqlalchemy.BLOB)

    user = orm.relation('User')
    community = orm.relation('Community')
    categories = orm.relation("Category",
                              secondary="association",
                              backref="news")

    def make_json(self):
        result = {}
        result['title'] = self.title
        result['content'] = self.content
        result['created_date'] = self.created_date
        result['user'] = self.user.make_json()
        return result