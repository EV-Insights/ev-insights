import os
import numpy as np
import plotly.express as px
from src.analysis.analysis import Analysis


class plug_duration(Analysis):
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
        # Plot distribution of plug duration
        """

        output_dict = {}

        bin_width = 10

        for dataset_name in self.datasets_names:
            self.logger.info(f"{dataset_name} - Plot distribution of plug duration")

            df = self.df.loc[self.df['dataset_name'] == dataset_name]

            min_duration = int(df['plug_duration_clip'].min())
            max_duration = int(df['plug_duration_clip'].max())

            num_bins = int((max_duration - min_duration) / bin_width) + 1
            bin_sequence = [min_duration + i * (bin_width * 5) for i in range(num_bins + 1)]

            # Create histogram
            fig = px.histogram(
                df,
                x='plug_duration_clip',
                nbins=num_bins,
                range_x=[min_duration, max_duration],
                title=f'<span style="font-size: 20px; display: block;">Distribution of plug duration</span><br>' +
                      (f'<span style="font-size: 15px; display: block;">{self.info}</span><br>' if self.info != '' else '') +
                      f'<span style="font-size: 13px; display: block;">Dataset: {dataset_name}</span>',
                labels={'plug_duration_clip': 'Plug Duration', 'count': 'Frequency'},
                category_orders={'x': bin_sequence}
            )
            fig.update_xaxes(title_text='Duration (minutes)')
            fig.update_yaxes(title_text='Occurrences')
            fig.update_xaxes(title_text='Duration (minutes)', tickvals=bin_sequence,
                             ticktext=[str(bin_val) for bin_val in bin_sequence])
            fig.update_layout(
                barmode='overlay',
                title={
                    "x": 0.5,
                    "xanchor": "center",
                    'y': 0.94,
                    'yanchor': 'top'
                },
                margin=dict(t=130),
            )

            # Save the figure
            if self.save_images:
                fig.write_image(os.path.join(self.output_dir, f'{dataset_name}_plug_duration_distribution.png'),
                                width=1080, height=720, scale=2)

            if self.show_images:
                fig.show()

        # TODO write results in output_dict, that is void now
        self.results = output_dict

        return
