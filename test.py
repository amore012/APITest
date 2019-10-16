from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps

db_connect = create_engine("mysql://anonymous@ensembldb.ensembl.org/ensembl_website_97?port=3306")

app = Flask(__name__)
api = Api(app)


class InvalidUsage(Exception):
    status_code = 405

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


class ensembl_lookup(Resource):
    def get(self):
        conn = db_connect.connect()


if __name__ == '__main__':
    app.run()