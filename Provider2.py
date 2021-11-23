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
        self.conn = psycopg2.connect(dbname='Lab2_Architecture', user='nick', password='06012002', host='localhost')

    def select_all_price(self):
        rows = []
        with self.conn.cursor() as cursor:
            cursor.execute('SELECT "Model"."modelName",  "ModelPlacing"."price" FROM "Model" JOIN "ModelPlacing" ON "ModelPlacing"."modelId" = "Model"."id"')
            rows = cursor.fetchall()
        return rows

    def select_all_desc(self, i):
        rows = []
        with self.conn.cursor() as cursor:
            cursor.execute('SELECT "Model"')
            rows = cursor.fetchall()
        return rows




class GetPrices(Resource):
    def get(self):
        db = SingletonDB()
        all_models = db.select_all_price()
        my_list = []
        for row in all_models:
            a = {"id": row[0], "modelId": row[1],  "price": row[2]}
            my_list.append(a)
        return my_list

class GetDescription(Resource):
    def get(self, id):
        db = SingletonDB()
        all_models = db.select_all_desc(id)
        my_list = []
        for row in all_models:
            a = {"model_id": row[0], "model_name": row[1], "desciption": row[2], "start_date": str(row[3]),
                 "end_date": str(row[4]), "delivery_type": row[5], "delivery_price": row[6],
                 "delivery_time": str(row[7]), "price": row[8], "sale_type": row[9], "lastname": row[10],
                 "email": row[11]}
            my_list.append(a)

        return my_list[0]


if __name__ == "__main__":
    app = Flask(__name__)
    api = Api(app)
    api.add_resource(GetPrices, '/price-list/')
    api.add_resource(GetDescription, '/details/<int:id>')
    app.run(port=5002, debug=True)
