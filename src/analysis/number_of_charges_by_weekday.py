import os
import pandas as pd
import plotly.express as px
from src.analysis.analysis import Analysis


class number_of_charges_by_weekday(Analysis):
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

        return

    def run(self):
        """
        # Plot total number of charging sessions by weekday
        """

        output_dict = {}

        for dataset_name in self.datasets_names:
            self.logger.info(f"{dataset_name} - Plot total number of charging sessions by weekday")

            df = self.df.loc[self.df['dataset_name'] == dataset_name]

            weekday_order = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
            grouped_df = df.groupby('plug_in_weekday')['energy_supplied'].count().reset_index()
            grouped_df['plug_in_weekday'] = pd.Categorical(grouped_df['plug_in_weekday'], categories=weekday_order, ordered=True)
            # Sort the DataFrame by the 'weekday' column
            grouped_df = grouped_df.sort_values(by='plug_in_weekday')
            grouped_df.rename(columns={"energy_supplied": "Number of charging sessions", "plug_in_weekday": "Day of Week"},
                              inplace=True)

            fig = px.bar(
                grouped_df,
                x='Day of Week',
                y='Number of charging sessions',
                title=f'<span style="font-size: 20px; display: block;">Number of charging sessions by Weekday</span><br>' +
                      (f'<span style="font-size: 15px; display: block;">{self.info}</span><br>' if self.info != '' else '') +
                      f'<span style="font-size: 13px; display: block;">Dataset: {dataset_name}</span>',
                text='Number of charging sessions')
            fig.update_xaxes(title_text='Day of Week')
            fig.update_yaxes(title_text='Number of Charging Sessions')

            fig.update_layout(
                title={
                    "x": 0.5,
                    "xanchor": "center",
                    'y': 0.94,
                    'yanchor': 'top'
                },
                margin=dict(t=100),
            )

            if self.save_images:
                fig.write_image(os.path.join(self.output_dir, f'{dataset_name}_number_of_charges_by_weekday.png'),
                                width=1080, height=720, scale=2)

            if self.show_images:
                fig.show()

        # TODO write results in output_dict, that is void now
        self.results = output_dict

        return
