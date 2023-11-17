import sys
sys.path.append("..")

from flask import Flask, request, jsonify, Response
import mysql
from mysql import connector
import json
from connectors.MySQL import MySQL
from connectors.InFlux import InFlux
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

    print(data['id'])
    status = metadata.register_datasource(data['id'], data)

    if status:
        return jsonify(status)
    else:
        return Response("", status=400, mimetype='application/json')
    
@app.route('/datasource/<string:source>', methods=['GET'])
def get_ds(source):
    data_source = metadata.get_datasource(source)

    if data_source:
        return jsonify(data_source)
    else:
        return Response("", status=400, mimetype='application/json')



# End point to retreive schema
@app.route('/schema/<string:source>/<string:dbname>/<string:table>', methods=['GET'])
def get_schema(source, dbname, table):
    #connect to the sql database
    if 'mysql' in source: 
        sql = MySQL()
        sql.connect_(dbname, db_config['host'], db_config['username'], db_config['password'])

        return sql.describe_db()
    
    elif 'influx' in source:
        influx = InFlux()
        status = influx.connect_("mtu", "localhost", "8086", "6R9Hg8swLRMBSVn6swE6yqmXAhSdcHAZ_G73NjP6QhdQKUkYhZWEuRfP-WsDKg5A3aYSnpBzmcG4fkUEoxZeGQ==")
    
        return influx.describe_db(dbname, table)

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