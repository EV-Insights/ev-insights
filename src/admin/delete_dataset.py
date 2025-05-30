import os
import pandas as pd
import plotly.express as px
from pprint import pprint
from src.admin.admin import Admin


class delete_dataset(Admin):
    def __init__(self, id, name, info, enabled, output_interface, output_dir, custom_params):
        super().__init__(id=id, name=name, info=info, enabled=enabled, output_interface=output_interface, output_dir=output_dir,
                         custom_params=custom_params)
        return

    def run(self):
        """
        # This admin function delete all data of a specific dataset in the databse
        """
        dataset_name = self.custom_params['dataset_name']

        # TODO to be implemented
        self.output_interface.delete_dataset(dataset_name=dataset_name)

        self.output.append(f"All data of the dataset {dataset_name} deleted from the database")

        return self.output
