from datetime import datetime, timedelta
import os
import random
import numpy as np
import xgboost as xgb
import pandas as pd
import plotly.express as px
from pprint import pprint
from src.forecast.forecast import Forecast
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
# pd.set_option('display.max_columns', None)


class xgboost_energy(Forecast):
    def __init__(self, id, name, algo, info, actor, actor_id, date, enabled, full_custom_mode, mode, submode, models_dir, model_name,
                 show_images, save_images, save_results, input_interface, output_interface, mlflow_interface, output_dir, data_selection,
                 custom_params):
        super().__init__(id=id, name=name, algo=algo, info=info, actor=actor, actor_id=actor_id, date=date, enabled=enabled,
                         full_custom_mode=full_custom_mode, mode=mode, submode=submode, models_dir=models_dir, model_name=model_name,
                         show_images=show_images, save_images=save_images, save_results=save_results, input_interface=input_interface,
                         output_interface=output_interface, mlflow_interface=mlflow_interface, output_dir=output_dir,
                         data_selection=data_selection, custom_params=custom_params)
        return

    def check_data(self):

        # Remove NaT values from plug_in_datetime
        if self.df is not None:
            if 'plug_in_datetime' in self.df.columns:
                self.df = self.df.dropna(subset=['plug_in_datetime'])

        return

    def feature_engineering(self):

        #self.columns = self.df.columns.tolist()

        self.columns.append('energy_supplied')

        for feature, filters in self.custom_params.items():

            # Plugin Duration in minutes
            if feature == 'plug_in_month':
                # Add feature
                if 'plug_in_month' not in self.df.columns:
                    self.df['plug_in_month'] = self.df['plug_in_datetime'].dt.month
                    self.columns.append('plug_in_month')

            # Week day name
            if feature == 'plug_in_weekday':
                # Add feature
                if 'plug_in_weekday' not in self.df.columns:
                    self.df['plug_in_weekday'] = self.df['plug_in_datetime'].dt.weekday
                    self.columns.append('plug_in_weekday')

            # Plugin hour minutes
            if feature == 'plug_in_hour_minutes':
                # Add feature
                if 'plug_in_hour_minutes' not in self.df.columns:
                    self.df['plug_in_hour_minutes'] = self.df['plug_in_datetime'].apply(
                        lambda row: self.utc_to_decimal_hours_minutes(row))
                    self.columns.append('plug_in_hour_minutes')

            # Plugin Duration in minutes
            if feature == 'plug_duration':
                # Add feature
                if 'plug_duration' not in self.df.columns:
                    self.df['plug_duration'] = (self.df['plug_out_datetime'] - self.df[
                        'plug_in_datetime']).dt.total_seconds() / 60
                    self.columns.append('plug_duration')

            # Average Duration Moving Averages
            if feature == 'avg_duration':
                for interval in filters:
                    cname = 'avg_duration' + str(interval)
                    if cname not in self.df.columns:
                        self.df[cname] = self.df['plug_duration'].shift(1).rolling(window=interval).mean()
                        self.columns.append(cname)

            # Average Duration Moving Averages
            if feature == 'avg_energy':
                for interval in filters:
                    cname = 'avg_energy' + str(interval)
                    if cname not in self.df.columns:
                        self.df[cname] = self.df['energy_supplied'].shift(1).rolling(window=interval).mean()
                        self.columns.append(cname)

        return

    def run(self):
        """
        # Forecast description
        """

        # Train the model or predict the forecast, depending on the mode chosen
        if self.mode == "train":
            self.train()

        elif self.mode == "predict":
            self.predict()

        else:
            self.train()
            self.predict()

        return

    def train(self):
        output_dict = {'train': {}}

        params = {'random_state': 16,
                  'test_size': 0.20}

        # Train model
        for dataset_name in self.datasets_names:
            self.logger.info(f"{dataset_name} - XGBoost Forecast - Model training")
            df = self.df.loc[self.df['dataset_name'] == dataset_name]

            unique_uids = df['user_id'].unique()

            df = df[self.columns]

            # TODO: Find a better place for this
            df['energy_supplied'] = df['energy_supplied'].astype(float)

            # 0/1 encoding of week days
            dummies = pd.get_dummies(df, columns=['plug_in_weekday'])
            weekday_column_names = [f'plug_in_weekday_{i}' for i in range(7)]
            # Ensure all days are encoded
            dummies = dummies.reindex(columns=weekday_column_names, fill_value=0)
            df = df.join(dummies)

            self.logger.info(df.columns.values)
            # self.logger.info(df.head(10))
            self.logger.info(f'Shape of features: {df.shape}')

            # remove target
            target = np.array(df['energy_supplied'])
            df = df.drop('energy_supplied', axis=1)

            data_array = np.array(df)
            train_features, test_features, train_labels, test_labels = train_test_split(data_array, target,
                                                                                        test_size=params['test_size'],
                                                                                        random_state=params['random_state'])
            self.logger.info(f'Training Features Shape: {train_features.shape}')
            self.logger.info(f'Training Labels Shape: {train_labels.shape}')
            self.logger.info(f'Testing Features Shape: {test_features.shape}')
            self.logger.info(f'Testing Labels Shape: {test_labels.shape}')

            # xgb_m = xgb(n_estimators=1000, random_state=42)
            xgb_m = xgb.XGBRegressor(objective="reg:squarederror", random_state=params['random_state'])

            xgb_m.fit(train_features, train_labels)

            # Use the forest's predict method on the test data
            predictions = xgb_m.predict(test_features)
            # Calculate the absolute errors
            errors = abs(predictions - test_labels)
            # Print out the mean absolute error (mae)
            self.logger.info('Results for energy_supplied')
            self.logger.info(f'Mean Absolute Error: {round(np.mean(errors), 2)}')

            # Calculate mean absolute percentage error (MAPE) for non-zero labels
            non_zero_indices = test_labels != 0
            filtered_errors = errors[non_zero_indices]
            filtered_test_labels = test_labels[non_zero_indices]
            # Calculate MAPE
            mape = 100 * np.mean(np.abs(filtered_errors / filtered_test_labels))

            # Calculate and display accuracy
            accuracy = 100 - np.mean(mape)
            self.logger.info(f'Accuracy: {round(accuracy, 2)} %.')

            model_name = self.get_model_name(prefix=self.name, pilot=dataset_name)

            # Save info
            output_dict['train'].update({
                model_name: {
                    'params': params,
                    'shapes': {
                        'training_features_shape': train_features.shape,
                        'training_labels_shape': train_labels.shape,
                        'testing_features_shape': test_features.shape,
                        'testing_labels_shape': test_labels.shape,
                    },
                    'model': xgb_m,
                    'metrics': {
                        'mae': round(np.mean(errors), 2),
                        'accuracy': round(accuracy, 2),
                    },
                    'artifacts': {
                    }
                }
            })

        self.results.update(output_dict)
        return

    def predict(self):
        output_dict = {'predict': {}}

        for dataset_name in self.datasets_names:
            if self.submode == 'schedule':
                df = self.df.loc[self.df['dataset_name'] == dataset_name]
                df = df[self.columns]
                df = df.drop(self.target, axis=1)
                input_data = df.iloc[[-1]]

                features = pd.DataFrame(input_data, index=[0])
                dummies = pd.get_dummies(features, columns=['plug_in_weekday'])
                weekday_column_names = [f'plug_in_weekday_{i}' for i in range(7)]
                dummies = dummies.reindex(columns=weekday_column_names, fill_value=0)
                features = features.join(dummies)

                est_energy = self.model.predict(features)

                output_dict['predict'].update(
                    {
                        'energy': est_energy[0].astype(float),
                        'date': self.date,
                        'created_at': datetime.now(),
                        'id': self.actor_id
                    }
                )

            elif self.submode == 'query':
                output_dict['predict'] = self.prediction

        self.results.update(output_dict)
        return

    def utc_to_decimal_hours_minutes(self, utc_time):
        return float(utc_time.strftime("%H")) + float(utc_time.strftime("%M")) / 60
