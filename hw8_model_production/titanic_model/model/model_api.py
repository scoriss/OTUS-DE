import os
import errno
import joblib
import pandas as pd
from pathlib import Path, PurePath
from flask import Flask, request, jsonify, make_response,send_from_directory
from titanic_model.model import *
from titanic_model.data import load_data
from titanic_model.preprocess import preprocess_data


FLASK_APP = Flask("Titanic Model API")
WORK_PATH = None
MODEL_PARAMS = None


@FLASK_APP.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(WORK_PATH, 'static'), 'favicon.ico')

@FLASK_APP.route('/')
@FLASK_APP.route('/predict', methods = ['GET'])
def api_predict():
    try:
        predict_result = predict_from_dump()
        FLASK_APP.logger.info("Predict result complete!")
        return make_response(jsonify(predict_result.to_dict(orient='records')), 200)
    except Exception as error:
        return get_response({'error': str(error)}, 500)

@FLASK_APP.route('/train', methods = ['GET', 'POST'])
def api_train():
    try:
        global WORK_PATH
        global MODEL_PARAMS

        FLASK_APP.logger.info('Start model train...')

        train_data_path = PurePath( WORK_PATH, MODEL_PARAMS.train_data_path)
        test_data_path = PurePath( WORK_PATH, MODEL_PARAMS.test_data_path)

        FLASK_APP.logger.info(f"Load train data for model from file: {train_data_path}")
        FLASK_APP.logger.info(f"Load test data for model from file: {test_data_path}")
        model_data = load_data(train_data_path, test_data_path)
        model_data = preprocess_data(model_data)
        
        FLASK_APP.logger.info("Train model... ")
        model = train_model(model_data, MODEL_PARAMS.train_params, True)

        model_dump_file = PurePath( WORK_PATH, MODEL_PARAMS.model_dump_path)
        columns_dump_file = PurePath( WORK_PATH, MODEL_PARAMS.column_dump_path)
        columns = get_data_for_predict(model_data)

        FLASK_APP.logger.info(f"Dump model in file: {model_dump_file}")
        FLASK_APP.logger.info(f"Dump columns in file: {columns_dump_file}")

        serialize_model(model, model_dump_file, columns, columns_dump_file)

        FLASK_APP.logger.info("Train model complete!")
        return get_response({'message': 'Train model complete!'}, 200)
    except Exception as error:
        return get_response({'error': str(error)}, 500)

def deploy_api(model_params: TitanicModelParams, work_path: str):
    global WORK_PATH
    global MODEL_PARAMS
    MODEL_PARAMS = model_params
    WORK_PATH = work_path

    FLASK_APP.run(
        host=os.environ.get("BACKEND_HOST", "0.0.0.0"), 
        port=MODEL_PARAMS.model_api_port, 
        debug=True
        )

def get_response(dict, status=200):
    return make_response(jsonify(dict), status)

def predict_from_dump() -> pd.DataFrame:
    global WORK_PATH
    global MODEL_PARAMS
    model_dump_file = PurePath( WORK_PATH, MODEL_PARAMS.model_dump_path)
    columns_dump_file = PurePath( WORK_PATH, MODEL_PARAMS.column_dump_path)

    if os.path.exists(model_dump_file) == False: 
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), str(model_dump_file))
    if os.path.exists(columns_dump_file) == False: 
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), str(columns_dump_file))

    predict_result = predict_model_from_dump(model_dump_file, columns_dump_file)
    columns = joblib.load(columns_dump_file)
    predict_report = pd.DataFrame({'PassengerId': columns.PassengerId, 'Survived': predict_result})
    predict_report.Survived = predict_report.Survived.astype(int)
    
    return predict_report

@FLASK_APP.errorhandler(404)
def not_found(error):
    FLASK_APP.logger.warning('PAGE NOT FOUND')
    return make_response(jsonify({'code': 'PAGE_NOT_FOUND'}), 404)

@FLASK_APP.errorhandler(405)
def not_found(error):
    FLASK_APP.logger.warning('METOD NOT ALLOWED')
    return make_response(jsonify({'code': 'METOD_NOT_ALLOWED'}), 405)

@FLASK_APP.errorhandler(500)
def server_error(error):
    FLASK_APP.logger.warning('INTERNAL SERVER ERROR')
    return make_response(jsonify({'code': 'INTERNAL_SERVER_ERROR'}), 500)

    

