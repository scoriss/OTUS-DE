import pandas as pd

def load_data(train_data_path: str, test_data_path: str) -> pd.DataFrame:
    train_data = pd.read_csv(train_data_path)
    test_data = pd.read_csv(test_data_path)
    model_data = pd.concat([train_data, test_data], ignore_index=True, sort=False)
    return model_data
