import os
import copy
import logging
import importlib
import pandas as pd
from datetime import datetime
from pprint import pprint
from abc import abstractmethod
from src.interfaces.interface import Interface

# Retrieve the names of forecasts from the source, ensuring the list updates automatically whenever a new forecast is added.
FORECAST = [s.replace(".py", "") for s in [f for f in os.listdir(os.path.dirname(os.path.abspath(__file__)))
                                           if ".py" in f and f not in ["forecast.py", "_sample_forecast.py", "__init__.py"]]]


class Forecast:
    def __init__(self, id: int, name: str, algo: str, info: str, actor: str, actor_id: int, date: datetime.date, enabled: bool,
                 full_custom_mode: bool, mode: str, submode: str, models_dir: str, model_name: str, show_images: bool, save_images: bool,
                 save_results: bool, input_interface: Interface, output_interface: Interface, mlflow_interface: Interface, output_dir: str,
                 data_selection: dict, custom_params: dict):
        self.id = id
        self.name = name
        self.algo = algo
        self.info = info
        self.actor = actor
        self.actor_id = actor_id
        self.date = datetime.strptime(date, "%Y-%m-%d").date() if date is not  None else None
        self.enabled = enabled
        self.full_custom_mode = full_custom_mode
        self.mode = mode
        self.submode = submode
        self.models_dir = models_dir
        if not os.path.isdir(self.models_dir):
            os.makedirs(self.models_dir)
        self.model_name = model_name
        self.show_images = show_images
        self.save_images = save_images
        self.save_results = save_results
        self.input_interface = input_interface
        self.output_interface = output_interface
        self.mlflow_interface = mlflow_interface
        # TODO add merge
        self.output_dir = output_dir
        if not os.path.isdir(self.output_dir):
            os.makedirs(self.output_dir)
        self.data_selection = data_selection
        self.custom_params = custom_params
        self.logger = logging.getLogger('forecast')
        self.logger.info("Initialized " + self.name)
        self.df = pd.DataFrame()
        self.model = None
        self.prediction = None
        self.datasets_names = []
        self.results = {}
        self.columns = []
        self.target = None
        return

    @abstractmethod
    def load_data(self, df: pd.DataFrame, prediction=None, model=None):
        if df is not None:
            self.df = df
            self.datasets_names = self.df['dataset_name'].unique()
        if model is not None:
            self.model = model
        if prediction is not None:
            self.prediction = prediction

        return

    @abstractmethod
    def check_data(self):
        pass

    @abstractmethod
    def feature_engineering(self):
        pass

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def train(self):
        pass

    @abstractmethod
    def predict(self):
        pass

    # TODO This should be moved into the interface
    def save_output_to_file(self):
        # Save output to file
        filename = os.path.join(self.output_dir, f"{self.name}.json")
        with open(filename, 'w') as file:
            pprint(self.results, stream=file)

        return

    def get_train_results(self, keys=None):
        results = copy.deepcopy(self.results)
        if keys:
            for key in self.results[self.mode]:
                for sub_key in self.results[self.mode][key]:
                    if sub_key not in keys:
                        results[self.mode][key].pop(sub_key)
        else:
            results = self.results

        return results

    def get_predict_results(self):
        return self.results

    @staticmethod
    def get_model_name(prefix, pilot=None, actor=None, actor_id=None):
        """
        Create a formatted string using the provided parameters.

        Parameters:
        - prefix (str): The required prefix for the string. Always included.
        - pilot (str or None): The pilot name. If None, it is excluded.
        - actor (str or None): The actor name, one of "u" (user), "c" (charging_station), "ug" (user group), "cg" (charging_station group).
            If None, it is excluded.
        - id (int or str or None): The optional identifier. If None, it is excluded.

        Returns:
        - str: A string in the format 'prefix_pilot_actor_id'

        Raises:
        - ValueError: If the actor is not in the set of valid values.
        """
        # Validate the actor parameter
        valid_actors = {"u", "c", "ug", "cg"}
        if actor is not None and actor not in valid_actors:
            raise ValueError(f"Invalid actor value: {actor}. Must be one of {valid_actors}.")

        components = [prefix]  # The prefix is always present

        if pilot:
            components.append(pilot)  # Add pilot if it's not None
        if actor:
            components.append(actor)  # Add actor if it's not None
        if actor_id:
            components.append(str(actor_id))  # Convert and add id if it's not None

        # Join the components with an underscore '_'
        model_name = "_".join(components)
        return model_name


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


def init_forecast(config, models_dir, input_interface=None, output_interface=None, mlflow_interface=None):
    logger = logging.getLogger('init_forecast')
    forecast = None
    forecast_module = config["name"]

    if config["name"] in FORECAST:
        if config["enabled"]:
            if 'full_custom_mode' not in config.keys():
                config['full_custom_mode'] = False

            full_module_path = f"src.forecast.{forecast_module}"
            ForecastClass = import_class(full_module_path, config["name"])
            forecast = ForecastClass(id=config['id'] if 'id' in config.keys() else 1,
                                     name=config['name'],
                                     algo=config['algo'],
                                     info=config['info'],
                                     actor=config['actor'] if 'actor' in config.keys() else None,
                                     actor_id=config['actor_id'] if 'actor_id' in config.keys() else None,
                                     date=config['date'] if 'date' in config.keys() else None,
                                     enabled=config['enabled'],
                                     full_custom_mode=config['full_custom_mode'],
                                     mode=config['mode'],
                                     submode=config['submode'] if 'submode' in config.keys() else None,
                                     models_dir=os.path.join(models_dir, config['name']),
                                     model_name=config['model_name'],
                                     show_images=config['show_images'],
                                     save_images=config['save_images'],
                                     save_results=config['save_results'],
                                     input_interface=input_interface,
                                     output_interface=output_interface,
                                     mlflow_interface=mlflow_interface,
                                     output_dir=config['output_dir'],
                                     data_selection=config['data_selection'] if not config['full_custom_mode'] else None,
                                     custom_params=config['custom_params'] if not config['full_custom_mode'] else None)
        else:
            logger.info('Forecast ' + config["name"] + ' not enabled.')
    else:
        raise Exception('Forecast ' + config["name"] + ' does not exist. Check the config file. ' +
                        'Available interfaces: ' + str(FORECAST))

    return forecast
