"""Load the skill-cluster taxonomy from configuration data, not from hardcoded Python lists."""

from __future__ import annotations

import json
from pathlib import Path

from app.analysis.types import SkillCluster
from app.config.settings import TAXONOMY_PATH


class Taxonomy:
    def __init__(self, clusters: list[SkillCluster]) -> None:
        if not clusters:
            raise ValueError("Taxonomy must contain at least one skill cluster")
        self._clusters = tuple(clusters)
        self._by_id = {cluster.id: cluster for cluster in self._clusters}

    @property
    def clusters(self) -> tuple[SkillCluster, ...]:
        return self._clusters

    def get(self, cluster_id: str) -> SkillCluster:
        return self._by_id[cluster_id]

    def embedding_texts(self) -> list[str]:
        return [cluster.embedding_text() for cluster in self._clusters]


def load_taxonomy(path: Path | None = None) -> Taxonomy:
    taxonomy_path = path or TAXONOMY_PATH
    payload = json.loads(taxonomy_path.read_text(encoding="utf-8"))
    clusters = [
        SkillCluster(
            id=item["id"],
            name=item["name"],
            description=item["description"],
            examples=tuple(item.get("examples", [])),
        )
        for item in payload["clusters"]
    ]
    return Taxonomy(clusters)
