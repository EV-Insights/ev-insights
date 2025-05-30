import os
import pandas as pd
import numpy as np
import plotly.express as px
from src.analysis.analysis import Analysis


class animated_energy_duration(Analysis):
    def __init__(self, id, name, info, enabled, full_custom_mode, show_images, save_images, save_results, input_interface, output_interface,
                 output_dir, data_selection, custom_params):
        super().__init__(id=id, name=name, info=info, enabled=enabled, full_custom_mode=full_custom_mode, show_images=show_images,
                         save_images=save_images, save_results=save_results, input_interface=input_interface, output_interface=output_interface,
                         output_dir=output_dir, data_selection=data_selection, custom_params=custom_params)
        return

    def check_data(self):
        # TODO check data before starting the analysis

        return

    def custom_settings(self):

        for feature, filters in self.custom_params.items():

            # Week day name
            if feature == 'plug_in_weekday':
                # Add feature
                if 'plug_in_weekday' not in self.df.columns:
                    self.df['plug_in_weekday'] = self.df['plug_in_datetime'].dt.day_name()

            # Plugin Duration in minutes
            if feature == 'plug_duration':
                # Add feature
                if 'plug_duration' not in self.df.columns:
                    self.df['plug_duration'] = (self.df['plug_out_datetime'] - self.df['plug_in_datetime']).dt.total_seconds() / 60

            # Plugin Duration in minutes clip
            if feature == 'plug_duration_clip':
                # Add feature
                if 'plug_duration_clip' not in self.df.columns:
                    self.df['plug_duration_clip'] = self.df['plug_duration']
                # Apply filters
                self.df['plug_duration_clip'] = np.clip(self.df['plug_duration_clip'].values, a_min=filters['min'], a_max=filters['max'])

        return

    def run(self):
        """
        # Plot animated duration demand by week of the year
        """

        output_dict = {}

        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        # Run analysis
        for dataset_name in self.datasets_names:
            self.logger.info(f"{dataset_name} - Plot animated duration demand by week of the year")

            df = self.df.loc[self.df['dataset_name'] == dataset_name]

            # df['plug_in_weekday'] = pd.Categorical(df['plug_in_weekday'], categories=days, ordered=True)
            df.loc[df['plug_in_weekday'].isin(days), 'plug_in_weekday'] = pd.Categorical(
                df.loc[df['plug_in_weekday'].isin(days), 'plug_in_weekday'],
                categories=days,
                ordered=True
            )

            df = df.sort_values('plug_in_weekday', ascending=True)

            fig = px.scatter(
                df, 
                x="plug_duration_clip", 
                y="energy_supplied", 
                animation_frame="plug_in_weekday",
                color="dataset_country", 
                title=f'<span style="font-size: 20px; display: block;">Animated duration demand by week of the year</span><br>' +
                      (f'<span style="font-size: 15px; display: block;">{self.info}</span><br>' if self.info != '' else '') +
                      f'<span style="font-size: 13px; display: block;">Dataset: {dataset_name}</span>',
            )
            fig.update_xaxes(title_text='Plug Duration')
            fig.update_yaxes(title_text='Energy Supplied')
            fig.update_layout(
                title={
                    "x": 0.5,
                    "xanchor": "center",
                    'y': 0.94,
                    'yanchor': 'top'
                },
                margin=dict(t=100),
                transition_duration=1500
            )
            # fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 1500

            if self.save_images:
                # fig.write_image(os.path.join(self.output_dir, f'{dataset_name}_scatter_animated_energy_duration.png'),
                #                 width=1080, height=720, scale=2)
                fig.write_html(os.path.join(self.output_dir, f'{dataset_name}_plugin_duration_by_plugin_hour.html'))

            if self.show_images:
                fig.show()

        # TODO write results in output_dict, that is void now
        self.results = output_dict

        return
