import os
import logging
import importlib
import pandas as pd
from pprint import pprint
from abc import abstractmethod
from src.interfaces.interface import Interface

# Retrieve the names of analyses from the source, ensuring the list updates automatically whenever a new analysis is added.
ANALYSIS = [s.replace(".py", "") for s in [f for f in os.listdir(os.path.dirname(os.path.abspath(__file__)))
                                           if ".py" in f and f not in ["analysis.py", "_sample_analysis.py", "__init__.py"]]]


class Analysis:
    def __init__(self, id: int, name: str, info: str, enabled: bool, full_custom_mode: bool, show_images: bool, save_images: bool,
                 save_results: bool, input_interface: Interface, output_interface: Interface, output_dir: str, data_selection: dict,
                 custom_params: dict):
        self.id = id
        self.name = name
        self.info = info
        self.enabled = enabled
        self.full_custom_mode = full_custom_mode
        self.show_images = show_images
        self.save_images = save_images
        self.save_results = save_results
        self.input_interface = input_interface
        self.output_interface = output_interface
        # TODO add merge
        self.output_dir = output_dir
        if not os.path.isdir(self.output_dir):
            os.makedirs(self.output_dir)
        self.data_selection = data_selection
        self.custom_params = custom_params
        self.logger = logging.getLogger('analysis')
        self.logger.info("Initialized " + self.name)
        self.df = pd.DataFrame()
        self.datasets_names = []
        self.results = {}
        return

    @abstractmethod
    def load_data(self, df: pd.DataFrame):
        if df is not None:
            self.df = df
            self.datasets_names = self.df['dataset_name'].unique()
        return

    @abstractmethod
    def check_data(self):
        pass

    @abstractmethod
    def custom_settings(self):
        pass

    @abstractmethod
    def run(self):
        pass

    def save_output_to_file(self):
        # Save output to file
        filename = os.path.join(self.output_dir, f"{self.name}.json")
        with open(filename, 'w') as file:
            pprint(self.results, stream=file)

        return

    def get_results(self):
        return self.results


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


def init_analysis(config, input_interface=None, output_interface=None):
    logger = logging.getLogger('init_analysis')
    analysis = None
    analysis_module = config["name"]

    if config["name"] in ANALYSIS:
        if config["enabled"]:
            if 'full_custom_mode' not in config.keys():
                config['full_custom_mode'] = False

            full_module_path = f"src.analysis.{analysis_module}"
            AnalysisClass = import_class(full_module_path, config["name"])
            analysis = AnalysisClass(id=config['id'] if 'id' in config.keys() else 1,
                                     name=config['name'],
                                     info=config['info'],
                                     enabled=config['enabled'],
                                     full_custom_mode=config['full_custom_mode'],
                                     show_images=config['show_images'],
                                     save_images=config['save_images'],
                                     save_results=config['save_results'],
                                     input_interface=input_interface,
                                     output_interface=output_interface,
                                     output_dir=config['output_dir'],
                                     data_selection=config['data_selection'] if 'data_selection' in config.keys() else None,    # if not config['full_custom_mode'] else None,
                                     custom_params=config['custom_params'] if 'custom_params' in config.keys() else None)   # if not config['full_custom_mode'] else None)
        else:
            logger.info('Analysis ' + config["name"] + ' not enabled.')
    else:
        raise Exception('Analysis ' + config["name"] + ' does not exist. Check the config file. ' +
                        'Available analyses: ' + str(ANALYSIS))

    return analysis
