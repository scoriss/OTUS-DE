from typing import Any
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score

from .train_params import TrainingParams

import logging

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)


def get_data_for_predict(model_data: pd.DataFrame) -> pd.DataFrame:
    data_to_predict = model_data[model_data.Survived.isnull()]
    data_to_predict = data_to_predict.drop(['Survived'], axis=1)

    return data_to_predict

def train_model(model_data: pd.DataFrame, train_params: TrainingParams, log_output: bool = False) -> RandomForestClassifier:
    if train_params.model_type == "RandomForestClassifier":
        model = RandomForestClassifier(
            criterion = train_params.criterion,
            n_estimators = train_params.n_estimators,
            min_samples_split = train_params.min_samples_split,
            min_samples_leaf = train_params.min_samples_leaf,
            max_features = train_params.max_features,
            oob_score = train_params.oob_score,
            random_state = train_params.random_state,
            n_jobs =- train_params.n_jobs
        )
    else:
        raise NotImplementedError()

    train_data = model_data.dropna()
    feature_train = train_data['Survived']
    label_train = train_data.drop(['Survived'], axis=1)

    x_train, x_test, y_train, y_test = train_test_split(label_train, feature_train, test_size=0.2)
    model.fit(x_train, np.ravel(y_train))

    if log_output:
        LOGGER.info("RF Accuracy: " + repr(round(model.score(x_test, y_test) * 100, 2)) + "%")

    result_rf = cross_val_score(model, x_train, y_train, cv=10, scoring='accuracy')
    if log_output:
        LOGGER.info('RF Cross validated score: '+ repr(round(result_rf.mean() * 100, 2)) )

    return model

def predict_model(model: RandomForestClassifier, model_data: pd.DataFrame) -> np.ndarray:
    data_to_predict = get_data_for_predict(model_data)

    predict_result = model.predict(data_to_predict)
    return predict_result
    
def predict_model_from_dump(model_dump_file: str, columns_dump_file: str) -> np.ndarray:
    model = joblib.load(model_dump_file)
    data_to_predict = joblib.load(columns_dump_file)

    predict_result = model.predict(data_to_predict)
    return predict_result

def serialize_object(object: Any, dump_file: str) -> str:
    with open(dump_file, "wb") as file:
        joblib.dump(object, file)
    return dump_file

def serialize_model(model: RandomForestClassifier, model_dump_file: str, 
        model_columns: pd.DataFrame, columns_dump_file: str) -> None:
    serialize_object(model, model_dump_file)
    serialize_object(model_columns, columns_dump_file)

def save_predict_report(data_to_predict: pd.DataFrame, predict: np.ndarray, report_path: str):
    predict_report = pd.DataFrame({'PassengerId': data_to_predict.PassengerId, 'Survived': predict})
    predict_report.Survived = predict_report.Survived.astype(int)
    predict_report.to_csv(report_path, index=False)
    
