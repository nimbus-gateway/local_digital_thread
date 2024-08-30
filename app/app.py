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
import docker

app = Flask(__name__)

config_instance = Config()
conf = config_instance.get_config()


print("Starting Data Source Manager API")

metadata = MetaData()


@app.route('/datasource', methods=['POST'])
def register_ds():
    data = request.get_json()

    print(data)
    status = metadata.register_datasource(data)

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
    
@app.route('/datasources', methods=['GET'])
def get_datasources():
    data_source = metadata.get_datasources()
    if data_source:
        return jsonify(data_source)
    else:
        return Response("", status=400, mimetype='application/json')



# End point to retreive schema
@app.route('/schema/<string:source>/<string:dbname>/<string:table>', methods=['GET'])
def get_schema(source, dbname, table):
    #connect to the sql database

    data_source = metadata.get_datasource(source)

    if data_source['connector'] == 'MySQL': 
        sql = MySQL()
        sql.connect_(dbname, conf['mysql']['host'],  conf['mysql']['username'],  conf['mysql']['password'])

        return sql.describe_db(table)
    
    elif data_source['connector'] == 'InFlux':
        influx = InFlux()
        status = influx.connect_(conf['influx']['org'], conf['influx']['host'], conf['influx']['port'], conf['influx']['token'])
    
        return influx.describe_db(dbname, table)

@app.route('/mapping', methods=['POST'])
def add_mapping():
    data = request.get_json()

    status = metadata.add_mapping(data)

    if status:
        return jsonify(status)
    else:
        return Response("", status=400, mimetype='application/json')
    

@app.route('/mapping', methods=['GET'])
def get_mapping():
    return metadata.get_mapping()

@app.route('/nodes', methods=['GET'])
def get_nodes():
    return jsonify(metadata.get_nodes())


@app.route('/addNode', methods=['POST'])
def registerNode():
    data = request.get_json()

    print("payload: ", data)
    result = metadata.register_nodeid(data['reference_id'], data['nodeid'], data['mapping'])

    if result:
        return jsonify(metadata.mapping)
    else:
        return Response("", status=400, mimetype='application/json')


@app.route('/removeNodes', methods=['DELETE'])
def removeNodes():
    try:
        # Clear all nodes
        status = metadata.remove_nodes()
        
        if status == None:
            return Response("", status=500, mimetype='application/json')
        # Optionally, you can also clear the mapping or other related data
        # metadata.mapping.clear()
        
        return jsonify({"message": "All nodes have been removed."}), 200
    except Exception as e:
        print("An error occurred:", str(e))
        return Response("", status=500, mimetype='application/json')


@app.route('/opcuaRestart', methods=['POST'])
def restart_container():

    client = docker.from_env()

    try:
        # Get the service name from the request data
        service_name = 'opcua_server'
        print("restarting opcua server...")
        print("service_name: opcua_server")
        if not service_name:
            return jsonify({"error": "Service name is required"}), 400

        print("finding the container...")
        # Find the container(s) by service name
        containers = client.containers.list(filters={"name": service_name})

        if not containers:
            return jsonify({"error": "No container found with the service name: {}".format(service_name)}), 404

        # Restart the containers
        for container in containers:
            container.restart()

        return jsonify({"message": "Container(s) with service name '{}' restarted successfully".format(service_name)}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    print("Hellow This is a new container")
    app.run(host="0.0.0.0", port="5000", debug=True)