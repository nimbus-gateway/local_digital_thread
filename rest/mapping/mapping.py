import json
import os

class Mapping:
    def __init__(self, location):

        self.mapping = []


        self.location = location


        f = open(self.location)
        
        # returns JSON object as
        # a dictionary
        loaded_dic = json.load(f)

        self.mapping  = loaded_dic

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
        
    def register_nodeid(self, nodeid, mapping):
        mapping["nodeid"] = str(nodeid)

        
        print("loging from mapping ", mapping["nodeid"])
        print("mapping ", mapping)
        print(self.mapping["Map"])

        self.mapping["Map"].append(mapping)

        print(self.mapping["Map"])
        try:
            with open(self.location, 'w') as json_file:
                json.dump(self.mapping, json_file)
          
                return True
        except Exception as e:
            print("An error occurred:", str(e))
            return False


        
    def get_buildings(self):
        return self.mapping['Buildings']
    
    def get_mapping(self):
        return self.mapping
    
    def get_datamap(self):
        return self.mapping['Map']





