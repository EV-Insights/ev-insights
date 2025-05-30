import os
from pprint import pprint
from src.services.service import Service


class IngestionService(Service):
    def __init__(self, name, output_dir, interfaces):
        super().__init__(name=name, output_dir=output_dir, interfaces=interfaces)
        return

    def find_substring(self, list_of_strings, substring):
        return next((stringa for stringa in list_of_strings if substring in stringa), None)

    def run(self):
        self.logger.info("Ingestion service start")

        # Ingest data
        if self.input_interface.input_data_type == 'bulk':
            # Ingest bulk datasets
            for dataset_id, dataset_value in self.input_interface.datasets.items():

                self.logger.info("Ingesting dataset %s" % dataset_value['info']['dataset_name'])

                # Insert dataset details
                try:
                    self.output_interface.insert_dataset_details(data=dataset_value['info'])
                except Exception as e:
                    self.output.append(str(e))

                # Insert charging stations details
                self.output_interface.insert_charging_stations(data=dataset_value['data'],
                                                               dataset_name=dataset_value['info']['dataset_name'])

                # Insert users
                self.output_interface.insert_users(data=dataset_value['data'], dataset_name=dataset_value['info']['dataset_name'])

                # Insert charging sessions
                self.output_interface.insert_charging_sessions(data=dataset_value['data'], dataset_name=dataset_value['info']['dataset_name'])

                # Add here further ingestion if needed
                # ...

            self.output.append("Bulk data ingested successfully")

        elif self.input_interface.input_data_type == 'table':
            # Ingest single tables
            # Ingest tables in this order
            tables = ["Dataset", "User", "ChargingStation", "ChargingSession"]
            for table in tables:
                dataset_path = self.find_substring(self.input_interface.data.keys(), table)
                if dataset_path:
                    dataset_value = self.input_interface.data[dataset_path]

                    self.logger.info(f"Ingesting file: {dataset_value['file_name']}")

                    # TODO it works, but check if this is the proper way to handle the injection of the same entry in dataset table (probably this is ok)
                    if dataset_value['table'] == "Dataset":
                        self.logger.info(f"Ingesting Dataset")
                        try:
                            self.output_interface.insert_dataset_details(data=dataset_value['df'].to_dict('records')[0])
                            self.output.append("Dataset ingested successfully")
                        except Exception as e:
                            self.output.append(str(e))
                            break

                    elif dataset_value['table'] == "User":
                        self.logger.info(f"Ingesting Users")
                        self.output_interface.insert_users(data=dataset_value['df'],
                                                           dataset_name=dataset_value['pilot'])
                        self.output.append("Users ingested successfully")

                    elif dataset_value['table'] == "ChargingStation":
                        self.logger.info(f"Ingesting ChargingStation")
                        self.output_interface.insert_charging_stations(data=dataset_value['df'],
                                                                       dataset_name=dataset_value['pilot'])
                        self.output.append("ChargingStations ingested successfully")

                    elif dataset_value['table'] == "ChargingSession":
                        self.logger.info(f"Ingesting ChargingSession")
                        self.output_interface.insert_charging_sessions(data=dataset_value['df'],
                                                                       dataset_name=dataset_value['pilot'])
                        self.output.append("ChargingSessions ingested successfully")

        self.logger.info("Ingestion service end")

        return self.output
