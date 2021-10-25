# titanic_model.py
import os
import errno
from typing import NoReturn
os.environ["OMP_NUM_THREADS"] = "4"
os.environ["OPENBLAS_NUM_THREADS"] = "4"
os.environ["MKL_NUM_THREADS"] = "4"
os.environ["VECLIB_MAXIMUM_THREADS"] = "4"
os.environ["NUMEXPR_NUM_THREADS"] = "4"

import click
import joblib
import numpy as np
from pathlib import Path, PurePath
from flask import Flask, request, jsonify

from titanic_model.logger import LOGGER
from titanic_model.data import load_data
from titanic_model.preprocess import preprocess_data
from titanic_model.model import *


MODEL_PARAMS = None
MODEL_DATA = None
MODEL = None
MODEL_COLUMNS = None

FLASK_APP = Flask(__name__)

def load_model_data():
    global MODEL_PARAMS
    global MODEL_DATA
    
    train_data_path = PurePath( Path(__file__).resolve().parent, MODEL_PARAMS.train_data_path)
    test_data_path = PurePath( Path(__file__).resolve().parent, MODEL_PARAMS.test_data_path)

    LOGGER.info(f"Load train data for model from file: {train_data_path}")
    LOGGER.info(f"Load test data for model from file: {test_data_path}")
    MODEL_DATA = load_data(train_data_path, test_data_path)

def save_serialized_model():
    global MODEL_DATA
    global MODEL
    
    model_dump_file = PurePath( Path(__file__).resolve().parent, MODEL_PARAMS.model_dump_path)
    columns_dump_file = PurePath( Path(__file__).resolve().parent, MODEL_PARAMS.column_dump_path)
    columns = get_data_for_predict(MODEL_DATA)

    LOGGER.info(f"Dump model in file: {model_dump_file}")
    LOGGER.info(f"Dump columns in file: {columns_dump_file}")

    serialize_model(MODEL, model_dump_file, columns, columns_dump_file)

def predict_from_dump() -> np.ndarray:
    global MODEL_PARAMS
    model_dump_file = PurePath( Path(__file__).resolve().parent, MODEL_PARAMS.model_dump_path)
    columns_dump_file = PurePath( Path(__file__).resolve().parent, MODEL_PARAMS.column_dump_path)
    report_path = PurePath( Path(__file__).resolve().parent, MODEL_PARAMS.predict_report_path)

    if os.path.exists(model_dump_file) == False: 
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), str(model_dump_file))
    if os.path.exists(columns_dump_file) == False: 
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), str(columns_dump_file))

    LOGGER.info(f"Load model from dump file: {model_dump_file}")
    LOGGER.info(f"Load columns from dump file: {columns_dump_file}")

    predict_result = predict_model_from_dump(model_dump_file, columns_dump_file)
    columns = joblib.load(columns_dump_file)
    save_predict_report(columns, predict_result, report_path)
    LOGGER.info(f"Save predict result in file: {str(report_path)}")

    return predict_result


@click.group()
def cli():
    """Titanic model program that predicts which passengers survived the Titanic shipwreck."""
    pass

@cli.command()
@click.argument('config_file', required=True, type=click.Path(exists=True))
def train(config_file):
    """- Train Titanic model"""
    global MODEL_PARAMS
    global MODEL_DATA
    global MODEL

    click.echo('RUN COMMAND - Train Titanic model')
    click.echo('YAML model configuration file: '+click.format_filename(config_file))
    LOGGER.info('Start model train...')

    MODEL_PARAMS = read_model_training_params(config_file)
    LOGGER.info('Load model training parameters from YAML configuration file')

    LOGGER.info(f"Start train pipeline with params {MODEL_PARAMS}")

    load_model_data()
    MODEL_DATA = preprocess_data(MODEL_DATA)
    
    LOGGER.info("Train model... ")
    MODEL = train_model(MODEL_DATA, MODEL_PARAMS.train_params, True)
    save_serialized_model()
    LOGGER.info("Train model complete!")
    

@cli.command()
@click.argument('config_file', required=True, type=click.Path(exists=True))
def serve(config_file):
    """- Serve REST API"""
    global MODEL_PARAMS

    click.echo('RUN COMMAND - Serve Titanic model')
    click.echo('YAML model configuration file: '+click.format_filename(config_file))
    LOGGER.info('Start serving model...')

    MODEL_PARAMS = read_model_training_params(config_file)
    LOGGER.info('Load model parameters from YAML configuration file')

    LOGGER.info(f"Start serving model with params {MODEL_PARAMS}")


@cli.command()
@click.argument('config_file', required=True, type=click.Path(exists=True))
def predict(config_file):
    """- Predict model result"""
    global MODEL_PARAMS

    click.echo('RUN COMMAND - Predict model result')
    click.echo('YAML model configuration file: '+click.format_filename(config_file))
    LOGGER.info('Start serving model...')

    MODEL_PARAMS = read_model_training_params(config_file)
    LOGGER.info('Load model parameters from YAML configuration file')

    LOGGER.info(f"Start predict model with params {MODEL_PARAMS}")
    LOGGER.info("Predict result...")
    predict_result = predict_from_dump()
    LOGGER.info("Predict result complete!")


if __name__ == '__main__':
    cli()

