from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict
from DB import SingletonDB
import requests
from SpecificationFilter import MinimalPageNumber, MaximalPageNumber, MaximalPrice, MinimalPrice, Payment


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
            full_models.append(requests.get('http://127.0.0.1:5002/details/'+str(row["id"])).json())
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
            a = {"id": row[0], "pageNumber": str(row[1]),
                 "xCoord": str(row[2]), "yCoord": row[3], "width": row[4],
                 "height": str(row[5]), "price": row[6], "payment": row[7], "status": row[8],
                 "chosenByUser": row[9]}
            my_list.append(a)
        self._model.set(my_list)

    def filter(self) -> None:
        self._model.filter()


class Director:
    def __init__(self) -> None:
        self._builder = None

    @property
    def builder(self) -> ObjectBuilder:
        return self._builder

    @builder.setter
    def builder(self, builder: ObjectBuilder) -> None:
        self._builder = builder

    def build_all_models(self) -> None:
        self.builder.extract_from_source()
        self.builder.reformat()

    def build_filtered_model(self) -> None:
        self.builder.extract_from_source()
        self.builder.reformat()
        self.builder.filter()


class OwnModel():
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
            cursor.execute('SELECT "public.ModelPlacing"."id", "public.ModelPlacing"."pageNumber", "public.ModelPlacing"."xCoord", "public.ModelPlacing"."yCoord", "public.ModelPlacing"."width", "public.ModelPlacing"."height", "public.ModelPlacing"."price", "public.ModelPlacing"."payment", "public.ModelPlacing"."status", "public.ModelPlacing"."chosenByUser" FROM "public.ModelPlacing"')
            rows = cursor.fetchall()
        return rows

    def insert(self, args):
        with self.conn.cursor() as cursor:
            print(args)
            cursor.execute('''INSERT INTO "public.ModelPlacing" ("modelId", "pageNumber", "xCoord", "yCoord", "width", "height", "price", "payment", "status", "chosenByUser") VALUES(%s,%s,%s,%s,%s,%s,%s,%s,'%s',%s)'''%(str(args["modelId"]), str(args["pageNumber"]), str(args["xCoord"]), str(args["yCoord"]), str(args["width"]), str(args["height"]), str(args["price"]), str(args["payment"]), str(args["status"]), str(args["chosenByUser"])))
        self.conn.commit()

    def delete(self, id):
        with self.conn.cursor() as cursor:
            cursor.execute('DELETE FROM "public.ModelPlacing" WHERE "id"='+str(id))
        self.conn.commit()

    def update(self, args):
        query_str = 'UPDATE "public.ModelPlacing" SET '
        for key, value in args.items():
            if key != 'id' and value is not None:
                query_str += '"' + key + '"=' + "'" + str(value) + "',"
        query_str = query_str[0:-1]
        query_str += ' WHERE "id"=' + str(args["id"])
        with self.conn.cursor() as cursor:
            cursor.execute(query_str)
        self.conn.commit()

    def filter(self):
        model_filter = MinimalPageNumber() & MaximalPageNumber() & MaximalPrice() & MinimalPrice() & Payment()
        models = []
        for i in self.models:
            if model_filter.filtering_value_is_satisfied(i):
                models.append(i)
        self.models = models
