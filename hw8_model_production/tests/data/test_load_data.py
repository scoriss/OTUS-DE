from typing import List
import pandas as pd

from titanic_model.data import load_data

def test_load_data(train_dataset_path: str, test_dataset_path: str, dataset_cols: List):
    data = load_data(train_dataset_path, test_dataset_path)
    assert len(data) > 300
    assert pd.Series(dataset_cols).isin(data.columns).all()