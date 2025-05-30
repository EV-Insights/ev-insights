import os
import json
from pprint import pprint
from fastapi import APIRouter, Depends
from src.api.v1.models.admin import DeleteDatasetParams
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


@router.get("/")
async def root():
    return {"message": "Hello from EV-INSIGHTS"}


@router.post("/init_db/")
async def init_db():
    try:
        # Load base conf file
        base_conf_file_path = os.path.join(base_conf_folder_path, "conf_api_initdb.json")
        if os.path.isfile(base_conf_file_path):
            config = json.loads(open(base_conf_file_path).read().replace("\n", ""))

            output = main(config_json=dict(config))
        else:
            raise FileNotFoundError

        return {'message': output if type(output) != Exception else str(output)}

    except Exception as e:
        return {'message': str(e)}


@router.post("/delete_dataset/")
async def delete_dataset(params: DeleteDatasetParams):
    try:
        dataset_name = params.pilot_name
        # Load base conf file
        base_conf_file_path = os.path.join(base_conf_folder_path, "conf_api_deletedataset.json")
        if os.path.isfile(base_conf_file_path):
            config = json.loads(open(base_conf_file_path).read().replace("\n", ""))

            config["services"]["admin"]["admin"][0]["custom_params"]["dataset_name"] = dataset_name

            output = main(config_json=dict(config))
        else:
            raise FileNotFoundError

        return {'message': output if type(output) != Exception else str(output)}

    except Exception as e:
        return {'message': str(e)}
