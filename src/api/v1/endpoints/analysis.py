import os
import json
from pprint import pprint
from fastapi import APIRouter, Depends
from src.api.v1.models.analysis import Stats
from src.__main__ import main
from src.celery_apps.tasks.analysis_tasks import stats_task


# Set base conf
if os.environ["SERVICE_ENVIRONMENT"] == "dev":
    base_conf_folder_path = "conf/api/dev"
elif os.environ["SERVICE_ENVIRONMENT"] == "test":
    base_conf_folder_path = "conf/api/testa"
elif os.environ["SERVICE_ENVIRONMENT"] == "prod":
    base_conf_folder_path = "conf/api/prod"
else:
    raise Exception(f"Wrong environment: {os.environ['SERVICE_ENVIRONMENT']}")


router = APIRouter()


# @router.get("/users/{user_id}/", tags=["users"])
# async def get_user(user_id: int):
#     # Logic to retrieve user data
#     return {"user_id": user_id, "name": "Pinco Pallino"}


@router.post("/stats/")
async def stats(params: Stats):
    """
        POST example
        {
            "entity": ['db', 'dataset', 'user', 'chargingstation']
            "id": <entity_id>  (except for db entity)
        }
        :param params:
        :return:
        """

    try:
        # Load base conf file
        base_conf_file_path = os.path.join(base_conf_folder_path, "conf_api_stats.json")
        if os.path.isfile(base_conf_file_path):
            config = json.loads(open(base_conf_file_path).read().replace("\n", ""))

            # Customize conf file based on entity value
            if params.entity == 'db':
                config["services"]["analysis"]["analysis"][0]["full_custom_mode"] = True

            elif params.entity == 'user':
                config["services"]["analysis"]["analysis"][0]["full_custom_mode"] = True
                config["services"]["analysis"]["analysis"][0].update({"data_selection": {
                                                                        "datasets": [],
                                                                        "merge_datasets": False,
                                                                        "fields": {
                                                                            "user_id": None,
                                                                            "plug_in_datetime": None,
                                                                            "plug_out_datetime": None,
                                                                            "energy_supplied": None
                                                                        }}})
                config["services"]["analysis"]["analysis"][0].update({"custom_params": {"entity": params.entity,
                                                                                        "id": params.id,
                                                                                        "plug_duration": None,
                                                                                        }})

            elif params.entity == 'dataset':
                config["services"]["analysis"]["analysis"][0]["full_custom_mode"] = True
                config["services"]["analysis"]["analysis"][0].update({"data_selection": {
                                                                         "datasets": [],
                                                                         "merge_datasets": False,
                                                                         "fields": {
                                                                             "dataset_name": None,
                                                                             "user_id": None,
                                                                             "plug_in_datetime": {
                                                                                 "from": None,
                                                                                 "to": None
                                                                             },
                                                                             "plug_out_datetime": {
                                                                                 "from": None,
                                                                                 "to": None
                                                                             },
                                                                            "energy_supplied": None
                                                                         }}})

                config["services"]["analysis"]["analysis"][0].update({"custom_params": {"entity": params.entity,
                                                                                        "id": params.id,
                                                                                        "plug_duration": None,
                                                                                        "energy_supplied_clip": {
                                                                                            "min": 0,
                                                                                            "max": 100
                                                                                        }}})
                print()

            elif params.entity == 'chargingstation':
                # TODO
                print()

            # Run stats
            output = main(config_json=dict(config))
            # output = stats_task.delay(dict(config))

        else:
            raise FileNotFoundError

        # return {'message': output if type(output) != Exception else str(output)}
        # return {'message': output.task_id}
        return {'message': output}

    except Exception as e:
        return {'message': str(e)}


@router.post("/get_dataset_list/")
async def get_dataset_list():
    # TODO is this the right place for this API? Admin would be better?
    # TODO implementation needed
    return {'message': 'API under construction...'}
