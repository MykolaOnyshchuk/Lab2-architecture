from flask import Flask
from flask_restful import Resource, Api, reqparse
import psycopg2
import copy
from SpecificationFilter import PageNumber, MaximalPrice, MinimalPrice, Payment


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

    def select_filtered_values(self):
        rows = []
        with self.conn.cursor() as cursor:
            cursor.execute('SELECT "Model"."id", "Model"."modelName", "Model"."modelText", "ModelOrder"."designDescription", "User"."firstName", "User"."lastName", "User"."email", "User"."phoneNumber" FROM "Model" JOIN "ModelOrder" ON "Model"."id" = "ModelOrder"."modelId" JOIN "User" ON "modelOrder"."clientId" = "User"."id"')
            rows = cursor.fetchall()
        return rows


class Models(Resource):
    def get(self):
        db = SingletonDB()
        all_products = db.select_filtered_values()
        my_list = []
        for row in all_products:
            a = {"id": row[0], "modelName": row[1], "modelText": row[2], "designDescription": str(row[3]), "firstName": str(row[4]), "lastName": row[5], "email": row[6], "phoneNumber": str(row[7])}
            my_list.append(a)
        all_products.clear()

        product_filter = PageNumber() & MaximalPrice() & MinimalPrice() & Payment()
        products = []
        for i in my_list:
            print(i)
            if product_filter.filtering_value_is_satisfied(i):
                products.append(i)
        return products


if __name__ == "__main__":
    app = Flask(__name__)
    api = Api(app)
    api.add_resource(Models, '/search/')
    app.run(port=5001, debug=True)
