from dataclasses import dataclass
from .train_params import TrainingParams
from marshmallow_dataclass import class_schema
import yaml


@dataclass()
class TitanicModelParams:
    train_data_path: str
    test_data_path: str
    model_dump_path: str
    column_dump_path: str
    predict_report_path: str
    train_params: TrainingParams
    model_api_port: int

ModelTrainingParamsSchema = class_schema(TitanicModelParams)

def read_model_training_params(path: str) -> TitanicModelParams:
    with open(path, "r") as input_stream:
        schema = ModelTrainingParamsSchema()
        return schema.load(yaml.safe_load(input_stream))
