"""
RR TalentIQ - Principal Component Analysis (PCA) & Dimensionality Reduction
Maps multi-dimensional domestic player features onto 2D and 3D latent performance spaces,
quantifying variance decomposition and underlying strategic axes.
"""

from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from ml.preprocessing import ScoutingDataPreprocessor, UNIVERSAL_SCOUTING_FEATURES


class PlayerPCAModel:
    """
    Dimensionality reduction engine for visual player landscape projections
    and performance factor decomposition.
    """

    def __init__(self, n_components: int = 2):
        self.n_components = n_components
        self.pca = PCA(n_components=n_components, random_state=42)
        self.preprocessor = ScoutingDataPreprocessor()
        self.feature_names: List[str] = []

    def fit_transform_projection(
        self,
        df: pd.DataFrame,
        feature_cols: Optional[List[str]] = None
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Projects high-dimensional player data onto 2D coordinates (PC1, PC2)
        and computes explained variance.
        """
        if feature_cols:
            self.preprocessor.feature_columns = feature_cols

        X_scaled, self.feature_names = self.preprocessor.fit_transform(df)
        components = self.pca.fit_transform(X_scaled)

        projected_df = df.copy()
        for i in range(self.n_components):
            projected_df[f"pca_dim_{i+1}"] = components[:, i].round(3)

        explained_var = [round(float(v) * 100, 2) for v in self.pca.explained_variance_ratio_]
        cumulative_var = round(float(np.sum(explained_var)), 2)

        # Component Loadings (weights of each feature in PC1 and PC2)
        loadings = {}
        for i in range(self.n_components):
            comp_weights = {
                self.feature_names[j]: round(float(self.pca.components_[i, j]), 3)
                for j in range(len(self.feature_names))
            }
            # Sort by absolute weight
            sorted_weights = dict(sorted(comp_weights.items(), key=lambda item: abs(item[1]), reverse=True))
            loadings[f"PC{i+1}"] = sorted_weights

        metadata = {
            "explained_variance_pct": explained_var,
            "cumulative_variance_pct": cumulative_var,
            "feature_names": self.feature_names,
            "component_loadings": loadings,
            "information_loss_pct": round(100.0 - cumulative_var, 2)
        }
        return projected_df, metadata

