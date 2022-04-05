import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Dessert(SqlAlchemyBase):
    __tablename__ = 'desserts'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    image = sqlalchemy.Column(sqlalchemy.String, nullable=False)  # путь до картинки
    content = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    country = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    user = orm.relation('User')
