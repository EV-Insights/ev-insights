import os
import glob
import json
import shutil
from pprint import pprint
from datetime import datetime
from fastapi import APIRouter, Depends
from src.api.v1.models.ingestion import IngestDatasetsParams, IngestDataParams
from src.__main__ import main

# Set base conf
if os.environ["SERVICE_ENVIRONMENT"] == "dev":
    base_conf_folder_path = "conf/api/dev"
elif os.environ["SERVICE_ENVIRONMENT"] == "test":
    base_conf_folder_path = "conf/api/test"
elif os.environ["SERVICE_ENVIRONMENT"] == "prod":
    base_conf_folder_path = "conf/api/prod"
else:
    raise Exception(f"Wrong environment: {os.environ['SERVICE_ENVIRONMENT']}")


router = APIRouter()


@router.post("/ingest_datasets/")
async def ingest_datasets(params: IngestDatasetsParams):
    """
    POST example
    {
        "datasets_list": ["ACN_Caltech", "AMB_Barcellona", "Elaad", "OLEV", "BeLib"],
        "folder_path": "../../data/input/public_datasets/",
        "limit_rows": 1000
    }
    :param params:
    :return:
    """

    # TODO IMPORTANTE: se:
    #  input_interface: limit_rows=0 e lista dataset vuota
    #  output_interface: init_db=true
    #  -> praticamente svuota tutto il db -> ok per il servizio init_db
    #  verificare che i due parametri non siano così settati
    #  --> verificare se è ancora così

    try:
        # Load base conf file
        base_conf_file_path = os.path.join(base_conf_folder_path, "conf_api_ingestdatasets.json")
        if os.path.isfile(base_conf_file_path):
            config = json.loads(open(base_conf_file_path).read().replace("\n", ""))

            # Add dynamic details to the basic conf file
            config["services"]["ingestion"]["interfaces"]["input"]["datasets_list"] = params.datasets_list
            config["services"]["ingestion"]["interfaces"]["input"]["input_dir"] = params.folder_path
            config["services"]["ingestion"]["interfaces"]["input"]["limit_rows"] = params.limit_rows

            output = main(config_json=dict(config))
        else:
            raise FileNotFoundError

        # TODO verify that the list of datasets has been correctly ingested (postgres get unique dataset names)
        return {'message': output if type(output) != Exception else str(output)}

    except Exception as e:
        return {'message': str(e)}


@router.post("/ingest_data/")
async def ingest_data(params: IngestDataParams):
    proc_folder_name = "_proc"
    ingested_folder_name = "_ingested"
    failed_folder_name = "_failed"  # TODO handle file not ingested in case of exceptions

    try:
        pilot = params.pilot_name
        debug_mode = params.debug_mode

        datetime_now = datetime.now()
        datetime_now_str = datetime_now.strftime('%Y%m%d%H%M%S%f')[:-3]

        # Load base conf file
        file_list = []
        base_conf_file_path = os.path.join(base_conf_folder_path, "conf_api_ingestdata.json")
        if os.path.isfile(base_conf_file_path):
            config = json.loads(open(base_conf_file_path).read().replace("\n", ""))

            # Get list of files to be ingested in the db
            input_folder_path = os.path.join(config["services"]["ingestion"]["interfaces"]["input"]["input_dir"], params.pilot_name)

            if not os.path.isdir(input_folder_path):
                raise Exception(f"ERROR: Data not ingested. Input folder not found. Check the pilot_name parameter ({pilot}).")

            # This is only used for debugging mode. If enabled, dummypilot files will be moved to the relative folder for processing
            if debug_mode:
                orig_files_path = os.path.join(input_folder_path, "../")
                pattern_csv = os.path.join(orig_files_path, '*.csv')
                files_csv = glob.glob(pattern_csv)

                # Copia tutti i file trovati nella cartella di destinazione
                for file_csv in files_csv:
                    shutil.copyfile(file_csv, os.path.join(input_folder_path, os.path.basename(file_csv)))

            file_list = glob.glob(os.path.join(input_folder_path, f'*{params.pilot_name}*.csv'))

        # Move files in the "_proc" folder for ingesting, ingest them , then move to _ingested
        if len(file_list) > 0:
            # Create tmp proc folder and ingested folder (if not exist)
            proc_folder_path = os.path.join(input_folder_path, f'{datetime_now_str}{proc_folder_name}')
            if not os.path.isdir(proc_folder_path):
                os.makedirs(proc_folder_path)
            ingested_folder_path = os.path.join(input_folder_path, ingested_folder_name)
            if not os.path.isdir(ingested_folder_path):
                os.makedirs(ingested_folder_path)

            # Set conf parameters
            config["services"]["ingestion"]["interfaces"]["input"]["input_dir"] = proc_folder_path
            config["services"]["ingestion"]["interfaces"]["input"]["datasets_list"] = [pilot]

            # Rename files and move them to <datetime>_proc folder
            for file in file_list:
                new_file_name = f"{datetime_now_str}_{os.path.basename(file)}"
                proc_file_path = os.path.join(proc_folder_path, new_file_name)
                shutil.move(file, proc_file_path)

            # Run ingestion service
            output = main(config_json=dict(config))

            for file in glob.glob(os.path.join(proc_folder_path,  "*")):
                # Rename file and move to <datetime>_proc folder
                shutil.move(file, ingested_folder_path)

            # Remove tmp proc folder
            if os.path.isdir(proc_folder_path):
                shutil.rmtree(proc_folder_path)

        else:
            raise Exception(f"ERROR: Data not ingested. Files not found in the pilot_name folder ({pilot})")

        # TODO verify that the list of datasets has been correctly ingested (postgres get unique dataset names)

        return {'message': output if type(output) != Exception else str(output)}

    except Exception as e:
        return {'message': str(e)}