# local_digital_thread

Energy data within an organisation can often be distributed across different data endpoints with varied meta-data representation which hinders seamless data collection and access from a single point for visualization and analytics. Moreover, there can be security and privacy constraints at data endpoints preventing data sharing and management. Thus, a local digital thread is required to aggregate the data from distributed data sources of an organization to standardize the data collection, representation, and preparation for further processing. 

This repository contains instructions on how to initialize and run the current POC of the Local Digital Thread application.

## Architecture 

The following Figure represents the architecture of the local digital thread:


![Architecture](https://github.com/tharindupr/local_digital_thread/blob/main/local%20digital%20thread%20architecture.png)

## Running the source code

### Step 1: Database Setup

To get started, you'll need to create the necessary database and populate it with data using the provided SQL script. Follow these steps:

- Locate the SQL script at `dbs/energymeters_block_13.sql`.
- Run the script to create and populate the database.

### Step 2: Running the REST API

The application uses a REST API to interact with the data. Follow these commands to run the REST API:

```bash
cd app
python app.py
```

### Step 3: Interacting with the REST API

To interact with the REST API, you can import the OPC UA.postman_collection.json collection into your Postman environment. This collection includes pre-configured requests for interacting with the API.


### Step 4: Run the OPC UA Server in seperate terminal

```bash
python server.py
```

### Step 5: OPC UA Client Data Insertion

To insert data into the OPC UA server, you can run the OPC UA client. Use the following command:

```bash
python opc_client-InfoModel.py
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

