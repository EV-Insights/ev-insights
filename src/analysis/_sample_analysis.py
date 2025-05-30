import os
import pandas as pd
import plotly.express as px
from pprint import pprint
from src.analysis.analysis import Analysis


class _sample_analysis(Analysis):
    def __init__(self, id, name, info, enabled, full_custom_mode, show_images, save_images, save_results, input_interface, output_interface,
                 output_dir, data_selection, custom_params):
        super().__init__(id=id, name=name, info=info, enabled=enabled, full_custom_mode=full_custom_mode, show_images=show_images,
                         save_images=save_images, save_results=save_results, input_interface=input_interface, output_interface=output_interface,
                         output_dir=output_dir, data_selection=data_selection, custom_params=custom_params)
        return

    def check_data(self):

        return

    def custom_settings(self):

        return

    def run(self):
        """
        # Analysis description
        """

        output_dict = {}

        # Run analysis
        for dataset_name in self.datasets_names:
            self.logger.info(f"{dataset_name} - Sample Analysis")
            df = self.df.loc[self.df['dataset_name'] == dataset_name]
            # ...

        self.results = output_dict

        return
