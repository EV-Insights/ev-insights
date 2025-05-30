import os
import logging
from abc import abstractmethod
from src.interfaces.interface import init_interface
from datetime import datetime
from pprint import pprint

SERVICES = {"analysis", "forecast", "ingestion", "admin"}


class Service:
    def __init__(self, name, output_dir, interfaces):
        self.name = name
        self.output_dir = output_dir
        if not os.path.isdir(self.output_dir):
            os.makedirs(self.output_dir)
        self.logger = logging.getLogger('service')
        self.logger.info("Initialized " + self.name)
        self.interfaces = interfaces

        # Init interfaces
        self.input_interface = init_interface(config=interfaces['input'])
        self.output_interface = init_interface(config=interfaces['output'])
        if "mlflow" in interfaces.keys():
            self.mlflow_interface = init_interface(config=interfaces['mlflow'])
        else:
            self.mlflow_interface = None

        self.output = []
        return

    @abstractmethod
    def run(self):
        pass

    def close_service(self):
        self.input_interface.close_interface()
        self.output_interface.close_interface()
        if self.mlflow_interface:
            self.mlflow_interface.close_interface()
        return


def init_service(config):
    logger = logging.getLogger('init_service')
    service = None

    service_name = config["name"]

    if service_name in SERVICES:

        if service_name == 'analysis':
            from src.services.analysis_service import AnalysisService
            service = AnalysisService(name=config['name'],
                                      output_dir=config['output_dir'],
                                      interfaces=config['interfaces'],
                                      analysis=config['analysis'])

        elif service_name == 'forecast':
            from src.services.forecast_service import ForecastService
            service = ForecastService(name=config['name'],
                                      models_dir=config['models_dir'],
                                      output_dir=config['output_dir'],
                                      interfaces=config['interfaces'],
                                      forecast=config['forecast'])

        elif service_name == 'ingestion':
            from src.services.ingestion_service import IngestionService
            service = IngestionService(name=config['name'],
                                       output_dir=config['output_dir'],
                                       interfaces=config['interfaces'])

        elif service_name == 'admin':
            from src.services.admin_service import AdminService
            service = AdminService(name=config['name'],
                                   output_dir=config['output_dir'],
                                   interfaces=config['interfaces'],
                                   admin=config['admin'])

        else:
            logger.error('Wrong service')

    else:
        raise Exception('Service ' + service_name + ' does not exist. Check the config file. ' +
                        'Available services: ' + str(SERVICES))

    return service
