from app.analysis.embeddings import HashingEmbedder
from app.analysis.taxonomy import load_taxonomy


def test_taxonomy_loads_expected_clusters() -> None:
    taxonomy = load_taxonomy()
    ids = {cluster.id for cluster in taxonomy.clusters}
    assert {
        "programming",
        "backend",
        "frontend",
        "databases",
        "cloud_devops",
        "data_science",
        "machine_learning",
        "ai_nlp",
        "testing",
        "system_design",
    } <= ids
    assert all(cluster.embedding_text() for cluster in taxonomy.clusters)


def test_every_cluster_has_valid_semantic_description() -> None:
    taxonomy = load_taxonomy()
    for cluster in taxonomy.clusters:
        assert cluster.description and len(cluster.description.strip()) > 20
        assert cluster.name and len(cluster.name.strip()) > 3
        assert len(cluster.examples) >= 3


def test_cluster_representations_can_be_embedded_by_embedder() -> None:
    taxonomy = load_taxonomy()
    embedder = HashingEmbedder(dim=64)
    texts = taxonomy.embedding_texts()
    embeddings = embedder.embed(texts)
    assert embeddings.shape == (len(taxonomy.clusters), 64)

