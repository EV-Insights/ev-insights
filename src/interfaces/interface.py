import os
import logging
from abc import abstractmethod
from datetime import datetime
from pprint import pprint

INTERFACES = {"File", "MySql", "PostgreSql", "MLflow"}


class Interface:
    def __init__(self, name, type, output_dir):
        self.name = name
        self.type = type
        self.output_dir = output_dir
        if not os.path.isdir(self.output_dir):
            os.makedirs(self.output_dir)
        self.logger = logging.getLogger('interface')
        self.logger.info("Initialized " + self.name)
        return

    @abstractmethod
    def get_data(self, data_selection: dict):
        pass

    @abstractmethod
    def close_interface(self):
        pass

    @abstractmethod
    def init_db(self):
        pass

    @abstractmethod
    def delete_dataset(self, dataset_name):
        pass

    @abstractmethod
    def save_forecast_model(self, forecaster_name, results, algo, file_path_name):
        pass

    @abstractmethod
    def save_forecast_prediction(self, forecaster_name, actor, model, experiment_id, run_id, results, algo):
        pass


def init_interface(config):
    logger = logging.getLogger('init_interface')
    interface = None

    interface_name = config["name"]

    if interface_name in INTERFACES:
        if interface_name == 'File':
            from src.interfaces.file_interface import File
            interface = File(name=config['name'],
                             type=config['type'],
                             input_dir=config['input_dir'],
                             output_dir=config['output_dir'],
                             limit_rows=config['limit_rows'],
                             input_data_type=config["input_data_type"] if config['type'] == 'input' else None,
                             datasets_list=config['datasets_list'],
                             datasets_details_file=config['datasets_details_file']
                             )
        elif interface_name == 'MySql':
            from src.interfaces.mysql_interface import MySql
            interface = MySql(name=config['name'],
                              type=config['type'],
                              init_db=config['init_db'],
                              output_dir=config['output_dir'],
                              host=config['host'],
                              user=config['user'],
                              password=config['password'],
                              database=config['database'])
        elif interface_name == 'PostgreSql':
            from src.interfaces.postgresql_interface import PostgreSql
            interface = PostgreSql(name=config['name'],
                                   type=config['type'],
                                   output_dir=config['output_dir'],
                                   host=config['host'],
                                   port=config['port'],
                                   user=config['user'],
                                   password=config['password'],
                                   database=config['database'])
        elif interface_name == 'MLflow':
            from src.interfaces.mlflow_interface import MLflow
            interface = MLflow(name=config['name'],
                               type=config['type'],
                               output_dir=config['output_dir'],
                               mlflow_dir=config['mlflow_dir'],
                               host=config['host'],
                               port=config['port'],
                               user=config['user'],
                               password=config['password'],
                               bucket_name=config['bucket_name'],
                               init_storage=config['init_storage'])
        else:
            logger.error('Wrong interface')

    else:
        raise Exception('Interface ' + interface_name + ' does not exist. Check the config file. ' +
                        'Available interfaces: ' + str(INTERFACES))

    return interface
