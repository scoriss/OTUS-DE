from titanic_model.model.train_params import TrainingParams
from titanic_model.model.model_params import TitanicModelParams, read_model_training_params

def test_model_params(config_file_path: str):
    model_params = read_model_training_params(config_file_path)
    assert isinstance(model_params, TitanicModelParams)
    assert isinstance(model_params.train_params, TrainingParams)