import datetime
import os
import logging

import psycopg2
from psycopg2.extras import RealDictCursor

import pandas as pd
from pprint import pprint
from src.interfaces.interface import Interface
from src.sql.postgresql import sql_query

# pd.set_option('display.max_columns', 20)
# pd.set_option('display.max_rows', 300)
# pd.set_option('display.width', 2000)


class PostgreSql(Interface):
    def __init__(self, name, type, output_dir, host, port, user, password, database):
        super().__init__(name=name, type=type, output_dir=output_dir)

        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.schema = self.database = database
        self.db = self.open_db_connection()
        self.dict_stats = {}            # Used to retrieve stats from db
        self.df = pd.DataFrame()        # TODO Used to store data from db (if needed, still unknown)
        self.db_schema_path = "src/sql/postgresql/schema.sql"

        # Map df columns with table attributes
        self.fields_table_map = {
            'dataset_id': 'd.id',
            'dataset_name': 'd.name',
            'dataset_country': 'd.country',
            'plug_in_datetime': 'cse.plug_in_datetime',
            'plug_out_datetime': 'cse.plug_out_datetime',
            'energy_supplied': 'cse.energy_supplied',
            'ev_max_charging_power': 'u.ev_max_charging_power',
            'user_id': 'u.id',
            'station_id': 'cst.id',
            'charging_station_id': 'cst.id'
        }

        return

    def open_db_connection(self):
        # Connect to Postgres server
        connection = psycopg2.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database
        )
        return connection

    def close_interface(self):
        self.close_db_connection()
        return

    def close_db_connection(self):
        if self.db:
            self.db.close()
        return

    def init_db(self):
        logger = logging.getLogger(__name__)
        try:
            # Create a cursor object
            cursor = self.db.cursor()

            # Execute SQL commands from the schema file to create tables and relationships
            schema_file_path = os.path.join(self.db_schema_path)
            self.execute_sql_file(cursor, schema_file_path)

            # Commit the changes
            self.db.commit()

        except psycopg2.Error as err:
            logger.error(f"Error: {err}")

        return

    def execute_sql_file(self, cursor, file_path):
        logger = logging.getLogger(__name__)
        try:
            with open(file_path, 'r') as file:
                sql_commands = file.read().split(';')

                for command in sql_commands:
                    if command.strip():
                        cursor.execute(command)

            logger.info(f"SQL commands from '{file_path}' executed successfully")
        except psycopg2.Error as err:
            logging.getLogger(__name__).info(f"Error executing SQL commands: {err}")

        return

    def insert_charging_point_types(self, data):
        cursor = self.db.cursor()

        # Insert charging point types
        for ch_p_type in data:
            data_row = [ch_p_type]
            cursor.execute(sql_query.insert_charging_point_types, data_row)
        cursor.close()
        self.db.commit()
        return

    def insert_dataset_details(self, data):
        # Get dataset id
        dataset_id = self.get_dataset_id_by_name(dataset_name=data['dataset_name'])

        if dataset_id is None:
            # Insert dataset details
            cursor = self.db.cursor()
            data_row = (data['dataset_name'],
                        data['dataset_url'],
                        data['dataset_description'],
                        data['dataset_owner'],
                        data['dataset_country'],
                        data['dataset_region'],
                        data['dataset_city'],
                        data['dataset_file_name'],
                        data['dataset_file_type'],
                        data['dataset_delimiter'],
                        data['dataset_encoding'],
                        data['dataset_license'],
                        data['dataset_charging_point_type'],
                        data['dataset_notes'])
            cursor.execute(sql_query.insert_dataset_info, data_row)
            cursor.close()
            self.db.commit()
        else:
            raise Exception(f"ERROR: Dataset {data['dataset_name']} already exists.")
        return

    def insert_charging_stations(self, data, dataset_name):
        # Get dataset id
        dataset_id = self.get_dataset_id_by_name(dataset_name=dataset_name)

        cursor = self.db.cursor()
        data = data.fillna("")  # TODO Should this be performed once before the start of data ingestion?
        id_column = 'charging_station_id' if 'charging_station_id' in data.columns else 'id'
        charging_stations_data = data[[id_column, 'max_charging_power']].drop_duplicates()

        for index, row in charging_stations_data.iterrows():
            data_row = (row[id_column] if id_column in row and row[id_column] != '' else None,
                        row['manufacturer'] if 'manufacturer' in row and row['manufacturer'] != '' else None,
                        row['model'] if 'model' in row and row['model'] != '' else None,
                        row['type'] if 'type' in row and row['type'] != '' else None,
                        row['num_plugs'] if 'num_plugs' in row and row['num_plugs'] != '' else None,
                        row['max_charging_power'] if 'max_charging_power' in row and row['max_charging_power'] != '' else None,
                        row['max_discharging_power'] if 'max_discharging_power' in row and row['max_discharging_power'] != '' else None,
                        dataset_id)
            cursor.execute(sql_query.insert_charging_stations, data_row)

        cursor.close()

        self.db.commit()
        return

    def insert_users(self, data, dataset_name):
        # Get dataset id
        dataset_id = self.get_dataset_id_by_name(dataset_name=dataset_name)

        cursor = self.db.cursor()
        data = data.fillna("")  # TODO Should this be performed once before the start of data ingestion?
        users_data = data[['user_id', 'ev_id', 'ev_max_charging_power']].drop_duplicates()

        for index, row in users_data.iterrows():
            data_row = (row['user_id'] if 'user_id' in row and row['user_id'] != '' else None,
                        row['ev_id'] if 'ev_id' in row and row['ev_id'] != '' else None,
                        row['ev_manufacturer'] if 'ev_manufacturer' in row and row['ev_manufacturer'] != '' else None,
                        row['ev_model'] if 'ev_model' in row and row['ev_model'] != '' else None,
                        row['ev_battery_capacity'] if 'ev_battery_capacity' in row and row['ev_battery_capacity'] != '' else None,
                        row['ev_battery_type'] if 'ev_battery_type' in row and row['ev_battery_type'] != '' else None,
                        row['ev_battery_useable_capacity'] if 'ev_battery_useable_capacity' in row and row['ev_battery_useable_capacity'] != '' else None,
                        row['ev_v2g'] if 'ev_v2g' in row and row['ev_v2g'] != '' else None,
                        row['ev_max_charging_power'] if 'ev_max_charging_power' in row and row['ev_max_charging_power'] != '' else None,
                        row['ev_max_discharging_power'] if 'ev_max_discharging_power' in row and row['ev_max_discharging_power'] != '' else None,
                        dataset_id)
            cursor.execute(sql_query.insert_users, data_row)
        cursor.close()

        self.db.commit()
        return

    def insert_charging_sessions(self, data, dataset_name):
        # Get dataset id
        dataset_id = self.get_dataset_id_by_name(dataset_name=dataset_name)

        # Get charging stations ids
        charging_stations = self.get_charging_stations(dataset_id=dataset_id)
        # Get user ids
        users = self.get_users(dataset_id=dataset_id)

        cursor = self.db.cursor()
        data = data.fillna("")  # TODO Should this be performed once before the start of data ingestion?
        charging_sessions_data = data[['plug_in_datetime',
                                       'plug_out_datetime',
                                       'charge_end_datetime',
                                       'charge_end_datetime_presence',
                                       'energy_supplied',
                                       'charging_station_id',
                                       'user_id', ]].drop_duplicates()

        for index, row in charging_sessions_data.iterrows():
            # Get charging_station_id from charging_stations dict extracted from db
            charging_station_id = charging_stations.get(str(row['charging_station_id']))
            user_id = users.get(str(row['user_id']))
            try:
                data_row = (row['plug_in_datetime'] if 'plug_in_datetime' in row and not pd.isna(row['plug_in_datetime']) and not row['plug_in_datetime'] == ''  else None,
                            row['plug_out_datetime'] if 'plug_out_datetime' in row and not pd.isna(row['plug_out_datetime']) and not row['plug_out_datetime'] == ''  else None,
                            row['charge_end_datetime'] if 'charge_end_datetime' in row and not pd.isna(row['charge_end_datetime']) and not row['charge_end_datetime'] == '' else None,
                            row['charge_end_datetime_presence'],
                            row['energy_supplied'] if 'energy_supplied' in row and row['energy_supplied'] != '' else None,
                            dataset_id,
                            charging_station_id,
                            user_id,)
            except Exception as e:
                self.logger.warn(e)
                self.logger.warn(dataset_name + " " + str(row))
                continue

            cursor.execute(sql_query.insert_charging_sessions, data_row)
        cursor.close()

        self.db.commit()
        return

    def get_charging_point_type_id(self, charging_point_type):
        cursor = self.db.cursor()
        cursor.execute(sql_query.get_charging_point_type_id_by_type, [charging_point_type])
        charging_point_type_id = cursor.fetchone()[0]
        cursor.close()
        return charging_point_type_id

    def get_charging_stations(self, dataset_id):
        cursor = self.db.cursor()
        cursor.execute(sql_query.get_charging_stations, [dataset_id])
        charging_stations = cursor.fetchall()
        charging_stations = dict((y, x) for x, y in charging_stations)
        cursor.close()
        return charging_stations

    def get_users(self, dataset_id):
        cursor = self.db.cursor()
        cursor.execute(sql_query.get_users, [dataset_id, dataset_id])
        users = cursor.fetchall()
        users = dict((y, x) for x, y in users)
        cursor.close()
        return users

    def get_dataset_id_by_name(self, dataset_name):
        cursor = self.db.cursor()
        cursor.execute(sql_query.get_dataset_id_by_name, [dataset_name])
        dataset_id = cursor.fetchone()
        cursor.close()
        return dataset_id[0] if dataset_id is not None else None

    def get_dataset_name_by_id(self, dataset_id):
        cursor = self.db.cursor()
        cursor.execute(sql_query.get_dataset_name_by_id, [dataset_id])
        dataset_name = cursor.fetchone()
        cursor.close()
        return dataset_name[0] if dataset_name is not None else None

    def get_dataset_list(self):
        cursor = self.db.cursor()
        cursor.execute(sql_query.get_dataset_list)
        rows = cursor.fetchall()
        dataset_list = [row[0] for row in rows]
        cursor.close()
        return dataset_list

    def get_stats(self):
        cursor = self.db.cursor()
        cursor.execute(sql_query.get_number_of_tables)
        charging_point_type_id = cursor.fetchall()
        cursor.close()
        return charging_point_type_id

    def check_column_existence(self, column):
        cursor = self.db.cursor()
        cursor.execute(sql_query.check_column_existence, [column])
        tables = cursor.fetchall()
        cursor.close()
        return len(tables) > 0

    def dynamic_query(self, fields, datasets, datetime_from=None, datetime_to=None, user_id=None, station_id=None):
        query = sql_query.dynamic_query % (fields, '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')
        cursor = self.db.cursor()

        formatted_query = query % (
            tuple(datasets), datetime_from, datetime_from, datetime_to, datetime_to, user_id, user_id, station_id, station_id
        )
        self.logger.info("Executing query: %s", formatted_query)

        cursor.execute(query, (tuple(datasets), datetime_from, datetime_from, datetime_to, datetime_to, user_id, user_id, station_id, station_id))
        res = cursor.fetchall()
        cursor.close()
        return res

    def get_data(self, data_selection: dict):

        df = None

        # Get list of available datasets
        datasets_available_names = self.get_dataset_list()

        # Fill datasets_list with all datasets (use all available data) in case datasets param is missing or void
        datasets_names_filter = data_selection['datasets'] \
            if ('datasets' in data_selection and len(data_selection['datasets']) > 0) else datasets_available_names

        for datasets_name in datasets_names_filter:
            if datasets_name not in datasets_available_names:
                raise Exception("Dataset '%s' is not available. Available datasets: %s" % (datasets_name, datasets_available_names))

        # Obsolete code
        # if len(data_selection['fields']) == 1 and data_selection['fields'][0] == "stats":
        #     # Ignore getting data since this is just used to retrieve stats from db
        #     self.logger.info("Get stats from DB")
        #     self.dict_stats = self.get_stats()
        #
        # else:
        table_fields = []

        # Check if all fields exist in the db
        for field in data_selection['fields']:
            if not self.check_column_existence(column=field) and False:  # TODO check: added "and False" to skip this check. Why is this still there?
                raise Exception(f"ERROR: field {field} does not exist in db. Please check conf file, data_selection, fields")
            else:
                if field in self.fields_table_map:
                    table_fields.append(self.fields_table_map[field])
                else:
                    raise Exception(f"ERROR: field {field} does not exist in db, neither in fields_table_map {self.fields_table_map} "
                                    f"Please check conf file, data_selection, fields")

        # Add dataset name column
        table_fields.insert(0, 'd.name') if 'd.name' not in table_fields else table_fields

        datasets = data_selection['datasets'] if len(data_selection['datasets']) > 0 else self.get_dataset_list()

        # Add filters
        datetime_from = None
        datetime_to = None
        user_id = None
        station_id = None
        if 'plug_in_datetime' in data_selection['fields']:
            datetime_from = data_selection['fields']['plug_in_datetime']['from'] \
                if (data_selection['fields']['plug_in_datetime'] is not None and
                    'from' in data_selection['fields']['plug_in_datetime'].keys()) else None
            datetime_from = datetime.datetime.strptime(datetime_from, "%Y-%m-%d") if datetime_from is not None else None
            datetime_to = data_selection['fields']['plug_in_datetime']['to'] \
                if (data_selection['fields']['plug_in_datetime'] is not None and
                    'to' in data_selection['fields']['plug_in_datetime'].keys()) else None
            datetime_to = datetime.datetime.strptime(datetime_to, "%Y-%m-%d") if datetime_to is not None else None
        if 'user_id' in data_selection['fields']:
            user_id = data_selection['fields']['user_id']
        if 'station_id' in data_selection['fields']:
            station_id = data_selection['fields']['station_id']

        data = self.dynamic_query(fields=", ".join(table_fields),
                                  datasets=datasets,
                                  datetime_from=datetime_from,
                                  datetime_to=datetime_to,
                                  user_id=user_id,
                                  station_id=station_id)

        # Create df and rename column based on map
        df_columns = []
        for field in table_fields:
            key = next((k for k, v in self.fields_table_map.items() if v == field), None)
            df_columns.append(key)
        df = pd.DataFrame(data, columns=df_columns)

        if 'plug_in_datetime' in df.columns:
            df = df.sort_values(by=['dataset_name', 'plug_in_datetime'])

        # Check merge_dataset param and unify data in a single dataset "Dataset_merged" if true
        if data_selection['merge_datasets']:
            df['dataset_name'] = "Dataset_merged"

        return df

    def delete_dataset(self, dataset_name):
        # TODO
        return

    def save_forecast_prediction(self, forecaster_name, actor, model, experiment_id, run_id, results, algo):
        self.logger.info(f"Saving predict results to PostreSQL DB")

        cursor = self.db.cursor()

        if actor == 'user':
            data_row = (results['predict']['date'],
                        results['predict']['energy'] if 'energy' in results['predict'].keys() else None,
                        results['predict']['duration'] if 'duration' in results['predict'].keys() else None,
                        experiment_id,
                        run_id,
                        results['predict']['created_at'],
                        results['predict']['id'])
            cursor.execute(sql_query.insert_user_forecast, data_row)

        elif actor == "charging_station":
            data_row = (results['predict']['date'],
                        results['predict']['energy'] if 'energy' in results['predict'].keys() else None,
                        results['predict']['connections'] if 'connections' in results['predict'].keys() else None,
                        experiment_id,
                        run_id,
                        results['predict']['created_at'],
                        results['predict']['id'])
            cursor.execute(sql_query.insert_charging_station_forecast, data_row)

        cursor.close()
        self.db.commit()

        return

    def get_prediction(self, actor, actor_id, date):
        cursor = self.db.cursor(cursor_factory=RealDictCursor)

        if actor.lower() == "user":
            cursor.execute(sql_query.get_user_prediction, [actor_id, date])
        elif actor.lower() == "charging_station":
            cursor.execute(sql_query.get_charging_station_prediction, [actor_id, date])
        else:
            raise Exception(f"Wrong actor {actor}, please select 'user' or 'charging_station'")

        prediction = cursor.fetchone()
        cursor.close()
        return dict(prediction)

    def get_actor_ids(self, actor, dataset_id):
        cursor = self.db.cursor(cursor_factory=RealDictCursor)

        if actor.lower() == "user":
            cursor.execute(sql_query.get_user_ids, [dataset_id, dataset_id])
        elif actor.lower() == "charging_station":
            cursor.execute(sql_query.get_charging_station_ids, [dataset_id, dataset_id])
        else:
            raise Exception(f"Wrong actor {actor}, please select 'user' or 'charging_station'")

        ids = cursor.fetchall()
        cursor.close()
        ids_list = [value for row in ids for value in row.values()]
        return ids_list
