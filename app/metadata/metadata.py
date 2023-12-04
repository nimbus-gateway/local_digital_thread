import json
import os

class MetaData:
    def __init__(self, location):

        self.mapping = []
        self.nodes = {}
        self.data_sources = {}

        self.location = location

        f = open(self.location)
        
        # returns JSON object as
        # a dictionary
        loaded_dic = json.load(f)

        self.mapping  = loaded_dic

    def register_datasource(self, key, source):
        try:
            print(str(key))
            self.data_sources[str(key)] = source
            return self.data_sources[str(key)] 
        except Exception as e:
            print("An error occurred:", str(e))
            return False

    def get_datasource(self, key):
        print(key)
        key_str = str(key)
        return self.data_sources[key_str]

    def reload_mapping(self):
        f = open(self.location)
        
        # returns JSON object as
        # a dictionary
        loaded_dic = json.load(f)

        self.mapping  = loaded_dic


    def add_mapping(self, new_map):

        self.mapping = new_map

        try:
            with open(self.location, 'w') as json_file:
                json.dump(self.mapping, json_file)
          
                return True
        except Exception as e:
            print("An error occurred:", str(e))
            return False
        
    def register_nodeid(self, reference_id, nodeid, mapping):
        mapping["nodeid"] = str(nodeid)
        mapping["MeasurementTimeStamp"] = {}
        mapping["Measurementvalue"] = {}
        mapping["MeasurementTimeStamp"]["nodeid"] = str(nodeid+1)
        mapping["Measurementvalue"]["nodeid"] = str(nodeid+2)
        print("loging from mapping ", mapping["nodeid"])
        print("mapping ", mapping)


        self.nodes[reference_id] = mapping
        print(self.nodes)
        return True
        # try:
        #     with open(self.location, 'w') as json_file:
        #         json.dump(self.mapping, json_file)
          
        #         return True
        # except Exception as e:
        #     print("An error occurred:", str(e))
        #     return False


        
    def get_buildings(self):
        return self.mapping['Buildings']
    
    def get_mapping(self):
        return self.mapping
    
    # def get_datamap(self):
    #     return self.mapping['Map']
    
    def get_nodes(self):
        print(self.nodes)
        return self.nodes





