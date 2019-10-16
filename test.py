from flask import Flask, request, jsonify, render_template
from flask_restful import Resource, Api
from sqlalchemy import create_engine

import mysql

db_connect = create_engine("mysql+mysqldb://anonymous@ensembldb.ensembl.org:3306/ensembl_website_97")

app = Flask(__name__)
api = Api(app)

field_config = ['display_label', 'location', 'stable_id', 'species']

class InvalidUsage(Exception):
    status_code = 400

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


@app.route('/')
def render_static():
    return render_template('index.html')


class genes(Resource):
    def get(self):
        wheres = []

        # Process lookup
        try:
            lookup = request.args['lookup']
        except InvalidUsage:
            return jsonify({405: "Invalid Query: it is mandatory to have a lookup value"})

        if len(lookup) < 3:
            return jsonify({405: "Invalid Query: please ensure your lookup is at least 3 characters"})
        elif not lookup.isalnum():
            return jsonify({200: "You connected fine, just are not allowed any non alpha-numeric characters"})
        wheres.append("display_label LIKE '"+lookup+"%%'")

        # Process Species
        try:
            species = request.args['species']
        except:
            pass
        else:
            if species is not None and len(species) > 0: # Deciding here that a blank species request will skip
                wheres.append("species like '"+species+"'")

        fields = ', '.join(field_config)
        where = ' AND '.join(wheres)
        conn = db_connect.connect()
        query = conn.execute("SELECT "+fields+" from gene_autocomplete WHERE "+where+";")
        result = {'data': [dict(zip(tuple (query.keys()), i)) for i in query.cursor]}
        return jsonify(result)


api.add_resource(genes, '/genes')

if __name__ == '__main__':
    app.run(port=5002)

