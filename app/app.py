import sys
sys.path.append("..")

from flask import Flask, request, jsonify, Response
import mysql
from mysql import connector
import json
from connectors.mysql_connector import MySQLConnector
from mapping.mapping import Mapping
from config.config import Config

app = Flask(__name__)

config_instance = Config("config/config.yaml")
opc_config = config_instance.get_opc_config()
db_config = config_instance.get_database_config()

print("Starting REST Server")
# print(opc_config)

mapping = Mapping(opc_config['map'])


# End point to retreive schema
@app.route('/schema/<string:dbname>', methods=['GET'])
def get_schema(dbname):
    #connect to the sql database

    sql = MySQLConnector(dbname, db_config['host'], db_config['username'], db_config['password'])

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

@app.route('/registerNode', methods=['POST'])
def registerNode():
    data = request.get_json()

    result = mapping.register_nodeid(data['nodeid'], data['mapping'])
    mapping.reload_mapping()

    if result:
        return jsonify(mapping.mapping)
    else:
        return Response("", status=400, mimetype='application/json')





if __name__ == '__main__':
    app.run(debug=True)