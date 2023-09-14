
import yaml

class Config:
    def __init__(self, config_file_path):
        self.config = self.load_config(config_file_path)

    def load_config(self, config_file_path):
        try:
            with open(config_file_path, 'r') as config_file:
                return yaml.safe_load(config_file)
        except FileNotFoundError:
            raise Exception(f"Config file '{config_file_path}' not found.")
        except yaml.YAMLError as e:
            raise Exception(f"Error parsing YAML config: {e}")

    def get_database_config(self):
        return self.config.get('database', {})

    def get_api_config(self):
        return self.config.get('api', {})

    def get_opc_config(self):
        return self.config.get('opc', {})
