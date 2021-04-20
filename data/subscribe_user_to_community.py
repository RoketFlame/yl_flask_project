import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class SubscribesUserToCommunities(SqlAlchemyBase):
    __tablename__ = 'subscribes_user_to_communities'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey('users.id'))

    community_id = sqlalchemy.Column(sqlalchemy.Integer,
                                     sqlalchemy.ForeignKey('communities.id'))
    user = orm.relation('User')
    community = orm.relation('Community')