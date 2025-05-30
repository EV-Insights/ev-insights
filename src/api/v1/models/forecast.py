from pydantic import BaseModel, field_validator, model_validator
from typing import Optional, List, Literal
from datetime import date


class TrainModelsDataParams(BaseModel):
    dataset_name: str
    target: str
    forecaster: str
    file_name: str = None


class PredictModelsDataParams(BaseModel):
    mode: Literal['schedule', 'query']
    actor: Literal['user', 'charging_station']
    actor_id: int
    target: Literal['duration', 'energy', 'connections']
    date: date

