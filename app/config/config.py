
import yaml
import os

class Config:
    def __init__(self, config_file_path=os.getenv('DATA_SOURCE_MANAGER_CONFIG','config/config.yaml')):
        self.config = self.load_config(config_file_path)

    def load_config(self, config_file_path):
        try:
            with open(config_file_path, 'r') as config_file:
                config = yaml.safe_load(config_file)

            # Override config values with environment variables if available
            config['mysql']['host'] = os.getenv('DB_HOST', config['mysql'].get('host'))
            config['mysql']['port'] = int(os.getenv('DB_PORT', config['mysql'].get('port')))
            config['mysql']['dbname'] = os.getenv('DB_NAME', config['mysql'].get('dbname'))
            config['mysql']['username'] = os.getenv('DB_USERNAME', config['mysql'].get('username'))
            config['mysql']['password'] = os.getenv('DB_PASSWORD', config['mysql'].get('password'))

            config['influx']['host'] = os.getenv('INFLUX_HOST', config['influx'].get('host'))
            config['influx']['port'] = os.getenv('INFLUX_PORT', config['influx'].get('port'))
            config['influx']['token'] = os.getenv('INFLUX_TOKEN', config['influx'].get('token'))
            config['influx']['org'] = os.getenv('INFLUX_ORG', config['influx'].get('org'))


            config['logging']['level'] = os.getenv('LOGGING_LEVEL', config['logging'].get('level'))
            config['logging']['file'] = os.getenv('LOGGING_FILE', config['logging'].get('file'))

            return config
        
        except FileNotFoundError:
            raise Exception(f"Config file '{config_file_path}' not found.")
        except yaml.YAMLError as e:
            raise Exception(f"Error parsing YAML config: {e}")

    def get_config(self):
        return self.config


