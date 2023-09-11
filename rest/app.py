from flask import Flask, request, jsonify, Response
import mysql
from mysql import connector
import json
from model_config import ModelConfig
from connectors.mysql_connector import MySQLConnector
from mapping.mapping import Mapping

app = Flask(__name__)


mapping = Mapping('./mapping/mapping.json')


# End point to retreive schema
@app.route('/schema/<string:dbname>', methods=['GET'])
def get_schema(dbname):
    #connect to the sql database

    sql = MySQLConnector(dbname)

    return sql.describe_db()
   


@app.route('/addMapping', methods=['POST'])
def add_mapping():
    data = request.get_json()

    status = mapping.add_mapping(data)

    if status:
        return jsonify(mapping.mapping)
    else:
        return Response("", status=400, mimetype='application/json')
    

@app.route('/getMapping', methods=['GET'])
def get_mapping():
    mapping.reload_mapping()
    return mapping.get_mapping()




if __name__ == '__main__':
    app.run(debug=True)