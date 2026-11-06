"""
RR TalentIQ - Unit Tests for Machine Learning Intelligence Modules
Validates preprocessing, K-Means clustering, silhouette validation,
PCA dimensionality reduction, and feature explainability.
"""

import pytest
import pandas as pd
import numpy as np
from analytics.domestic_data_loader import DomesticDataLoader
from ml.preprocessing import ScoutingDataPreprocessor
from ml.clustering import PlayerClusteringEngine
from ml.player_model import PlayerPCAModel
from ml.explainability import MLExplainabilityEngine
from scouting.player_ranker import PlayerRanker


@pytest.fixture
def scored_dataset():
    loader = DomesticDataLoader()
    raw = loader.get_benchmarked_uncapped_talents()
    ranker = PlayerRanker()
    return ranker.rank_players(raw)


def test_preprocessing_pipeline(scored_dataset):
    """Verifies that preprocessor handles missing values and scales features to zero mean."""
    preprocessor = ScoutingDataPreprocessor()
    X_scaled, features = preprocessor.fit_transform(scored_dataset)

    assert X_scaled.shape[0] == len(scored_dataset)
    assert X_scaled.shape[1] == len(features)
    # Check zero mean across features
    assert np.allclose(np.mean(X_scaled, axis=0), 0.0, atol=1e-2)
    # Check unit variance
    assert np.allclose(np.std(X_scaled, axis=0), 1.0, atol=1e-2)


def test_kmeans_clustering_and_validation(scored_dataset):
    """Verifies K-Means cluster assignment, silhouette score validation, and archetype labeling."""
    cluster_engine = PlayerClusteringEngine(n_clusters=3, random_state=42)
    clustered_df, meta = cluster_engine.fit_predict_archetypes(scored_dataset)

    assert "cluster_id" in clustered_df.columns
    assert "cluster_archetype" in clustered_df.columns
    assert clustered_df["cluster_id"].nunique() == 3
    assert meta["silhouette_score"] > 0.15  # Valid cluster separation
    assert meta["n_clusters"] == 3
    assert len(meta["cluster_archetypes"]) == 3


def test_pca_dimensionality_reduction(scored_dataset):
    """Verifies that PCA extracts 2 principal components and retains substantial variance."""
    pca_model = PlayerPCAModel(n_components=2)
    projected_df, meta = pca_model.fit_transform_projection(scored_dataset)

    assert "pca_dim_1" in projected_df.columns
    assert "pca_dim_2" in projected_df.columns
    assert meta["cumulative_variance_pct"] > 40.0  # Retains > 40% of multi-metric variance
    assert meta["information_loss_pct"] < 60.0
    assert "PC1" in meta["component_loadings"]
    assert "PC2" in meta["component_loadings"]


def test_ml_explainability(scored_dataset):
    """Verifies that explainability engine computes driver metrics and coverage score for a player."""
    target_player = scored_dataset.iloc[0]["player_name"]
    explanation = MLExplainabilityEngine.explain_player_features(target_player, scored_dataset)

    assert explanation["player_name"] == target_player
    assert explanation["data_coverage_pct"] >= 90.0
    assert len(explanation["feature_breakdown"]) >= 5
    assert len(explanation["positive_drivers"]) >= 1

