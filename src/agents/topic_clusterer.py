"""Topic Clusterer agent — groups keywords into semantic topic clusters."""

from typing import Any, Dict, List, Optional

import numpy as np
from loguru import logger
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import silhouette_score

from agents.base_agent import BaseAgent
from contracts.topic_clusterer import TopicClusterInput, TopicClusterOutput
from core.config import settings
from models.base import AgentResponse
from models.keywords import Keyword, KeywordCluster
from models.topics import TopicCategory


class TopicClustererAgent(BaseAgent):
    """Clusters keywords into topic groups using TF-IDF + KMeans."""

    def __init__(self):
        super().__init__(name="TopicClusterer", model=settings.clustering_model)

    async def process(self, input_data: TopicClusterInput) -> AgentResponse:
        self.start_task()
        terms = [kw.term for kw in input_data.keywords]
        logger.info(f"Clustering {len(terms)} keywords (method={input_data.method})")

        # NOTE: If keywords >= 2000, consider upgrading to embeddings + HDBSCAN
        if len(terms) >= 2000:
            logger.warning("Large keyword set (>=2000). Consider embeddings + HDBSCAN for better clustering.")

        if len(terms) < 3:
            # Not enough keywords to cluster
            cluster = KeywordCluster(
                cluster_id=0,
                label="All Keywords",
                keywords=input_data.keywords,
                size=len(terms),
            )
            topic = TopicCategory(name="All Keywords", keywords=terms)
            output = TopicClusterOutput(
                clusters=[cluster],
                topics=[topic],
                method_used=input_data.method,
            )
            return self.create_response(status="success", data=output.model_dump())

        # TF-IDF vectorization
        vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words="english",
            ngram_range=(1, 2),
        )
        tfidf_matrix = vectorizer.fit_transform(terms)

        # Find optimal k via silhouette score
        min_k, max_k = input_data.n_clusters_range
        max_k = min(max_k, len(terms) - 1)
        min_k = max(min_k, 2)

        best_k = min_k
        best_score = -1

        for k in range(min_k, max_k + 1):
            km = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = km.fit_predict(tfidf_matrix)
            if len(set(labels)) > 1:
                score = silhouette_score(tfidf_matrix, labels)
                if score > best_score:
                    best_score = score
                    best_k = k

        # Final clustering with optimal k
        kmeans = KMeans(n_clusters=best_k, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(tfidf_matrix)

        # Build cluster objects
        clusters = []
        topics = []
        feature_names = vectorizer.get_feature_names_out()

        for cluster_id in range(best_k):
            mask = cluster_labels == cluster_id
            cluster_keywords = [input_data.keywords[i] for i, m in enumerate(mask) if m]
            cluster_terms = [terms[i] for i, m in enumerate(mask) if m]

            # Get top terms for label
            center = kmeans.cluster_centers_[cluster_id]
            top_indices = center.argsort()[-3:][::-1]
            label_parts = [feature_names[i] for i in top_indices]
            label = " / ".join(label_parts).title()

            avg_demand = np.mean([kw.trends_momentum or 0 for kw in cluster_keywords]) if cluster_keywords else 0.0

            cluster = KeywordCluster(
                cluster_id=cluster_id,
                label=label,
                keywords=cluster_keywords,
                size=len(cluster_keywords),
                avg_demand_signal=round(float(avg_demand), 4),
            )
            clusters.append(cluster)

            topic = TopicCategory(
                name=label,
                keywords=cluster_terms,
                demand_signal=round(float(avg_demand), 4),
            )
            topics.append(topic)

        output = TopicClusterOutput(
            clusters=clusters,
            topics=topics,
            method_used=input_data.method,
            metadata={"optimal_k": best_k, "silhouette_score": round(best_score, 4)},
        )

        logger.info(f"Created {best_k} clusters (silhouette={best_score:.4f})")
        return self.create_response(status="success", data=output.model_dump(), metadata=output.metadata)
