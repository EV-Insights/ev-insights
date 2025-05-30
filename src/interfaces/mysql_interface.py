import os
import logging
import mysql
import mysql.connector
from src.interfaces.interface import Interface
from src.sql.mysql import sql_query


class MySql(Interface):
    def __init__(self, name, type, init_db, output_dir, host, user, password, database):
        super().__init__(name=name, type=type, output_dir=output_dir)

        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.init_db = init_db
        self.db_schema_path = "src/sql/mysql/schema.sql"
        self.db = self.open_db_connection()

        if self.init_db:
            self.db_initialization()

        return

    def open_db_connection(self):
        # Connect to MySQL server
        connection = mysql.connector.connect(
            host=self.host,
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

    def db_initialization(self):
        logger = logging.getLogger(__name__)
        try:
            # Create a cursor object
            cursor = self.db.cursor()

            # Execute SQL commands from the schema file to create tables and relationships
            schema_file_path = os.path.join(self.db_schema_path)
            self.execute_sql_file(cursor, schema_file_path)

            # Commit the changes
            self.db.commit()

        except mysql.connector.Error as err:
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
        except mysql.connector.Error as err:
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
        # Get charging_point_type_id from DB
        charging_point_type_id = self.get_charging_point_type_id(data['dataset_charging_point_type'])

        # Insert dataset details
        cursor = self.db.cursor()
        data_row = (data['dataset_id'],
                    data['dataset_name'],
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
                    charging_point_type_id,
                    data['dataset_notes'])
        cursor.execute(sql_query.insert_dataset_info, data_row)
        cursor.close()
        self.db.commit()
        return

    def insert_charging_stations(self, data, dataset_id):
        cursor = self.db.cursor()
        data = data.fillna("")  # TODO Should this be performed once before the start of data ingestion?
        charging_stations_data = data[['charging_station_id', 'max_charging_power']].drop_duplicates()
        for index, row in charging_stations_data.iterrows():
            data_row = (row['charging_station_id'] if 'charging_station_id' in row else "",
                        row['manufacturer'] if 'manufacturer' in row else "",
                        row['model'] if 'model' in row else "",
                        row['type'] if 'type' in row else "",
                        row['num_plugs'] if 'num_plugs' in row else "",
                        row['max_charging_power'] if 'max_charging_power' in row else "",
                        row['max_discharging_power'] if 'max_discharging_power' in row else "",
                        dataset_id)
            cursor.execute(sql_query.insert_charging_stations, data_row)
        cursor.close()

        self.db.commit()
        return

    def insert_users(self, data, dataset_id):
        cursor = self.db.cursor()
        data = data.fillna("")  # TODO Should this be performed once before the start of data ingestion?
        users_data = data[['user_id', 'ev_id', 'ev_max_charging_power']].drop_duplicates()
        for index, row in users_data.iterrows():
            data_row = (row['user_id'] if 'user_id' in row else "",
                        row['ev_id'] if 'ev_id' in row else "",
                        row['ev_manufacturer'] if 'ev_manufacturer' in row else "",
                        row['ev_model'] if 'ev_model' in row else "",
                        row['ev_battery_capacity'] if 'ev_battery_capacity' in row else "",
                        row['ev_battery_type'] if 'ev_battery_type' in row else "",
                        row['ev_battery_useable_capacity'] if 'ev_battery_useable_capacity' in row else "",
                        row['ev_v2g'] if 'ev_v2g' in row else "",
                        row['ev_max_charging_power'] if 'ev_max_charging_power' in row else "",
                        row['ev_max_discharging_power'] if 'ev_max_discharging_power' in row else "",
                        dataset_id)
            cursor.execute(sql_query.insert_users, data_row)
        cursor.close()

        self.db.commit()
        return

    def insert_charging_sessions(self, data, dataset_id):
        # Get charging stations ids
        charging_stations = self.get_charging_stations(dataset_id=dataset_id)
        # Get user ids
        users = self.get_users(dataset_id=dataset_id)

        cursor = self.db.cursor()
        data = data.fillna("")  # TODO Should this be performed once before the start of data ingestion?
        charging_sessions_data = data[['plug_in_datetime',
                                       'plug_out_datetime',
                                       'charge_end_datetime',
                                       'energy_supplied',
                                       'ev_max_charging_power',
                                       'charging_station_id',
                                       'user_id', ]].drop_duplicates()
        for index, row in charging_sessions_data.iterrows():
            # Get charging_station_id from charging_stations dict extracted from db
            charging_station_id = charging_stations.get(str(row['charging_station_id']))
            user_id = users.get(str(row['user_id']))
            data_row = (row['plug_in_datetime'],
                        row['plug_out_datetime'],
                        row['charge_end_datetime'],
                        row['energy_supplied'],
                        dataset_id,
                        charging_station_id,
                        user_id,)
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
