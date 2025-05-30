import os
import pandas as pd
import plotly.express as px
from pprint import pprint
from src.admin.admin import Admin


class init_db(Admin):
    def __init__(self, id, name, info, enabled, output_interface, output_dir, custom_params):
        super().__init__(id=id, name=name, info=info, enabled=enabled, output_interface=output_interface, output_dir=output_dir,
                         custom_params=custom_params)
        return

    def run(self):
        """
        # This admin function delete all data in the databse and initialize the schema
        """

        self.output_interface.init_db()

        self.output.append("Database initialized, all data deleted")

        return self.output
