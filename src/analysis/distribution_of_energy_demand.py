import os
import numpy as np
import plotly.express as px
from src.analysis.analysis import Analysis


class distribution_of_energy_demand(Analysis):
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

            # Energy supplied clipped between min and max values
            if feature == 'energy_supplied_clip':
                # Add feature
                if 'energy_supplied_clip' not in self.df.columns:
                    self.df['energy_supplied_clip'] = self.df['energy_supplied']
                # Apply filters
                self.df['energy_supplied_clip'] = np.clip(self.df['energy_supplied_clip'].values, a_min=filters['min'], a_max=filters['max'])

        return

    def run(self):
        """
        # Plot distribution of energy demand
        """
        output_dict = {}

        bin_width = 1

        for dataset_name in self.datasets_names:
            self.logger.info(f"{dataset_name} - Plot distribution of energy demand")

            df = self.df.loc[self.df['dataset_name'] == dataset_name]

            min_energy = int(df['energy_supplied_clip'].min())
            max_energy = int(df['energy_supplied_clip'].max())

            num_bins = int((max_energy - min_energy) / bin_width) + 1
            bin_sequence = [min_energy + i * (bin_width * 5) for i in range(num_bins + 1)]

            # Create histogram
            fig = px.histogram(
                df,
                x='energy_supplied_clip',
                nbins=num_bins,
                range_x=[min_energy, max_energy],
                title=f'<span style="font-size: 20px; display: block;">Distribution of supplied energy</span><br>' +
                      (f'<span style="font-size: 15px; display: block;">{self.info}</span><br>' if self.info != '' else '') +
                      f'<span style="font-size: 13px; display: block;">Dataset: {dataset_name}</span>',
                labels={'energy_supplied': 'Energy supplied', 'count': 'Frequency'},
                category_orders={'x': bin_sequence}
            )
            fig.update_xaxes(title_text='Energy Supplied')
            fig.update_yaxes(title_text='Occurrences')
            fig.update_xaxes(title_text='Energy [kWh]', tickvals=bin_sequence,
                             ticktext=[str(bin_val) for bin_val in bin_sequence])
            fig.update_layout(
                barmode='overlay',
                title={
                    "x": 0.5,
                    "xanchor": "center",
                    'y': 0.94,
                    'yanchor': 'top'
                },
                margin=dict(t=100),
            )

            # Save the figure
            if self.save_images:
                fig.write_image(os.path.join(self.output_dir, f'{dataset_name}_energy_supplied_distribution.png'),
                                width=1080, height=720, scale=2)

            if self.show_images:
                fig.show()

        # TODO write results in output_dict, that is void now
        self.results = output_dict

        return
