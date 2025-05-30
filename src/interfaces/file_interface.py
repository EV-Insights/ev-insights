import logging
import os
import json
import glob
import logging
import csv
import pandas as pd
from pprint import pprint
from datetime import datetime, timedelta
from dateutil import parser
from src.interfaces.interface import Interface
from src.utils.globals import DATAFRAME_COLUMNS


class File(Interface):
    """
    A class to handle file-based data ingestion and processing for datasets.

    Attributes:
        input_dir (str): Directory containing input files.
        limit_rows (int): Maximum number of rows to read from each dataset.
        input_data_type (str): Type of input data ('bulk' or 'table').
        datasets_details_file (str): Path to the file containing dataset metadata.
        datasets_list (list): List of dataset names to process.
        datasets (dict): Dictionary containing processed datasets.
        df (pd.DataFrame): Combined DataFrame of all processed datasets.
    """
    def __init__(self, name, type, input_dir, output_dir, limit_rows, input_data_type, datasets_list, datasets_details_file):
        """
        Initializes the File interface for data ingestion and processing.

        Args:
            name (str): Name of the interface.
            type (str): Type of the interface ('input' or 'output').
            input_dir (str): Directory containing input files.
            output_dir (str): Directory for output files.
            limit_rows (int): Maximum number of rows to read from each dataset.
            input_data_type (str): Type of input data ('bulk' or 'table').
            datasets_list (list): List of dataset names to process.
            datasets_details_file (str): Path to the file containing dataset metadata.
        """
        super().__init__(name=name, type=type, output_dir=output_dir)
        self.input_dir = input_dir
        self.limit_rows = limit_rows
        self.input_data_type = input_data_type

        # Data gathering from files
        if self.type == "input":
            self.datasets_details_file = datasets_details_file
            self.datasets_list = datasets_list

            if self.input_data_type == 'bulk':
                # Get bulk dataset
                self.datasets = self.get_datasets_from_files(datasets_list=datasets_list,
                                                             datasets_details_file=self.datasets_details_file,
                                                             limit_rows=self.limit_rows)
                self.datasets = self.prepare_datasets()
                self.df = self.convert_datasets_in_df()

            elif self.input_data_type == 'table':
                # Get data structured in tables (dataset, user, chargingstation, chargingsession)
                self.logger.info(f"Ingest files from this folder {self.input_dir}")
                self.file_list = glob.glob(os.path.join(self.input_dir,  "*.csv"))

                self.data = {}
                for file_path in self.file_list:
                    file_name = os.path.basename(file_path)
                    self.data.update({file_path: {'file_name': file_name,
                                                  'pilot': file_name.split("_")[1] if len(file_name.split("_")) == 3 else file_name.split("_")[0],
                                                  'table': (file_name.split("_")[2] if len(file_name.split("_")) == 3 else file_name.split("_")[1]).split(".")[0],
                                                  'df': pd.read_csv(filepath_or_buffer=file_path, delimiter=",", encoding='utf-8')}})
            else:
                raise Exception(f"Wrong input_data_type ({self.input_data_type}). Please specify 'bulk' or 'table'")

        return

    def close_interface(self):
        """
        Placeholder method for closing the interface.
        """
        return

    def sort_list(self, file_path):
        """
        Sorts a list of files based on a priority map.

        Args:
            file_path (str): Path to the file.

        Returns:
            int: Priority value for sorting.
        """
        file_name = os.path.basename(file_path).lower()
        for key in self.priority_map:
            if key in file_name:
                return self.priority_map[key]
        return float('inf')

    def convert_datasets_in_df(self):
        """
        Converts all datasets into a single DataFrame.

        Returns:
            pd.DataFrame: Combined DataFrame of all datasets.
        """
        df = pd.DataFrame()
        for dataset_id, dataset_value in self.datasets.items():

            # Add data to df
            df_tmp = dataset_value['data']

            # Add info to df
            i = 0
            for key in dataset_value['info'].keys():
                df_tmp.insert(i, key, dataset_value['info'][key])
                i += 1

            df = pd.concat([df, df_tmp]).reset_index(drop=True)

        return df

    def get_datasets_from_files(self, datasets_list, datasets_details_file, limit_rows=None):
        """
        Reads datasets from files based on metadata and returns them as a dictionary.

        Args:
            datasets_list (list): List of dataset names to process.
            datasets_details_file (str): Path to the file containing dataset metadata.
            limit_rows (int, optional): Maximum number of rows to read.

        Returns:
            dict: Dictionary containing dataset metadata and data.
        """
        datasets_details = {}
        with open(datasets_details_file, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            datasets_details = [row for row in reader if row['dataset_name'] in datasets_list]

        datasets = {}
        for dataset_info in datasets_details:
            self.logger.info("Gathering '%s' dataset" % dataset_info['dataset_name'])
            inputfile = os.path.join(self.input_dir, dataset_info['dataset_name'], dataset_info.get('dataset_file_name'))
            self.logger.info(inputfile)

            if os.path.exists(inputfile):
                df_orig = pd.DataFrame()
                if dataset_info.get('dataset_file_type') == 'csv':
                    df_orig = pd.read_csv(filepath_or_buffer=str(inputfile), delimiter=dataset_info.get('dataset_delimiter'),
                                          encoding=dataset_info.get('dataset_encoding'), nrows=limit_rows)

                if dataset_info.get('dataset_file_type') == 'xlsx':
                    df_orig = pd.read_excel(io=str(inputfile), sheet_name=dataset_info['dataset_sheet_name'],
                                            engine='openpyxl', nrows=limit_rows)

                if dataset_info.get('dataset_file_type') == 'json':
                    with open(inputfile) as data_file:
                        data = json.load(data_file)
                    # TODO: Generalize "items" json flattening may be an issue
                    df_orig = pd.json_normalize(data, '_items').head(self.limit_rows)

                if df_orig is not None:
                    datasets.update({dataset_info['dataset_name']: {"info": dataset_info,
                                                                  "data": df_orig}})
            else:
                raise Exception("File '%s' does not exist. Please check dataset name '%s' and file name '%s'" %
                                (inputfile, dataset_info['dataset_name'], dataset_info.get('dataset_file_name')))

        return datasets

    def get_data(self, data_selection: dict):
        """
        Retrieves data based on the specified selection criteria.

        Args:
            data_selection (dict): Dictionary specifying datasets and fields to retrieve.

        Returns:
            pd.DataFrame: Filtered DataFrame based on the selection criteria.
        """
        # Get list of available datasets
        datasets_available_names = self.df['dataset_name'].unique()

        # Fill datasets_list in case datasets param is missing or void
        datasets_names_filter = data_selection['datasets'] \
            if ('datasets' in data_selection and len(data_selection['datasets']) > 0) else datasets_available_names

        for datasets_name in datasets_names_filter:
            if datasets_name not in datasets_available_names:
                raise Exception("Dataset '%s' is not available. Available datasets: %s" % (datasets_name, datasets_available_names))

        # Get list of available fields
        fields_available_names = self.df.columns

        # Fill fields in case field param is missing or void
        datasets_fields_filter = data_selection['fields'] \
            if ('fields' in data_selection and len(data_selection['fields']) > 0) else fields_available_names

        # Check columns existence
        for field in datasets_fields_filter:
            if field not in fields_available_names:
                raise Exception("Field '%s' is not available. Available fields: %s" % (field, fields_available_names))

        # Add dataset name columns in any case
        datasets_fields_filter['dataset_name'] = None if 'dataset_name' not in datasets_fields_filter else None

        # Check merge_dataset param and unify data in a single dataset "Dataset_merged" if true
        if data_selection['merge_datasets']:
            self.df['dataset_name'] = "Dataset_merged"

        return self.df.loc[:, datasets_fields_filter.keys()]

    def convert_date(self, date_string):
        """
        Converts a date string with a shortened year format to a full datetime object.

        Args:
            date_string (str): The input date string with a shortened year (e.g., '23-01-01').

        Returns:
            pd.Timestamp: The converted datetime object.
        """
        # Rimuovi i primi due caratteri dall'anno e aggiungi "20" prima di convertire
        date_string_with_2000 = "20" + date_string[2:]
        # Converti la stringa di data in formato datetime
        return pd.to_datetime(date_string_with_2000, format='%Y-%m-%d %H:%M:%S')

    def prepare_dataset_amb_barcellona(self, df):
        """
        Prepares the dataset for the 'AMB_Barcellona' source by renaming columns and adding required fields.

        Args:
            df (pd.DataFrame): The input DataFrame containing raw data.

        Returns:
            pd.DataFrame: The processed DataFrame with standardized columns and additional fields.
        """
        df.rename(columns={'CONSUMPTION (kWh)': 'energy_supplied',
                           'CHARGING POINT': 'charging_station_id',
                           'Pmax': 'max_charging_power'}, inplace=True)
        df['plug_in_datetime'] = (pd.to_datetime(df["START TIME"], dayfirst=True).astype('string') + " " +
                                  df['ora'].astype('string') + ":" + df['Mins'].astype('string'))
        df['plug_in_datetime'] = pd.to_datetime(df['plug_in_datetime'], format='%Y-%m-%d %H:%M')
        df['charge_end_datetime'] = df['plug_in_datetime'] + df['DURATION (min)'].apply(lambda x: timedelta(minutes=x))
        df['plug_out_datetime'] = df['charge_end_datetime']
        df['charge_end_datetime_presence'] = False
        df['user_id'] = pd.NA
        df['ev_id'] = pd.NA
        df['ev_max_charging_power'] = pd.NA
        df = df[DATAFRAME_COLUMNS]
        return df

    def prepare_dataset_olev(self, df):
        """
        Prepares the dataset for the 'OLEV' source by renaming columns and adding required fields.

        Args:
            df (pd.DataFrame): The input DataFrame containing raw data.

        Returns:
            pd.DataFrame: The processed DataFrame with standardized columns and additional fields.
        """
        df.rename(columns={'Energy': 'energy_supplied',
                           'CPID': 'charging_station_id'}, inplace=True)
        df['plug_in_datetime'] = pd.to_datetime(df.StartDate + " " + df.StartTime, format='%Y-%m-%d %H:%M:%S')
        df['charge_end_datetime'] = pd.to_datetime(df.EndDate + " " + df.EndTime, format='%Y-%m-%d %H:%M:%S')
        df['plug_out_datetime'] = df['charge_end_datetime']
        df['charge_end_datetime_presence'] = False
        df['user_id'] = pd.NA
        df['max_charging_power'] = pd.NA
        df['ev_id'] = pd.NA
        df['ev_max_charging_power'] = pd.NA
        df = df[DATAFRAME_COLUMNS]
        return df

    def prepare_dataset_harvard_dataverse(self, df):
        """
        Prepares the dataset for the 'Harvard Dataverse' source by renaming columns and adding required fields.

        Args:
            df (pd.DataFrame): The input DataFrame containing raw data.

        Returns:
            pd.DataFrame: The processed DataFrame with standardized columns and additional fields.
        """
        df.rename(columns={'kwhTotal': 'energy_supplied',
                           'stationId': 'charging_station_id',
                           'userId': 'user_id'}, inplace=True)
        df['plug_in_datetime'] = df['created'].apply(lambda x: self.convert_date(x))
        df['charge_end_datetime'] = df['ended'].apply(lambda x: self.convert_date(x))
        df['plug_out_datetime'] = df['charge_end_datetime']
        df['charge_end_datetime_presence'] = False
        df['max_charging_power'] = pd.NA
        df['ev_id'] = pd.NA
        df['ev_max_charging_power'] = pd.NA
        df = df[DATAFRAME_COLUMNS]
        return df

    def prepare_dataset_Elaad(self, df):
        """
        Prepares the dataset for the 'Elaad' source by renaming columns and adding required fields.

        Args:
            df (pd.DataFrame): The input DataFrame containing raw data.

        Returns:
            pd.DataFrame: The processed DataFrame with standardized columns and additional fields.
        """
        df.rename(columns={'TotalEnergy': 'energy_supplied',
                           'MaxPower': 'ev_max_charging_power',
                           'StartCard': 'user_id'},
                  inplace=True)
        df['plug_in_datetime'] = pd.to_datetime(df.UTCTransactionStart, dayfirst=True)
        df['charge_end_datetime'] = pd.to_datetime(df.UTCTransactionStop, dayfirst=True)
        df['plug_out_datetime'] = df['charge_end_datetime']
        df['charge_end_datetime_presence'] = False
        df['charging_station_id'] = df.apply(lambda row: '{}_{}'.format(row['ChargePoint'], row['Connector']), axis=1)
        df['ev_id'] = pd.NA
        df['max_charging_power'] = pd.NA
        df = df[DATAFRAME_COLUMNS]
        return df

    def prepare_dataset_belib(self, df):
        """
        Prepares the dataset for the 'BeLib' source by renaming columns and adding required fields.

        Args:
            df (pd.DataFrame): The input DataFrame containing raw data.

        Returns:
            pd.DataFrame: The processed DataFrame with standardized columns and additional fields.
        """
        df.rename(columns={'Prise de courant': 'max_charging_power',
                           'Borne': 'charging_station_id',
                           'UUID Badge': 'user_id'},
                  inplace=True)
        df['plug_in_datetime'] = df['Date de début'].apply(lambda x: pd.to_datetime(parser.parse(x))).dt.tz_localize(None)
        df['charge_end_datetime'] = df['Date de fin'].apply(lambda x: pd.to_datetime(parser.parse(x))).dt.tz_localize(None)
        df['plug_out_datetime'] = df['charge_end_datetime']
        df['charge_end_datetime_presence'] = False
        df['energy_supplied'] = df["L'énergie (Wh)"] / 1000
        df['ev_id'] = pd.NA
        df['ev_max_charging_power'] = pd.NA
        df = df[DATAFRAME_COLUMNS]
        return df

    def prepare_dataset_ACN_Caltech(self, df):
        """
        Prepares the dataset for the 'ACN_Caltech' source by renaming columns and adding required fields.

        Args:
            df (pd.DataFrame): The input DataFrame containing raw data.

        Returns:
            pd.DataFrame: The processed DataFrame with standardized columns and additional fields.
        """
        df.rename(columns={"kWhDelivered": "energy_supplied",
                           "stationID": "charging_station_id",
                           "userID": "user_id"},
                  inplace=True)
        df['plug_in_datetime'] = pd.to_datetime(df.connectionTime)
        df['charge_end_datetime'] = pd.to_datetime(df.doneChargingTime)
        df['plug_out_datetime'] = pd.to_datetime(df.disconnectTime)
        df['charge_end_datetime_presence'] = True
        df['max_charging_power'] = pd.NA
        df['ev_id'] = pd.NA
        df['ev_max_charging_power'] = pd.NA
        df = df[DATAFRAME_COLUMNS]
        return df

    def prepare_dataset_Norway_12loc(self, df):
        """
        Prepares the dataset for the 'Norway_12loc' source by renaming columns and adding required fields.

        Args:
            df (pd.DataFrame): The input DataFrame containing raw data.

        Returns:
            pd.DataFrame: The processed DataFrame with standardized columns and additional fields.
        """
        df.rename(columns={"energy_session": "energy_supplied"},
                  inplace=True)
        df['charging_station_id'] = df.user_id  # in this dataset the charging_station_id is missing, since the charging stations are private we can use the user_id
        df['plug_in_datetime'] = pd.to_datetime(df.plugin_time)
        df['charge_end_datetime'] = pd.to_datetime(df.plugout_time)
        df['plug_out_datetime'] = df['charge_end_datetime']
        df['charge_end_datetime_presence'] = False
        df['max_charging_power'] = pd.NA
        df['ev_id'] = pd.NA
        df['ev_max_charging_power'] = pd.NA
        df = df[DATAFRAME_COLUMNS]
        return df

    # Here you can add other datasets
    # def prepare_dataset_<new_dataset_name>(self, df):
    #     ...
    #     return df

    def check_dataset_columns(self, df):
        """
        Validates that the DataFrame contains the expected columns.

        Args:
            df (pd.DataFrame): The DataFrame to validate.

        Returns:
            bool: True if the DataFrame contains the expected columns.

        Raises:
            ValueError: If the DataFrame does not contain the expected columns.
        """
        if set(df.columns) == set(DATAFRAME_COLUMNS):
            return True
        else:
            raise ValueError("Columns are not properly set\n"
                             "Expected columns: %s\n"
                             "df.columns=%s"
                             % (DATAFRAME_COLUMNS, df.columns.tolist()))

    def prepare_datasets(self):
        """
        Prepares datasets by applying specific transformations based on dataset names.

        Returns:
            dict: Dictionary of transformed datasets.
        """
        new_datasets = {}
        for dataset_id, dataset_value in self.datasets.items():
            match dataset_value['info']['dataset_name']:
                case 'AMB_Barcellona':
                    df = self.prepare_dataset_amb_barcellona(df=dataset_value['data'])

                case 'BeLib':
                    df = self.prepare_dataset_belib(df=dataset_value['data'])

                case 'Elaad':
                    df = self.prepare_dataset_Elaad(df=dataset_value['data'])

                # TODO
                #  case 'Hanse_und_Universitaetsstadt_Rostock':
                #     df = prepare_dataset_hanse_und_universitaetsstadt_rostock(df=dataset_value['data'])

                case 'Harvard_dataverse':
                    df = self.prepare_dataset_harvard_dataverse(df=dataset_value['data'])

                case 'OLEV':
                    df = self.prepare_dataset_olev(df=dataset_value['data'])

                case 'ACN_Caltech':
                    df = self.prepare_dataset_ACN_Caltech(df=dataset_value['data'])

                case 'Norway_12loc':
                    df = self.prepare_dataset_Norway_12loc(df=dataset_value['data'])

                # Here you can add other datasets
                # case '<new_dataset_name>':
                #     df = self.prepare_dataset_<new_dataset_name>(df=dataset_value['data'])

                case _:
                    raise ValueError("Wrong dataset name: %s" % dataset_value['info']['dataset_name'])

            # Check dataset columns
            if self.check_dataset_columns(df):
                if 'plug_in_datetime' in df.columns:
                    df = df.sort_values(by='plug_in_datetime')
                new_datasets.update({dataset_id: {"info": dataset_value['info'], "data": df}})

        return new_datasets

    def save_forecast_model(self, forecaster_name, results, file_path, algo=None):
        """
        Saves the forecast model outputs to a file.

        Args:
            forecaster_name (str): The name of the forecaster.
            results (dict): A dictionary containing the training results, where each key is a model name
                            and the value is a dictionary with model details.
            file_path (str): The base file path where the model files will be saved.
            algo (str, optional): The algorithm used for forecasting (not currently utilized).

        Workflow:
            1. Iterates through the models in the training results.
            2. Constructs a unique filename for each model.
            3. If a file with the same name already exists, renames the old file with a timestamp.
            4. Saves the model to the specified file path.
        """
        for model_name, output in results['train'].items():
            model_filename = f"{model_name}.ubj"
            custom_file_path_name = os.path.join(os.path.dirname(file_path), model_filename)
            # Rename existing files, if present, to keep track old models
            if os.path.exists(custom_file_path_name):  # TODO flag per mantenere o meno vecchi modelli
                path = os.path.dirname(custom_file_path_name)
                new_file_name = f'{os.path.basename(custom_file_path_name)}.{datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]}'
                new_file_path_name = os.path.join(path, new_file_name)
                os.rename(custom_file_path_name, new_file_path_name)
            # Save model to file
            model = output['model']
            model.save_model(custom_file_path_name)

        return

    def get_model(self):
        # TODO to be implemented
        return
