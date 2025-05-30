import os
import logging
import importlib
import pandas as pd
from pprint import pprint
from abc import abstractmethod
from src.interfaces.interface import Interface

# Retrieve the names of admin functions from the source, ensuring the list updates automatically whenever a new admin is added.
ADMIN = [s.replace(".py", "") for s in [f for f in os.listdir(os.path.dirname(os.path.abspath(__file__)))
                                           if ".py" in f and f not in ["admin.py", "_sample_admin.py", "__init__.py"]]]


class Admin:
    def __init__(self, id: int, name: str, info: str, enabled: bool, output_interface: Interface, output_dir: str, custom_params: dict):
        self.id = id
        self.name = name
        self.info = info
        self.enabled = enabled
        self.output_interface = output_interface
        self.output_dir = output_dir
        if not os.path.isdir(self.output_dir):
            os.makedirs(self.output_dir)
        self.custom_params = custom_params
        self.logger = logging.getLogger('admin')
        self.logger.info("Initialized " + self.name)
        self.results = {}
        self.output = []
        return

    @abstractmethod
    def run(self):
        pass


def import_class(module_path, class_name):
    """
    Import a class by its string name.

    Args:
        module_path (str): The path of the module containing the class.
        class_name (str): The name of the class to import.

    Returns:
        The imported class.
    """
    module = importlib.import_module(module_path)
    _class = getattr(module, class_name)
    return _class


def init_admin(config, output_interface=None):
    logger = logging.getLogger('init_admin')
    admin = None
    admin_module = config["name"]

    if config["name"] in ADMIN:
        if config["enabled"]:
            full_module_path = f"src.admin.{admin_module}"
            AdminClass = import_class(full_module_path, config["name"])
            admin = AdminClass(id=config['id'] if 'id' in config.keys() else 1,
                               name=config['name'],
                               info=config['info'],
                               enabled=config['enabled'],
                               output_interface=output_interface,
                               output_dir=config['output_dir'],
                               custom_params=config['custom_params'])
        else:
            logger.info('Admin ' + config["name"] + ' not enabled.')
    else:
        raise Exception('Admin ' + config["name"] + ' does not exist. Check the config file. ' +
                        'Available admin options: ' + str(ADMIN))

    return admin

