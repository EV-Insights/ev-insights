from pydantic import BaseModel, field_validator, model_validator
from typing import Optional, List, Literal


class IngestDatasetsParams(BaseModel):
    datasets_list: list
    folder_path: str
    limit_rows: int


class IngestDataParams(BaseModel):
    pilot_name: str
    force_ingestion: bool
    debug_mode: bool = False