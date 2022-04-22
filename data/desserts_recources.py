from . import db_session
from .users import User
from .desserts import Dessert
from .map import if_country, map_image

from flask import jsonify
from flask import url_for
from flask_restful import Resource, abort, reqparse

from shutil import copy

DEFAULT_DESSERT_AVATAR = "default_des_pic.jpg"

parser = reqparse.RequestParser()
parser.add_argument('title', required=True)
parser.add_argument('content', required=True)
parser.add_argument('user_id', required=True, type=int)
parser.add_argument('country', required=True, )


def abort_if_dessert_not_found(dessert_id):
    session = db_session.create_session()
    news = session.query(Dessert).get(dessert_id)
    if not news:
        abort(404, message=f"Dessert {dessert_id} not found")


class DessertResource(Resource):
    def get(self, dessert_id):
        abort_if_dessert_not_found(dessert_id)
        session = db_session.create_session()
        dessert = session.query(Dessert).get(dessert_id)
        return jsonify({'dessert': dessert.to_dict(
            only=('title', 'content', 'country', 'created_date', 'user.name'))})


class DessertListResource(Resource):
    def get(self):
        session = db_session.create_session()
        desserts = session.query(Dessert).all()
        return jsonify({'desserts': [item.to_dict(
            only=('title', 'content', 'user.name')) for item in desserts]})

    def post(self):
        # возможность создать дессерт реализована только для дессертов
        # без картинки - то есть при создании, у него будет defolt'ная фотография
        args = parser.parse_args()
        session = db_session.create_session()
        user = session.query(User).get(int(args['user_id']))
        if not user:
            abort(400, message=f"User {args['user_id']} does not exist")
        if not if_country(args['country']):
            abort(400, message=f"country '{args['country']}' does not exist")
        dessert = Dessert(
            title=args['title'],
            content=args['content'],
            user_id=args['user_id'],
            country=args['country'],
            user=user
        )

        session.add(dessert)
        session.commit()

        url = url_for('static', filename=f"img")[1:]
        copy(url + f"/{DEFAULT_DESSERT_AVATAR}", url + f"/dessert_photos/{dessert.id}.jpg")

        map_image(dessert.country, dessert.id)

        return jsonify({'success': 'OK'})
