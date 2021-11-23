from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict
from DB import SingletonDB
import requests
from flask_restful import reqparse
from SpecificationFilter import PageNumber, MaximalPrice, MinimalPrice, Payment


class ObjectBuilder(ABC):
    @property
    @abstractmethod
    def model(self) -> None:
        pass

    @abstractmethod
    def extract_from_source(self) -> None:
        pass

    @abstractmethod
    def reformat(self) -> None:
        pass

    @abstractmethod
    def filter(self) -> None:
        pass


class Provider1ObjectBuilder(ObjectBuilder):
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self._model = OwnModel()

    @property
    def model(self) -> OwnModel:
        model = self._model
        self.reset()
        return model

    def extract_from_source(self) -> None:
        self._model.set(requests.get('http://127.0.0.1:5001/search/').json())

    def reformat(self) -> None:
        pass

    def filter(self) -> None:
        self._model.filter()


class Provider2ObjectBuilder(ObjectBuilder):
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self._model = OwnModel()

    @property
    def model(self) -> OwnModel:
        model = self._model
        self.reset()
        return model

    def extract_from_source(self) -> None:
        self._model.set(requests.get('http://127.0.0.1:5002/price-list/').json())

    def reformat(self) -> None:
        full_models = []
        for row in self._model.models:
            full_models.append(requests.get('http://127.0.0.1:5002/details/'+str(row["modelId"])).json())
        self._model.set(full_models)

    def filter(self) -> None:
        self._model.filter()


class OwnObjectBuilder(ObjectBuilder):
    def __init__(self) -> None:
        self.reset()
        self.db = SingletonDB()

    def reset(self) -> None:
        self._model = OwnModel()

    @property
    def model(self) -> OwnModel:
        model = self._model
        self.reset()
        return model

    def extract_from_source(self) -> None:
        self._model.set(self._model.select_all_db_data())

    def reformat(self) -> None:
        my_list = []
        for row in self.model.models:
            a = {"id": row[0], "modelId": row[1], "pageNumber": str(row[2]),
                 "xCoord": str(row[3]), "yCoord": row[4], "width": row[5],
                 "height": str(row[6]), "price": row[7], "payment": row[8], "status": row[9],
                 "chosenByUser": row[10]}
            my_list.append(a)
        self._model.set(my_list)

    def filter(self) -> None:
        self._model.filter()


class Director:
    def __init__(self) -> None:
        self._builder = None

    @property
    def builder(self) -> Builder:
        return self._builder

    @builder.setter
    def builder(self, builder: Builder) -> None:
        self._builder = builder

    def build_all_models(self) -> None:
        self.builder.extract_from_source()
        self.builder.reformat()

    def build_filtered_model(self) -> None:
        self.builder.extract_from_source()
        self.builder.reformat()
        self.builder.filter()


class OwnModel:
    def __init__(self):
        self.models = []
        self.conn = SingletonDB().conn

    def add(self, model: Dict[str, Any]):
        self.models.append(model)

    def join(self, another_model):
        self.models += another_model.models

    def drop(self, id):
        del self.models[id]

    def set(self, models):
        self.models = models

    def select_all_db_data(self):
        rows = []
        with self.conn.cursor() as cursor:
            cursor.execute('SELECT "ModelPlacing"."id", "ModelPlacing"."modelId", "ModelPlacing"."pageNumber", "ModelPlacing"."xCoord", "ModelPlacing"."yCoord", "ModelPlacing"."width", "ModelPlacing"."hight", "ModelPlacing"."price", "ModelPlacing"."payment"')
            rows = cursor.fetchall()
        return rows

    def insert(self, args):
        with self.conn.cursor() as cursor:
            cursor.execute('''INSERT INTO "ModelPlacing" ("id", "modelId", "pageNumber", "xCoord", "yCoord", "width", "height", "price", "payment") VALUES('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')'''%(args["id"], args["modelId"], str(args["pageNumber"]), str(args["xCoord"]), str(args["yCoord"]), str(args["width"]), str(args["height"]), str(args["price"]), str(args["payment"])))
        self.conn.commit()

    def delete(self, id):
        with self.conn.cursor() as cursor:
            cursor.execute('DELETE FROM "ModelPlacing" WHERE "modelId"='+str(id))
        self.conn.commit()

    def update(self, args):
        query_str = 'UPDATE "model" SET '
        for key, value in args.items():
            if key != 'modelId' and value is not None:
                query_str += '"' + key + '"=' + "'" + str(value) + "',"
        query_str = query_str[0:-1]
        query_str += ' WHERE "modelId"=' + str(args["modelId"])
        with self.conn.cursor() as cursor:
            cursor.execute(query_str)
        self.conn.commit()

    def filter(self):
        model_filter = PageNumber() & MaximalPrice() & MinimalPrice() & Payment()
        models = []
        for i in self.models:
            if model_filter.filtering_value_is_satisfied(i):
                models.append(i)
        self.models = models
