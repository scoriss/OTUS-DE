from dataclasses import dataclass, field

@dataclass()
class TrainingParams:
    model_type: str = field(default="RandomForestClassifier")
    criterion: str = field(default="entropy")
    n_estimators: int = field(default=700)
    min_samples_split: int = field(default=10)
    min_samples_leaf: int = field(default=1)
    max_features: str = field(default="auto")
    oob_score: bool = field(default=True)
    random_state: int = field(default=1)
    n_jobs: int = field(default=-1)

