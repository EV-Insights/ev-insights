import os
import json
import logging
from pprint import pprint
from fastapi import APIRouter, Depends
from src.api.v1.models.forecast import TrainModelsDataParams, PredictModelsDataParams
from src.__main__ import main
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.executors.pool import ThreadPoolExecutor


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

if bool(os.environ["SCHEDULE_ENABLED"]) == True:
    scheduler = AsyncIOScheduler()


@router.post("/train/")
async def train(params: TrainModelsDataParams):
    try:
        # Load base conf file
        base_conf_file_path = os.path.join(base_conf_folder_path, f"conf_api_forecast_train.json")

        if os.path.isfile(base_conf_file_path):
            config = json.loads(open(base_conf_file_path).read().replace("\n", ""))

            # Add dynamic details to the base conf file
            # Set dataset_name
            if params.dataset_name is not None:
                config["services"]["forecast"]["interfaces"]["input"]["datasets_list"] = params.dataset_name

            # Enable the right forecaster and delete others
            forecaster = next((item for item in config["services"]["forecast"]["forecast"] if item["name"] == params.forecaster), None)

            # Enable forecaster
            forecaster['enabled'] = True

            # Set datasets/pilots
            forecaster['data_selection']['datasets'] = [params.dataset_name]

            # Set forecaster to conf
            config["services"]["forecast"]["forecast"] = [forecaster]

            # Run forecaster
            output = main(config_json=dict(config))

        else:
            raise FileNotFoundError

        return {'message': output if type(output) != Exception else str(output)}

    except Exception as e:
        return {'message': str(e)}


@router.post("/predict/")
async def predict(params: PredictModelsDataParams):
    print(f"Predict is running: {params}")

    try:
        mode = params.mode
        # Load base conf file
        base_conf_file_path = os.path.join(base_conf_folder_path, f"conf_api_forecast_predict_{mode}.json")
        config = None
        if os.path.isfile(base_conf_file_path):
            config = json.loads(open(base_conf_file_path).read().replace("\n", ""))

        if config:
            # Set mode (predict submode)
            config["services"]["forecast"]["submode"] = params.mode

            if params.mode == 'schedule':
                # Enable the right forecaster and delete others

                forecaster = None
                if params.target == 'duration':
                    forecaster = next((
                        item for item in config["services"]["forecast"]["forecast"] if item["name"] == 'xgboost_charge_duration'), None)
                # elif params.target == 'energy':
                #     # TODO
                # elif params.target == 'connections':
                #     # TODO

                # Enable forecaster
                forecaster['enabled'] = True

                #
                forecaster['actor'] = params.actor
                forecaster['actor_id'] = params.actor_id
                forecaster['date'] = params.date.strftime("%Y-%m-%d")

                # Set forecaster to conf
                config["services"]["forecast"]["forecast"] = [forecaster]

            elif params.mode == 'query':
                config["services"]["forecast"]["submode"] = params.mode

                forecaster = None
                if params.target == 'duration':
                    forecaster = next((
                        item for item in config["services"]["forecast"]["forecast"] if item["name"] == 'xgboost_charge_duration'), None)

                # Set actor file name
                forecaster['actor'] = params.actor
                forecaster['actor_id'] = params.actor_id
                forecaster['date'] = params.date.strftime("%Y-%m-%d")

                # Set forecaster to conf
                config["services"]["forecast"]["forecast"] = [forecaster]

            # Run forecaster
            output = main(config_json=dict(config))
        else:
            raise FileNotFoundError

        return {'message': output if type(output) != Exception else str(output)}

    except Exception as e:
        return {'message': str(e)}


if bool(os.environ["SCHEDULE_ENABLED"]) == True:
    @router.on_event("startup")
    def startup_event():
        # Run predict schedule each midnight

        # Get users ids
        user_ids = list(range(1, 11))  # TODO get list of users from db (per farlo va creato un servizio admin con un suo conf che abbia come input postgres e che legga in quel modo la lista di utenti dal db, li restituisca qui e poi avvii i job... )
        for user_id in user_ids:
            params = PredictModelsDataParams(mode='schedule',
                                             actor='user',
                                             actor_id=user_id,
                                             target='duration',
                                             date=datetime.now().date() + timedelta(days=1))
            # scheduler.add_job(predict, args=[params], misfire_grace_time=60)
            # scheduler.add_job(predict, trigger='interval', minutes=10, args=[params], misfire_grace_time=60, replace_existing=True)
            scheduler.add_job(predict, trigger='cron', hour="*", args=[params], misfire_grace_time=60, replace_existing=True)

        # # Get charging_stations ids
        # charging_stations_ids = list(range(1, 68))  # TODO get from db
        # for charging_station_id in charging_stations_ids:
        #     params = PredictModelsDataParams(mode='schedule',
        #                                      actor='charging_station',
        #                                      actor_id=charging_station_id,
        #                                      target='energy',
        #                                      date=datetime.now().date() + timedelta(days=1))
        #     scheduler.add_job(predict, 'interval', minutes=2, args=[params])

        scheduler.start()
        return


    @router.on_event("shutdown")
    def shutdown_event():
        scheduler.shutdown()
        return


    @router.get("/jobs")
    def get_jobs():
        jobs = scheduler.get_jobs()
        return {"jobs": [job.id for job in jobs]}
