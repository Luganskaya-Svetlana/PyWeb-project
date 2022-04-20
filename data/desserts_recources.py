from flask_restful import Resource, abort, reqparse
from . import db_session
from .desserts import Dessert
from flask import jsonify

parser = reqparse.RequestParser()
parser.add_argument('title', required=True)
parser.add_argument('content', required=True)
parser.add_argument('is_private', required=True, type=bool)
parser.add_argument('user_id', required=True, type=int)


def abort_if_news_not_found(news_id):
    session = db_session.create_session()
    news = session.query(Dessert).get(news_id)
    if not news:
        abort(404, message=f"News {news_id} not found")


class NewsResource(Resource):
    def get(self, news_id):
        abort_if_news_not_found(news_id)
        session = db_session.create_session()
        news = session.query(Dessert).get(news_id)
        return jsonify({'news': news.to_dict(
            only=('title', 'content', 'user_id', 'is_private'))})

    def delete(self, news_id):
        abort_if_news_not_found(news_id)
        session = db_session.create_session()
        news = session.query(Dessert).get(news_id)
        session.delete(news)
        session.commit()
        return jsonify({'success': 'OK'})


# по идее, не должен работать корректно - ведь при импорте вида
# from . import news_ersources.py код с инициализацией parser'а
# просто не выполнится
class NewsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        news = session.query(Dessert).all()
        return jsonify({'news': [item.to_dict(
            only=('title', 'content', 'user.name')) for item in news]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        news = Dessert(
            title=args['title'],
            content=args['content'],
            user_id=args['user_id'],
            is_private=args['is_private']
        )
        session.add(news)
        session.commit()
        return jsonify({'success': 'OK'})
