from flask import jsonify
from flask_restful import abort, Resource, reqparse

from data import db_session
from data.news import News

parser = reqparse.RequestParser()
parser.add_argument('title', required=True)
parser.add_argument('content', required=True)
parser.add_argument('is_private', required=True, type=bool)
parser.add_argument('is_published_by_community', required=False, type=bool)
parser.add_argument('user_id', required=False, type=int)
parser.add_argument('community_id', required=False, type=int)


def abort_if_news_not_found(news_id):
    session = db_session.create_session()
    news = session.query(News).get(news_id)
    if not news:
        abort(404, message=f"News {news_id} not found")


class NewsResource(Resource):
    def get(self, news_id):
        abort_if_news_not_found(news_id)
        session = db_session.create_session()
        news = session.query(News).get(news_id)
        return jsonify({'news': news.to_dict(
            only=('title', 'content', 'user_id', 'is_private', 'is_published_by_community', 'community_id'))})

    def delete(self, news_id):
        abort_if_news_not_found(news_id)
        session = db_session.create_session()
        news = session.query(News).get(news_id)
        session.delete(news)
        session.commit()
        return jsonify({'success': 'OK'})


class NewsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        news = session.query(News).all()
        return jsonify({'news': [item.to_dict(
            only=('title', 'content', 'user.name')) for item in news]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        news = News()
        news.title = args['title']
        news.content = args['content']
        news.user_id = args['user_id']
        news.is_published_by_community = args['is_published_by_community']
        news.community_id = args['community_id']
        news.is_private = args['is_private']
        session.add(news)
        session.commit()
        return jsonify({'success': 'OK'})
