import os
import pandas as pd
import plotly.express as px
from pprint import pprint
from src.admin.admin import Admin


class _sample_admin(Admin):
    def __init__(self, id, name, info, enabled, output_interface, output_dir, custom_params):
        super().__init__(id=id, name=name, info=info, enabled=enabled, output_interface=output_interface, output_dir=output_dir,
                         custom_params=custom_params)
        return

    def check_data(self):

        return

    def custom_settings(self):

        return

    def run(self):
        """
        # Admin function description
        """

        output_dict = {}

        # Run admin function
        # ...

        self.results = output_dict

        return
