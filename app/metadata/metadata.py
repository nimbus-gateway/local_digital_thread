import json
import os
from tinydb import Query
from db.db import TinyDBManager
import uuid

class MetaData:

    def __init__(self):
        """
        Initialize the MetaData with a TinyDBManager instance.
        
        :param db_manager: An instance of TinyDBManager for database operations.
        """
        self.db_manager = TinyDBManager()

        # Initialize data structures that will be loaded from the database
        self.mapping = []
        self.nodes = {}
        self.data_sources = {}


    def register_datasource(self, source):
        try:
            # Check if a data source with the same name already exists
            existing_source = self.db_manager.search('name', source.get('name'))
            print(existing_source)
            if existing_source:
                print("Data Source Exists")
                 # Update the existing record without changing the ID
                source['name'] = existing_source[0]['name']  # Preserve the existing ID
                source['type'] = 'datasource'
                existing_key = existing_source[0]['key']
                print('Existing Key')
                print(existing_key)
                self.db_manager.update(source, 'key', existing_key)  # Update the record

                return {
                    "status": "success",
                    "message": "Data source updated successfully.",
                    "key": existing_key
                }
            
            # Generate a unique ID for the new data source
            unique_id = uuid.uuid4()
            source['type'] = 'datasource'
            source['key'] = str(unique_id)

            # Insert the new data source into the database
            self.db_manager.insert(source)

            return {
                "status": "success",
                "message": "Data source registered successfully.",
                "key": source['key']
            }
        except Exception as e:
            print("An error occurred:", str(e))
            return {
                "status": "error",
                "message": f"An error occurred: {str(e)}"
            }
    
    def get_datasource(self, key):
        print(key)
        key_str = str(key)
        result = self.db_manager.search('key', key_str)
        if result:
            return result[0]
        return None
    

    def get_datasources(self):
        # Retrieve all data sources from the database
        datasources = self.db_manager.search('type', 'datasource')
        data_sources = datasources
        return data_sources


    def add_mapping(self, new_map):
        self.mapping = new_map

        try:
            # Update or insert the mapping in the database
            existing_mapping = self.db_manager.search('type', 'mapping')
            if existing_mapping:
                self.db_manager.update({'data': self.mapping}, 'type', 'mapping')
            else:
                self.db_manager.insert({'type': 'mapping', 'data': self.mapping})
            return {
                "status": "success",
                "message": "Mapping added successfully.",
            }
        except Exception as e:
            print("An error occurred:", str(e))
            return False
        
    def get_mapping(self):
        result = self.db_manager.search('type', 'mapping')
        if result:
            return result[0]
        return None
        
    def register_nodeid(self, reference_id, nodeid, mapping):
        mapping["nodeid"] = str(nodeid)
        mapping["MeasurementTimeStamp"] = {}
        mapping["Measurementvalue"] = {}
        mapping["MeasurementTimeStamp"]["nodeid"] = str(nodeid+1)
        mapping["Measurementvalue"]["nodeid"] = str(nodeid+2)
        mapping["type"] = 'node'
        mapping["reference_id"] = reference_id

        print("loging from mapping ", mapping["nodeid"])
        print("mapping ", mapping)
        

        self.db_manager.insert(mapping)
        return True
    

    def get_nodes(self):
        result = self.db_manager.search('type', 'node')
        if result:
            return result
        return None

    def remove_nodes(self):
        result = self.db_manager.delete('type', 'node')
        print(result)
        if result:
            return result
        return None


    def get_buildings(self):
        result = self.db_manager.search('type', 'mapping')
        if result:
            return result[0]['dataa']['Buildings']
        return None






