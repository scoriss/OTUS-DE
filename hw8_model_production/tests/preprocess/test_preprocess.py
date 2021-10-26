from typing import List
import pandas as pd

from titanic_model.data import load_data
from titanic_model.preprocess import preprocess_data

def test_preprocess_data(train_dataset_path: str, test_dataset_path: str, preprocess_cols: List):
    data = load_data(train_dataset_path, test_dataset_path)
    preprocess_df = preprocess_data(data)
    assert len(preprocess_df) > 300
    assert pd.Series(preprocess_cols).isin(preprocess_df.columns).all()