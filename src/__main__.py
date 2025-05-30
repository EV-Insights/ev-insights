import json
import os
import sys
import argparse
import logging
from shutil import copy
from datetime import datetime
from pathlib import Path
from pprint import pprint
from src.utils.logger import Logger
from src.services.service import init_service
path = os.path.dirname(os.path.dirname(__file__))
sys.path.append(path)


def main(config_file=None, config_json=None):

    service = None
    output = []

    try:
        if config_file is None and config_json is None:
            raise Exception("Please provide config_file_path or config_json")
        elif config_file is not None and config_json is not None:
            raise Exception("Please only provide config_file_path or config_json")

        if config_file is not None:
            config_file_path = config_file
            config_json = json.loads(open(config_file).read().replace("\n", ""))
        elif config_json is not None:
            config_file_path = "api_" + config_json['service']

        datetime_now = datetime.now()

        service_name = config_json['service']
        config = config_json['services'][service_name]

        # Init output dir
        output_dir = os.path.join(config['utils']['output_dir'],
                                  datetime_now.strftime("%Y-%m-%d_%H.%M.%S") + "__" +
                                  Path(os.path.basename(__file__)).stem + "__" +
                                  Path(os.path.basename(config_file_path)).stem)
        config['utils']['output_dir'] = os.path.abspath(output_dir)
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)

        # Init config dir
        config_dir = os.path.join(output_dir, 'config')
        config['utils']['config_dir'] = os.path.abspath(config_dir)
        if not os.path.isdir(config_dir):
            os.makedirs(config_dir)

        # Init log dir
        log_dir = os.path.join(output_dir, config['utils']['logger']['output_dir'])
        config['utils']['logger']['output_dir'] = os.path.abspath(log_dir)
        if not os.path.isdir(log_dir):
            os.makedirs(log_dir)

        # Init interfaces dir
        input_interface_dir = os.path.join(output_dir, config['interfaces']['input']['output_dir'])
        config['interfaces']['input']['output_dir'] = os.path.abspath(input_interface_dir)
        if not os.path.isdir(input_interface_dir):
            os.makedirs(input_interface_dir)
        output_interface_dir = os.path.join(output_dir, config['interfaces']['output']['output_dir'])
        config['interfaces']['output']['output_dir'] = os.path.abspath(output_interface_dir)
        if not os.path.isdir(output_interface_dir):
            os.makedirs(output_interface_dir)
        if "mlflow" in config['interfaces']:
            mlflow_dir = os.path.join(config['utils']['input_dir'], config['interfaces']['mlflow']['mlflow_dir'])
            config['interfaces']['mlflow']['mlflow_dir'] = os.path.abspath(mlflow_dir)
            if not os.path.isdir(mlflow_dir):
                os.makedirs(mlflow_dir)

        # Init service dir
        output_service_dir = os.path.join(output_dir, config['output_dir'])
        config['output_dir'] = os.path.abspath(output_service_dir)
        if not os.path.isdir(output_service_dir):
            os.makedirs(output_service_dir)

        # Init logger
        Logger(config=config['utils']['logger'], filename="main")
        logger = logging.getLogger(__name__)
        logger.info("Start main")

        if config_file is not None:
            # Copy the config file into the output folder
            copy(config_file_path, config_dir)
            # Save also utils config file with full path for any inconvenience
            filename = Path(config_file_path).stem + "_fullpaths.json"
            file_path = os.path.join(config_dir, filename)
            with open(file_path, 'w') as json_file:
                json.dump(config, json_file, indent=4)

        elif config_json is not None:
            # Write config into the output folder
            file_path = os.path.join(config_dir, "api_conf_file.json")
            with open(file_path, 'w') as json_file:
                json.dump(config, json_file, indent=4)

        # Init service
        service = init_service(config=config)

        # Run service
        output_tmp = service.run()
        output.append(output_tmp)

        # Close service (if needed)
        if service is not None:
            service.close_service()

    except Exception as e:
        logging.critical(e, exc_info=True)
        output_tmp = str(e)
        output.append(output_tmp)

    return output


if __name__ == '__main__':
    # Read conf file
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-c', help='configuration file', required=True)

    # Set configuration
    args = arg_parser.parse_args()

    output = main(config_file=args.c)



