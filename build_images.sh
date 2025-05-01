#!/bin/bash

docker build app/ -t data_source_manager:latest

docker build opcua_server/ -t opcua_sever:latest

docker build opcua_client/MQTT -t opcua_client_mqtt:latest

