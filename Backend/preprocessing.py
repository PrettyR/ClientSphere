import pandas as pd
import numpy as np
from typing import List, Tuple
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler


def infer_numeric_feature_columns(df: pd.DataFrame, drop_columns: List[str] | None = None) -> List[str]:
    drop_columns = drop_columns or []
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    return [c for c in numeric_cols if c not in drop_columns]


def build_numeric_preprocess_pipeline() -> Pipeline:
    return Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])


def prepare_features(
    df: pd.DataFrame,
    drop_columns: List[str] | None = None
) -> Tuple[pd.DataFrame, List[str]]:
    """
    Select numeric feature columns excluding provided columns.
    Returns the feature dataframe and the feature column list.
    """
    drop_columns = drop_columns or []
    feature_columns = infer_numeric_feature_columns(df, drop_columns=drop_columns)
    X = df[feature_columns].copy()
    return X, feature_columns


