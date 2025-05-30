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
from matplotlib import pyplot as plt
import seaborn as sns
import lightgbm as lgb
import statsmodels.api as sts



class lightgbm_station_charges(Forecast):
    def __init__(self, id, name, algo, info, actor, actor_id, date, enabled, full_custom_mode, mode, submode, models_dir, model_name,
                 show_images, save_images, save_results, input_interface, output_interface, mlflow_interface, output_dir, data_selection,
                 custom_params):
        super().__init__(id=id, name=name, algo=algo, info=info, actor=actor, actor_id=actor_id, date=date, enabled=enabled,
                         full_custom_mode=full_custom_mode, mode=mode, submode=submode, models_dir=models_dir, model_name=model_name,
                         show_images=show_images, save_images=save_images, save_results=save_results, input_interface=input_interface,
                         output_interface=output_interface, mlflow_interface=mlflow_interface, output_dir=output_dir,
                         data_selection=data_selection, custom_params=custom_params)
        return

    def add_lags(self, df_, lag_col, lags, lag_windows=None):
        """Returns a new dataframe that also includes lagged values of the lag_col column of df.
           For long lags (1 day or more), also include mean, min, max over lag_window."""

        df = df_.copy()
        # Add lagged values
        for lag, lag_str in lags.items():
            df["lag_" + lag_str] = df[lag_col].shift(int(lag))
        if lag_windows is not None:
            # Add mean/min/max over lags windows
            for lag_w, lag_w_str in lag_windows.items():
                for lag, lag_str in lags.items():
                    df["lag_" + lag_str + "mean" + lag_w_str] = df[lag_col].shift(
                        int(lag) - int(lag_w) // 2).rolling(int(lag_w) + 1).mean()
                    df["lag_" + lag_str + "max" + lag_w_str] = df[lag_col].shift(
                        int(lag) - int(lag_w) // 2).rolling(int(lag_w) + 1).max()
                    df["lag_" + lag_str + "min" + lag_w_str] = df[lag_col].shift(
                        int(lag) - int(lag_w) // 2).rolling(int(lag_w) + 1).min()

        return df

    def add_timefeat_df(self, df_):
        """Add time-related features to df_"""

        # Create time features (for periodic features: use sin and cos)
        df = df_.copy()
        df["day_of_week"] = df.index.dayofweek.astype("category")
        df["day_of_year_sin"] = np.sin(2 * np.pi * df.index.dayofyear / 365.25)
        df["day_of_year_cos"] = np.cos(2 * np.pi * df.index.dayofyear / 365.25)
        df["month"] = df.index.month.astype("category")
        # time_mins = df.index.hour * 60 + df.index.minute
        # df["time_sin"] = np.sin(2 * np.pi * time_mins / (60 * 24))
        # df["time_cos"] = np.cos(2 * np.pi * time_mins / (60 * 24))
        df['is_business_day'] = df.index.map(lambda x: pd.tseries.offsets.BDay().is_on_offset(x)).astype("category")

        return df

    def smape(self, preds, target):
        n = len(preds)
        masked_arr = ~((preds == 0) & (target == 0))
        preds, target = preds[masked_arr], target[masked_arr]
        num = np.abs(preds - target)
        denom = np.abs(preds) + np.abs(target)
        smape_val = (200 * np.sum(num / denom)) / n
        return smape_val

    def lgbm_smape(self, preds, train_data):
        labels = train_data.get_label()
        smape_val = self.smape(np.expm1(preds), np.expm1(labels))
        return 'SMAPE', smape_val, False

    def plot_lgb_importances(self, model, plot=False, num=10):
        gain = model.feature_importance('gain')
        feat_imp = pd.DataFrame({'feature': model.feature_name(),
                                 'split': model.feature_importance('split'),
                                 'gain': 100 * gain / gain.sum()}).sort_values('gain', ascending=False)
        if plot:
            plt.figure(figsize=(10, 10))
            sns.set(font_scale=1)
            sns.barplot(x="gain", y="feature", data=feat_imp[0:25])
            plt.title('Feature Importance')
            plt.tight_layout()
            plt.show()
        else:
            print(feat_imp.head(num))
        return feat_imp

    def utc_to_decimal_hours_minutes(self, utc_time):
        return float(utc_time.strftime("%H")) + float(utc_time.strftime("%M")) / 60

    def check_data(self):

        # Remove NaT values from plug_in_datetime
        if self.df is not None:
            if 'plug_in_datetime' in self.df.columns:
                self.df = self.df.dropna(subset=['plug_in_datetime'])

        return

    def feature_engineering(self):

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
                    self.target.append('plug_duration')

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

            # TODO: Discuss if right place here!
            if feature == 'ts_engineering':
                lags = filters['lags']
                lag_windows = filters['lag_windows']

                # Set 'plug_in_datetime' as the index, resample to get daily demand, ensure all days are present (fill with 0)
                self.df.set_index('plug_in_datetime', inplace=True)
                dataset_name_mode = self.df['dataset_name'].mode()[0]
                station_id_mode = self.df['station_id'].mode()[0]
                self.df['number_charges'] = self.df['station_id']
                self.df = self.df.resample('D').agg({
                    'number_charges': 'size',
                    'dataset_name': lambda x: dataset_name_mode,
                    'station_id': lambda x: station_id_mode
                })
                date_range = pd.date_range(start=self.df.index.min(), end=self.df.index.max(), freq='D')
                self.df = self.df.reindex(date_range, fill_value=0)
                self.df = self.add_timefeat_df(self.df)
                self.df = self.add_lags(self.df, "number_charges", lags, lag_windows)
                self.columns = [col for col in self.df.columns if col not in ['dataset_name', 'date', 'number_charges', 'year']]


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
            #self.logger.info(f"{dataset_name} - XGBoost Forecast - Model training")
            df = self.df.loc[self.df['dataset_name'] == dataset_name]

            X = df[self.columns]
            y = df['number_charges']
            print(df['number_charges'].describe())

            n_rows = len(df)
            # TODO Pretty rough train-test split
            train_size = int(n_rows * 0.9)
            X_train, X_test = X.iloc[:train_size, :], X.iloc[train_size:, :]
            y_train, y_test = y.iloc[:train_size], y.iloc[train_size:]

            self.logger.info(f'Training Features Shape: {X_train.shape}')
            self.logger.info(f'Training Labels Shape: {X_test.shape}')
            self.logger.info(f'Testing Features Shape: {y_train.shape}')
            self.logger.info(f'Testing Labels Shape: {y_test.shape}')

            # LightGBM parameters
            lgb_params = {'num_leaves': 10,
                          'learning_rate': 0.02,
                          'max_depth': 5,
                          'verbose': 0,
                          'early_stopping_rounds': 200,
                          'nthread': -1}

            lgbtrain = lgb.Dataset(data=X_train, label=y_train, feature_name=self.columns)
            lgbtest = lgb.Dataset(data=X_test, label=y_test, reference=lgbtrain, feature_name=self.columns)

            # Train the model
            lgbm_m = lgb.train(
                lgb_params,
                lgbtrain,
                valid_sets=[lgbtrain, lgbtest],
                callbacks=[lgb.early_stopping(lgb_params['early_stopping_rounds'])]
            )

            y_pred_test = lgbm_m.predict(X_test, num_iteration=lgbm_m.best_iteration)

            errors = abs(y_pred_test - y_test)
            self.logger.info(f'Mean Absolute Error: {round(np.mean(errors), 2)}')
            # Calculate mean absolute percentage error (MAPE) for non-zero labels
            non_zero_indices = y_test != 0
            filtered_errors = errors[non_zero_indices]
            filtered_test_labels = y_test[non_zero_indices]
            # Calculate MAPE
            mape = 100 * np.mean(np.abs(filtered_errors / filtered_test_labels))
            accuracy = 100 - np.mean(mape)
            print("Accuracy " + str(accuracy))

            smape = self.smape(np.expm1(y_pred_test), np.expm1(y_test))
            print("SMAPE " + str(smape))

            model_name = self.get_model_name(prefix=self.name, pilot=dataset_name)

            # Save info
            output_dict['train'].update({
                model_name: {
                    'params': params,
                    'shapes': {
                        'training_features_shape': X_train.shape,
                        'training_labels_shape': X_test.shape,
                        'testing_features_shape': y_train.shape,
                        'testing_labels_shape': y_test.shape,
                    },
                    'model': lgbm_m,
                    'metrics': {
                        'smape': round(smape, 2),
                        'mape': round(mape, 2),
                        'accuracy': round(accuracy, 2)
                    },
                    'artifacts': {
                    }
                }
            })

        self.results.update(output_dict)
        return

    def predict(self):
        output_dict = {'predict': {}}

        input_data = {
            'plug_in_month': self.date.month,
            'plug_in_weekday': self.date.weekday(),
            'avg_energy_2': None,
            'avg_duration_2': None,
            'avg_energy_7': None,
            'avg_duration_7': None
        }

        for dataset_name in self.datasets_names:
            if self.submode == 'schedule':
                self.df = self.df.loc[self.df['dataset_name'] == dataset_name]
                input_data['avg_energy_2'] = self.df['avg_energy_2'].iloc[-1]
                input_data['avg_duration_2'] = self.df['avg_duration_2'].iloc[-1]
                input_data['avg_energy_7'] = self.df['avg_energy_7'].iloc[-1]
                input_data['avg_duration_7'] = self.df['avg_duration_7'].iloc[-1]

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
