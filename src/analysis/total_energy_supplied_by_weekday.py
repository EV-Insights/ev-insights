import os
import pandas as pd
import plotly.express as px
from pprint import pprint
from src.analysis.analysis import Analysis


class total_energy_supplied_by_weekday(Analysis):
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
                # Apply filters
                self.df['plug_duration'] = self.df['plug_duration'].apply(lambda x: x if filters['min'] <= x <= filters['max'] else None)
                self.df = self.df.dropna()

        return

    # def run(self):
    #     """
    #     # Plot total energy supplied by weekday
    #     """
    #     output_dict = {}
    #
    #     for dataset_name in self.datasets_names:
    #         self.logger.info(f"{dataset_name} - Plot total energy supplied by weekday")
    #
    #         df = self.df.loc[self.df['dataset_name'] == dataset_name]
    #
    #         weekday_order = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    #         grouped_df = df.groupby('plug_in_weekday')['energy_supplied'].sum().reset_index()
    #         grouped_df['plug_in_weekday'] = pd.Categorical(grouped_df['plug_in_weekday'], categories=weekday_order, ordered=True)
    #
    #         # Sort the DataFrame by the 'weekday' column
    #         grouped_df = grouped_df.sort_values(by='plug_in_weekday')
    #
    #         fig = px.bar(
    #             grouped_df,
    #             x="plug_in_weekday",
    #             y="energy_supplied",
    #             title=f'Total Energy Supplied by Weekday<br>' +
    #                   (f'<span style="font-size: 20px; display: block;">{self.info}</span><br>' if self.info != '' else '') +
    #                   f'<span style="font-size: 18px; display: block;">Dataset: {dataset_name}</span>',
    #             text="energy_supplied"
    #         )
    #         fig.update_layout(
    #             title={
    #                 "x": 0.5,
    #                 "xanchor": "center",
    #                 'y': 0.94,
    #                 'yanchor': 'top'
    #             },
    #             margin=dict(t=130),
    #         )
    #
    #         fig.update_xaxes(title_text='Day of Week')
    #         fig.update_yaxes(title_text='Total Energy Supplied [kWh]')
    #
    #         # Increase the size of text on the plot
    #         fig.update_layout(
    #             font=dict(
    #                 size=20  # Adjust the font size as needed
    #             )
    #         )
    #
    #         if self.save_images:
    #             fig.write_image(os.path.join(self.output_dir, f'{dataset_name}_energy_supplied_by_weekday.png'),
    #                             width=1080, height=720, scale=2)
    #
    #         if self.show_images:
    #             fig.show()
    #
    #         output_dict.update({dataset_name: dict(zip(grouped_df['plug_in_weekday'], grouped_df['energy_supplied']))})
    #
    #     # TODO write results in output_dict, that is void now
    #     self.results = output_dict
    #
    #     return

    import plotly.express as px
    import plotly.io as pio

    def run(self):
        """
        Plot total energy supplied by weekday, with enhanced style.
        """
        output_dict = {}

        for dataset_name in self.datasets_names:
            self.logger.info(f"{dataset_name} - Plot total energy supplied by weekday")

            df = self.df.loc[self.df['dataset_name'] == dataset_name]

            weekday_order = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
            grouped_df = df.groupby('plug_in_weekday')['energy_supplied'].sum().reset_index()
            grouped_df['plug_in_weekday'] = pd.Categorical(grouped_df['plug_in_weekday'], categories=weekday_order, ordered=True)
            grouped_df = grouped_df.sort_values(by='plug_in_weekday')

            fig = px.bar(
                grouped_df,
                x="plug_in_weekday",
                y="energy_supplied",
                text="energy_supplied",
                color="plug_in_weekday",
                color_discrete_sequence=px.colors.sequential.Tealgrn,
                hover_data={"energy_supplied": ":.2f", "plug_in_weekday": True},
                title=f"Total Energy Supplied by Weekday<br>"
                      f"<span style='font-size: 18px; color:gray;'>{self.info}</span><br>"
                      f"<span style='font-size: 16px;'>Dataset: <b>{dataset_name}</b></span>"
            )

            fig.update_traces(
                texttemplate="%{text:.1f} kWh",
                textposition="outside",
                marker_line_width=1.5,
                marker_line_color="white"
            )

            fig.update_layout(
                title={
                    "x": 0.5,
                    "xanchor": "center",
                    'y': 0.92,
                    'yanchor': 'top'
                },
                xaxis_title="Day of the Week",
                yaxis_title="Total Energy Supplied [kWh]",
                font=dict(size=18),
                uniformtext_minsize=12,
                uniformtext_mode='hide',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                bargap=0.25,
                margin=dict(t=120, l=60, r=40, b=60),
                showlegend=False
            )

            fig.update_yaxes(showgrid=True, gridwidth=0.3, gridcolor='lightgray')
            fig.update_xaxes(showline=True, linewidth=1, linecolor='gray')

            if self.save_images:
                fig.write_image(os.path.join(self.output_dir, f'{dataset_name}_energy_supplied_by_weekday.png'),
                                width=1080, height=720, scale=2)

            if self.show_images:
                fig.show()

            output_dict[dataset_name] = dict(zip(grouped_df['plug_in_weekday'], grouped_df['energy_supplied']))

        self.results = output_dict
        return
