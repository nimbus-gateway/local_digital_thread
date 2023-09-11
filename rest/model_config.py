import json

class ModelConfig:
    def __init__(self, location):
        self.host = "localhost"
        self.port = 8080
        self.username = "user123"
        self.password = "secretpassword"
        self.mapping = []
        self.buildings = []

        self.load_mapping(location)

    def load_mapping(self, location):
        # Opening JSON file
        f = open(location)
        
        # returns JSON object as
        # a dictionary
        loaded_dic = json.load(f)

        self.mapping  = loaded_dic["Map"]
        self.buildings = loaded_dic["Buildings"]

    def add_mapping(self, new_map):
        f = open('mapping.json')

        self.mapping  = json.load(f)

        self.mapping['map'].append(new_map)

        try:
            json.dump(self.mapping, f)
            return True
        except Exception as e:
            print("An error occurred:", str(e))
            return False
        
    def get_buildings(self):
        return self.buildings
    
    def get_mapping(self):
        return self.mapping




