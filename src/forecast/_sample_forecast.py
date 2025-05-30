import os
import pandas as pd
import plotly.express as px
from pprint import pprint
from src.forecast.forecast import Forecast


class _sample_forecast(Forecast):
    def __init__(self, id, name, algo, info, actor, actor_id, date, enabled, full_custom_mode, mode, submode, models_dir, model_name,
                 show_images, save_images, save_results, input_interface, output_interface, mlflow_interface, output_dir, data_selection,
                 custom_params):
        super().__init__(id=id, name=name, algo=algo, info=info, actor=actor, actor_id=actor_id, date=date, enabled=enabled,
                         full_custom_mode=full_custom_mode, mode=mode, submode=submode, models_dir=models_dir, model_name=model_name,
                         show_images=show_images, save_images=save_images, save_results=save_results, input_interface=input_interface,
                         output_interface=output_interface, mlflow_interface=mlflow_interface, output_dir=output_dir,
                         data_selection=data_selection, custom_params=custom_params)
        return

    def check_data(self):

        return

    def feature_engineering(self):

        return

    def run(self):
        """
        # Forecast description
        """

        output_dict = {}

        # Run forecast
        for dataset_name in self.datasets_names:
            self.logger.info(f"{dataset_name} - Sample Forecast")
            df = self.df.loc[self.df['dataset_name'] == dataset_name]
            # ...

        self.results = output_dict

        return

    def train(self):
        return

    def predict(self):
        return

