# local_digital_thread

Energy data within an organisation can often be distributed across different data endpoints with varied meta-data representation, which hinders seamless data collection and access from a single point for visualization and analytics. Moreover, there can be security and privacy constraints at data endpoints preventing data sharing and management. Thus, a local digital thread is required to aggregate the data from distributed data sources of an organization to standardize the data collection, representation, and preparation for further processing. 

This repository contains instructions on how to initialize and run the current POC of the Local Digital Thread application.

## Architecture 

The following Figure represents the architecture of the local digital thread:


![Architecture](https://github.com/nimbus-gateway/local_digital_thread/blob/main/docs/local%20digital%20thread%20architecture.png?raw=true)

## Running the source code

### Pre Requisites 
1. Python 3.X
2. Pip3
3. MySQL/Influx DB
4. Telegraf 1.29.1

### Data Transformation API

The application uses a REST API to interact with the data. Follow these commands to run the REST API:

```bash
cd app
flask run --host=0.0.0.0 --port=5000
```

To interact with the REST API, you can import the OPC UA.postman_collection.json collection into your Postman environment. This collection includes pre-configured requests for interacting with the API. The following are the steps:

1. Register Local Data Source: POST /datasource
2. Populate the Common Information Model(CIM): POST /mapping
3. Restart the OPC UA server


### Running OPC UA Server

The OPC UA server implements the CORDS' local digital thread's [CIM](https://github.com/nimbus-gateway/local_digital_thread/blob/main/docs/cim.PNG?raw=true) as an OPC UA representation. The local database schemas can then be mapped to OPC UA object instances defined through the Data Transformation API. 

```bash
python server.py
```

### Running Telegraf
Telegraf is used to collect data pushed to the OPC UA server. The data that is being collected are pushed to an Influx DB instance for persistence. So make sure that a Influx DB instance is running and a bucket name "Local Digital Thread" exists in the DB.

```bash
cd telegraf
telegraf --config telegraf.conf
```

### Client CLI for pushing data 
To insert data into the OPC UA server, you can run the OPC UA client. Use the following command:

```bash
python opc_client.py --opcua_reference_id="name_of_opc_ua_object"
```


## Running from the Docker

Make sure that databases are initialized. Follow the Step 1 in previous step.

### Step 1: Build and Run the Rest API

Change the `app/config/config.yaml` as requred.

```bash
cd app
docker build -t flask-app .
docker compose up
```

### Step 2: Build the OPC Server

Change the `app/config/config.yaml` as requred.

```bash
docker build -t opc_server .
docker compose up
```

