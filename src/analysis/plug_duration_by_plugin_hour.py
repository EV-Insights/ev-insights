import os
import math
import pandas as pd
import numpy as np
import plotly.express as px
from pprint import pprint
from src.analysis.analysis import Analysis


class plug_duration_by_plugin_hour(Analysis):
    def __init__(self, id, name, info, enabled, full_custom_mode, show_images, save_images, save_results, input_interface, output_interface,
                 output_dir, data_selection, custom_params):
        super().__init__(id=id, name=name, info=info, enabled=enabled, full_custom_mode=full_custom_mode, show_images=show_images,
                         save_images=save_images, save_results=save_results, input_interface=input_interface, output_interface=output_interface,
                         output_dir=output_dir, data_selection=data_selection, custom_params=custom_params)
        return

    def check_data(self):

        return

    def custom_settings(self):
        for feature, filters in self.custom_params.items():

            # Add plug in hour
            if feature == 'plug_in_hour':
                # Add feature
                if 'plug_in_hour' not in self.df.columns:
                    self.df['plug_in_hour'] = self.df['plug_in_datetime'].dt.hour

            # Plug Duration in minutes
            if feature == 'plug_duration':
                # Add feature
                if 'plug_duration' not in self.df.columns:
                    self.df['plug_duration'] = (self.df['plug_out_datetime'] - self.df['plug_in_datetime']).dt.total_seconds() / 60

            # Plug Duration in minutes clip
            if feature == 'plug_duration_clip':
                # Add feature
                if 'plug_duration_clip' not in self.df.columns:
                    self.df['plug_duration_clip'] = self.df['plug_duration']
                # Apply filters
                self.df['plug_duration_clip'] = np.clip(self.df['plug_duration_clip'].values, a_min=filters['min'], a_max=filters['max'])

        return

    def run(self):
        """
        # Analysis description
        """

        output_dict = {}

        # Run analysis
        for dataset_name in self.datasets_names:
            self.logger.info(f"{dataset_name} - Plot distribution of plug duration by hour of plugin")
            df = self.df.loc[self.df['dataset_name'] == dataset_name]

            fig = px.box(
                df,
                x="plug_in_hour",
                y="plug_duration_clip",
                title=f'<span style="font-size: 20px; display: block;">Plug Duration by Plug-in Hour</span><br>' +
                      (f'<span style="font-size: 15px; display: block;">{self.info}</span><br>' if self.info != '' else '') +
                    f'<span style="font-size: 13px; display: block;">Dataset: {dataset_name}</span>',
            )
            fig.update_layout(
                title={
                    "x": 0.5,
                    "xanchor": "center",
                    'y': 0.94,
                    'yanchor': 'top'
                },
                margin=dict(t=100),
            )
            fig.update_xaxes(title_text='Hours of the Day')
            fig.update_yaxes(title_text='Plug Duration')

            # Save the figure
            if self.save_images:
                fig.write_image(os.path.join(self.output_dir, f'{dataset_name}_plug_duration_by_plugin_hour.png'),
                                width=1080, height=720, scale=2)
                fig.write_html(os.path.join(self.output_dir, f'{dataset_name}_plug_duration_by_plugin_hour.html'))

            if self.show_images:
                fig.show()

            output = self.extract_stats(df[['plug_in_hour', 'plug_duration_clip']])
            output_dict.update({dataset_name: output})

        self.results = output_dict

        return

    def extract_stats(self, df):
        # Calculate quartiles as outlined in the plotly documentation
        # (method #10 in paper https://jse.amstat.org/v14n3/langford.html)
        def get_percentile(data, p):
            data_sorted = sorted(float(d) for d in data)
            n = len(data_sorted)
            x = n * p + 0.5

            # If integer, return
            if x.is_integer():
                idx = int(x - 1)
                if 0 <= idx < n:
                    return round(data_sorted[idx], 2)  # account for zero-indexing

            # If not an integer, get the interpolated value of the values of floor and ceiling indices
            x1, x2 = math.floor(x), math.ceil(x)
            if 1 <= x1 <= n and 1 <= x2 <= n:
                y1, y2 = data_sorted[x1 - 1], data_sorted[x2 - 1]  # account for zero-indexing
                return round(np.interp(x=x, xp=[x1, x2], fp=[y1, y2]), 2)
            else:
                return None

        # Get unique values of 'plug_in_hour'
        unique_plug_in_hours = df['plug_in_hour'].unique()

        # Dictionary to store boxplot statistics for each plug_in_hour
        boxplot_stats_dict = {}

        # Iterate over unique plug_in_hours and calculate boxplot statistics
        for hour in unique_plug_in_hours:
            filtered_data = df[df['plug_in_hour'] == hour]['plug_duration_clip']

            q1 = get_percentile(filtered_data, 0.25)
            median = get_percentile(filtered_data, 0.50)
            q3 = get_percentile(filtered_data, 0.75)

            if q1 is not None and median is not None and q3 is not None:
                iqr = q3 - q1

                # Calculate fences
                lower_limit = q1 - 1.5 * iqr
                upper_limit = q3 + 1.5 * iqr

                # Calculate lower and upper fences
                lower_fence = round(min([i for i in filtered_data.tolist() if i >= lower_limit]), 2)
                upper_fence = round(max([i for i in filtered_data.tolist() if i <= upper_limit]), 2)

                # Store statistics in dictionary
                boxplot_stats_dict[hour] = {
                    'q1': q1,
                    'median': median,
                    'q3': q3,
                    'lower_fence': lower_fence,
                    'upper_fence': upper_fence
                }

        return boxplot_stats_dict
