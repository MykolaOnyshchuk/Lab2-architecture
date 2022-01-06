from flask import Flask
from flask_restful import Resource, Api, reqparse
import psycopg2
import copy


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class SingletonDB(metaclass=SingletonMeta):
    def __init__(self):
        self.conn = psycopg2.connect(dbname='architecture2', user='postgres', password='06012002', host='localhost')

    def select_all_price(self):
        rows = []
        with self.conn.cursor() as cursor:
            cursor.execute('SELECT "architecture2"."ModelPlacing"."id", "architecture2"."ModelPlacingPayment"."price", "architecture2"."ModelPlacingPayment"."payment" FROM "architecture2"."ModelPlacing" JOIN "architecture2"."ModelPlacingPayment" ON "architecture2"."ModelPlacing"."id" = "architecture2"."ModelPlacingPayment"."model_placing_id"')
            rows = cursor.fetchall()
        return rows

    def select_all_desc(self, i):
        rows = []
        with self.conn.cursor() as cursor:
            cursor.execute('SELECT "architecture2"."ModelPlacing"."id",  "architecture2"."ModelPlacing"."pageNumber", "architecture2"."ModelPlacing"."xCoord", "architecture2"."ModelPlacing"."yCoord", "architecture2"."ModelPlacing"."width", "architecture2"."ModelPlacing"."height", "architecture2"."ModelPlacingPayment"."price", "architecture2"."ModelPlacingPayment"."payment", "architecture2"."ModelPlacing"."status", "architecture2"."ModelPlacing"."chosenByUser" FROM "architecture2"."ModelPlacing" JOIN "architecture2"."ModelPlacingPayment" on "architecture2"."ModelPlacing"."id" = "architecture2"."ModelPlacingPayment"."model_placing_id"')
            rows = cursor.fetchall()
        return rows




class GetPrices(Resource):
    def get(self):
        db = SingletonDB()
        all_models = db.select_all_price()
        my_list = []
        for row in all_models:
            a = {"id": row[0], "price": row[1], "payment": row[2]}
            my_list.append(a)
        return my_list

class GetDescription(Resource):
    def get(self, id):
        db = SingletonDB()
        all_models = db.select_all_desc(id)
        my_list = []
        for row in all_models:
            a = {"id": row[0], "pageNumber": str(row[1]), "xCoord": str(row[2]), "yCoord": str(row[3]),
                 "width": str(row[4]), "height": str(row[5]), "price": str(row[6]),
                 "payment": str(row[7]), "status": row[8], "chosenByUser": str(row[9])
                 }
            my_list.append(a)

        return my_list[0]


if __name__ == "__main__":
    app = Flask(__name__)
    api = Api(app)
    api.add_resource(GetPrices, '/price-list/')
    api.add_resource(GetDescription, '/details/<int:id>')
    app.run(port=5002, debug=True)
