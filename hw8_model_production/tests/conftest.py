import os
import pytest
from pathlib import Path, PurePath
import pandas as pd

project_dir = Path(__file__).resolve().parent.parent

@pytest.fixture()
def test_dataset_path():
    return os.path.join(PurePath(project_dir, "data","test.csv"))

@pytest.fixture()
def train_dataset_path():
    return os.path.join(PurePath(project_dir, "data", "train.csv"))

@pytest.fixture()
def config_file_path():
    return os.path.join(PurePath(project_dir, "configs", "model_config.yaml"))

@pytest.fixture()
def model_dump_path():
    return os.path.join(os.path.dirname(__file__), "model_test.bin")

@pytest.fixture()
def columns_dump_path():
    return os.path.join(os.path.dirname(__file__), "columns_test.bin")

@pytest.fixture()
def dataset_cols():
    return ["PassengerId", "Pclass", "Sex", "Age", "Embarked", "Survived"]

@pytest.fixture()
def preprocess_cols():
    return ["PassengerId", "Family", "Sex", "Is_Alone", "Fare_High_Mid", "Survived"]

