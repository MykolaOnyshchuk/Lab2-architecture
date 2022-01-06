from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from ObjectBuilder import Director, OwnObjectBuilder, Provider1ObjectBuilder, Provider2ObjectBuilder
from DB import SingletonDB
from ChainOfResp import *
from Facade import Facade


if __name__ == "__main__":
    app = Flask(__name__)
    api = Api(app)
    @app.route("/get_models/", methods=['GET', 'POST', 'DELETE', 'PUT'])
    def get_prod():
        postHandler = PostHandler()
        getHandler = GetHandler()
        deleteHandler = DeleteHandler()
        putHandler = PutHandler()
        postHandler.set_next(getHandler).set_next(deleteHandler).set_next(putHandler)
        return postHandler.handle(request.method)
    app.run(debug=True)
    SingletonDB().conn.close()
