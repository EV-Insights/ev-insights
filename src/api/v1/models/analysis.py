from pydantic import BaseModel, field_validator, model_validator
from typing import Optional, List, Literal


class Stats(BaseModel):
    entity: Literal['db', 'dataset', 'user', 'chargingstation']
    id: Optional[int] = None

    @classmethod
    @model_validator(mode='before')
    def check_required_fields(cls, values):
        entity = values.get('entity')

        if entity == 'db' and not values.get('datasets_list'):
            raise ValueError("'dataset_list' is required when entity is 'db'")

        if (entity == 'user' or entity == 'dataset' or entity == 'chargingstation') and not values.get('id'):
            raise ValueError(f"'id' is required when entity is {entity}")

        return values
