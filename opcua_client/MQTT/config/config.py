
import yaml
import os

class Config:
    def __init__(self, config_file_path=os.getenv('DATA_SOURCE_MANAGER_CONFIG','config/config.yaml')):
        self.config = self.load_config(config_file_path)

    def load_config(self, config_file_path):
        try:
            with open(config_file_path, 'r') as config_file:
                config = yaml.safe_load(config_file)

            config['opc']['server_url'] = os.getenv('OPC_SERVER_URL', config['opc'].get('server_url'))
            config['opc']['namespace_uri'] = os.getenv('OPC_NAMESPACE_URI', config['opc'].get('namespace_uri'))
            config['opc']['namespace'] = os.getenv('OPC_NAMESPACE', config['opc'].get('namespace'))
            config['opc']['servername'] = os.getenv('OPC_SERVERNAME', config['opc'].get('servername'))
            config['opc']['reference_id'] = os.getenv('OPCUA_REFERENCE_ID', config['opc'].get('reference_id'))
            config['opc']['map'] = os.getenv('OPC_MAP', config['opc'].get('map'))

            config['data_source_manager']['host'] = os.getenv('DATA_SOURCE_MANAGER_HOST', config['data_source_manager'].get('host'))
            config['data_source_manager']['port'] = os.getenv('DATA_SOURCE_MANAGER_PORT', config['data_source_manager'].get('port'))

            config['logging']['level'] = os.getenv('LOGGING_LEVEL', config['logging'].get('level'))
            config['logging']['file'] = os.getenv('LOGGING_FILE', config['logging'].get('file'))

            return config
        
        except FileNotFoundError:
            raise Exception(f"Config file '{config_file_path}' not found.")
        except yaml.YAMLError as e:
            raise Exception(f"Error parsing YAML config: {e}")

    def get_config(self):
        return self.config
    



