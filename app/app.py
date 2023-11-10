import sys
sys.path.append("..")

from flask import Flask, request, jsonify, Response
import mysql
from mysql import connector
import json
from connectors.MySQL import MySQL
from metadata.metadata import MetaData
from config.config import Config

app = Flask(__name__)

config_instance = Config("config/config.yaml")
opc_config = config_instance.get_opc_config()
db_config = config_instance.get_database_config()

print("Starting REST Server")
# print(opc_config)

metadata = MetaData(opc_config['map'])


@app.route('/datasource', methods=['POST'])
def register_ds():
    data = request.get_json()

    print(data)
    status = metadata.register_datasource("test", data)

    if status:
        return jsonify(status)
    else:
        return Response("", status=400, mimetype='application/json')
    
@app.route('/datasource/<string:source>', methods=['GET'])
def get_ds(source):
    data_source = metadata.get_datasource("test")

    if data_source:
        return jsonify(data_source)
    else:
        return Response("", status=400, mimetype='application/json')



# End point to retreive schema
@app.route('/schema/<string:source>/<string:dbname>', methods=['GET'])
def get_schema(source, dbname):
    #connect to the sql database

    sql = MySQL()
    sql.connect_(dbname, db_config['host'], db_config['username'], db_config['password'])

    return sql.describe_db()
   

@app.route('/mapping', methods=['POST'])
def add_mapping():
    data = request.get_json()

    status = metadata.add_mapping(data)

    if status:
        return jsonify(metadata.mapping)
    else:
        return Response("", status=400, mimetype='application/json')
    

@app.route('/mapping', methods=['GET'])
def get_mapping():
    metadata.reload_mapping()
    return metadata.get_mapping()

@app.route('/nodes', methods=['GET'])
def get_nodes():
    metadata.reload_mapping()
    return metadata.get_nodes()


@app.route('/addNode', methods=['POST'])
def registerNode():
    data = request.get_json()

    result = metadata.register_nodeid(data['nodeid'], data['mapping'])
    metadata.reload_mapping()

    if result:
        return jsonify(metadata.mapping)
    else:
        return Response("", status=400, mimetype='application/json')





if __name__ == '__main__':
    app.run(debug=True)