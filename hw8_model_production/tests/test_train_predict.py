import os
import joblib
from sklearn.ensemble import RandomForestClassifier
from titanic_model.model import *
from titanic_model.data import load_data
from titanic_model.preprocess import preprocess_data


def test_train_model(test_dataset_path: str, train_dataset_path: str, 
        config_file_path: str, model_dump_path: str, columns_dump_path: str):
    if os.path.exists(model_dump_path):
        os.remove(model_dump_path)
    if os.path.exists(columns_dump_path):
        os.remove(columns_dump_path)

    model_params = read_model_training_params(config_file_path)
    model_data = load_data(train_dataset_path, test_dataset_path)
    model_data = preprocess_data(model_data)
    model = train_model(model_data, model_params.train_params, False)
    columns = get_data_for_predict(model_data)
    serialize_model(model, model_dump_path, columns, columns_dump_path)

    assert isinstance(model, RandomForestClassifier)
    assert len(model) > 300
    assert os.path.exists(model_dump_path)
    assert os.path.exists(columns_dump_path)

def test_predict_model(model_dump_path: str, columns_dump_path: str):
    predict_result = predict_model_from_dump(model_dump_path, columns_dump_path)

    assert len(predict_result) > 300
