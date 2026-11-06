"""
RR TalentIQ - K-Means Clustering & Archetype Discovery Engine
Discovers natural statistical groupings of domestic players using unsupervised
K-Means clustering, validated with silhouette scores and inertia elbow metrics.
"""

from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from ml.preprocessing import ScoutingDataPreprocessor, UNIVERSAL_SCOUTING_FEATURES


class PlayerClusteringEngine:
    """
    Performs K-Means clustering to uncover hidden player archetypes,
    validated with objective cluster quality metrics.
    """

    def __init__(self, n_clusters: Optional[int] = None, random_state: int = 42):
        self.n_clusters = n_clusters
        self.random_state = random_state
        self.kmeans: Optional[KMeans] = None
        self.preprocessor = ScoutingDataPreprocessor()
        self.silhouette_avg: float = 0.0
        self.cluster_names: Dict[int, str] = {}

    def find_optimal_clusters(
        self,
        X_scaled: np.ndarray,
        k_min: int = 2,
        k_max: int = 6
    ) -> Tuple[int, Dict[int, float]]:
        """
        Calculates silhouette scores for varying k and identifies the optimal cluster count.
        """
        n_samples = len(X_scaled)
        actual_k_max = min(k_max, n_samples - 1)
        if actual_k_max < k_min:
            return 2, {2: 0.5}

        scores = {}
        for k in range(k_min, actual_k_max + 1):
            km = KMeans(n_clusters=k, random_state=self.random_state, n_init=10)
            labels = km.fit_predict(X_scaled)
            score = silhouette_score(X_scaled, labels)
            scores[k] = round(float(score), 3)

        optimal_k = max(scores, key=scores.get)
        return optimal_k, scores

    def fit_predict_archetypes(
        self,
        df: pd.DataFrame,
        feature_cols: Optional[List[str]] = None
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Fits K-Means, assigns cluster labels, generates human-readable archetypes,
        and computes evaluation metrics.
        """
        if feature_cols:
            self.preprocessor.feature_columns = feature_cols

        X_scaled, used_features = self.preprocessor.fit_transform(df)
        
        # Determine cluster count if not predefined
        if self.n_clusters is None:
            self.n_clusters, sil_scores = self.find_optimal_clusters(X_scaled)
        else:
            sil_scores = {}

        self.kmeans = KMeans(
            n_clusters=self.n_clusters,
            random_state=self.random_state,
            n_init=15
        )
        cluster_labels = self.kmeans.fit_predict(X_scaled)
        self.silhouette_avg = round(float(silhouette_score(X_scaled, cluster_labels)), 3)

        clustered_df = df.copy()
        clustered_df["cluster_id"] = cluster_labels

        # Derive human-readable archetype names from centroid profiles
        self.cluster_names = self._generate_archetype_names(clustered_df, used_features)
        clustered_df["cluster_archetype"] = clustered_df["cluster_id"].map(self.cluster_names)

        metadata = {
            "n_clusters": self.n_clusters,
            "silhouette_score": self.silhouette_avg,
            "inertia": round(float(self.kmeans.inertia_), 2),
            "feature_columns": used_features,
            "cluster_archetypes": self.cluster_names,
            "k_search_scores": sil_scores
        }
        return clustered_df, metadata

    def _generate_archetype_names(
        self,
        clustered_df: pd.DataFrame,
        feature_cols: List[str]
    ) -> Dict[int, str]:
        """
        Inspects cluster centroids to assign meaningful cricket scout archetype labels.
        """
        names = {}
        for c_id in range(self.n_clusters):
            subset = clustered_df[clustered_df["cluster_id"] == c_id]
            if len(subset) == 0:
                names[c_id] = f"Cluster {c_id}"
                continue

            mean_sr = subset["strike_rate"].mean() if "strike_rate" in subset.columns else 120.0
            mean_econ = subset["economy"].mean() if "economy" in subset.columns else 8.0
            mean_wkts = subset["wickets"].mean() if "wickets" in subset.columns else 0.0
            mean_runs = subset["runs"].mean() if "runs" in subset.columns else 0.0
            mean_age = subset["age"].mean() if "age" in subset.columns else 24.0

            if mean_wkts >= 15 and mean_econ <= 7.8:
                if mean_sr > 125.0 and mean_runs > 100:
                    names[c_id] = "Dual-Threat All-Rounder (Bowler Dominant)"
                else:
                    names[c_id] = "High-Control Strike Bowler"
            elif mean_sr >= 155.0 and mean_runs >= 400:
                names[c_id] = "Explosive High-Impact Finisher / Power Hitter"
            elif mean_runs >= 450 and mean_sr < 155.0:
                names[c_id] = "High-Volume Anchor / Top-Order Accumulator"
            elif mean_age < 22.0:
                names[c_id] = "High-Ceiling Youth Prospect"
            else:
                names[c_id] = f"Tactical Utility Specialist (Group {c_id+1})"

        return names

