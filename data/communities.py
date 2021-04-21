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
    creator_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))

    creator = orm.relation('User')
    news = orm.relation("News", back_populates='community')

    def make_json(self):
        result = {}
        result['id'] = self.id
        result['creator'] = self.creator.make_json()
        result['name'] = self.name
        result['description'] = self.description
        result['created_date'] = self.created_date
        result['news'] = [news.make_json() for news in self.news]
        return result