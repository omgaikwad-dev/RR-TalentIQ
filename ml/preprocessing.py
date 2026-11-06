"""
RR TalentIQ - Machine Learning Preprocessing & Feature Engineering
Extracts, imputes, and standardizes multi-dimensional feature sets
for unsupervised clustering, PCA projection, and model evaluation.
"""

from typing import Tuple, List, Dict, Any, Optional
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer


# Feature Subsets for Specialized ML Workflows
BATTING_ML_FEATURES = [
    "strike_rate",
    "batting_average",
    "boundary_pct_bat",
    "dot_ball_pct_bat",
    "runs_per_innings",
    "age"
]

BOWLING_ML_FEATURES = [
    "economy",
    "bowling_strike_rate",
    "bowling_average",
    "dot_ball_pct_bowl",
    "wickets_per_innings",
    "age"
]

UNIVERSAL_SCOUTING_FEATURES = [
    "strike_rate",
    "batting_average",
    "boundary_pct_bat",
    "economy",
    "bowling_strike_rate",
    "wickets",
    "runs",
    "age",
    "overall_scouting_score"
]


class ScoutingDataPreprocessor:
    """
    Standardizes raw and derived metrics for scikit-learn models,
    guaranteeing no data leakage and graceful handling of edge cases.
    """

    def __init__(self, feature_columns: Optional[List[str]] = None):
        self.feature_columns = feature_columns or UNIVERSAL_SCOUTING_FEATURES
        self.imputer = SimpleImputer(strategy="median")
        self.scaler = StandardScaler()
        self.is_fitted = False

    def fit_transform(self, df: pd.DataFrame) -> Tuple[np.ndarray, List[str]]:
        """
        Fits imputer and scaler on the dataset, returns the scaled feature matrix.
        """
        # Ensure selected feature columns exist in df
        available_features = [col for col in self.feature_columns if col in df.columns]
        if len(available_features) < 2:
            raise ValueError(f"Insufficient numeric feature columns found in dataset: {available_features}")

        raw_features = df[available_features].values
        imputed_features = self.imputer.fit_transform(raw_features)
        scaled_features = self.scaler.fit_transform(imputed_features)
        
        self.feature_columns = available_features
        self.is_fitted = True
        return scaled_features, available_features

    def transform(self, df: pd.DataFrame) -> np.ndarray:
        """
        Transforms new incoming data using previously fitted scaler.
        """
        if not self.is_fitted:
            raise RuntimeError("Preprocessor must be fitted using fit_transform before calling transform.")
        raw_features = df[self.feature_columns].values
        imputed = self.imputer.transform(raw_features)
        return self.scaler.transform(imputed)

