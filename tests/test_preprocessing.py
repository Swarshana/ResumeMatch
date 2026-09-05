from app.analysis.importance import detect_importance
from app.analysis.preprocessing import (
    extract_section_chunks,
    is_administrative_content,
    is_section_header,
    split_into_chunks,
    to_text_chunks,
)


def test_splits_bullets_and_skips_headers() -> None:
    text = """
    EXPERIENCE
    - Built REST APIs with FastAPI and PostgreSQL for internal tools.
    Skills
    * Trained classification models with scikit-learn and pandas.
    """
    chunks = split_into_chunks(text)
    assert len(chunks) == 2
    assert "FastAPI" in chunks[0]
    assert "scikit-learn" in chunks[1]


def test_deduplicates_and_filters_short_lines() -> None:
    text = """
    - Built REST APIs with FastAPI and PostgreSQL for internal tools.
    - Built REST APIs with FastAPI and PostgreSQL for internal tools.
    - Hi
    """
    chunks = split_into_chunks(text, min_chars=20)
    assert len(chunks) == 1


def test_resume_chunk_ids_are_stable() -> None:
    chunks = to_text_chunks(
        "- Designed scalable backend services using Python and FastAPI for production traffic.",
        source="resume",
    )
    assert chunks[0].id == "ev_0"
    assert chunks[0].source == "resume"


def test_empty_text_returns_no_chunks() -> None:
    assert split_into_chunks("   ") == []


def test_resume_headings_are_not_evidence() -> None:
    text = """
    WORK EXPERIENCE
    EDUCATION
    PROJECTS
    CERTIFICATIONS
    """
    chunks = split_into_chunks(text)
    assert len(chunks) == 0


def test_resume_bullets_become_evidence_units() -> None:
    text = """
    EXPERIENCE
    • Architected microservices with Python and FastAPI.
    • Deployed containerized applications to AWS ECS with Docker.
    """
    chunks = to_text_chunks(text, source="resume")
    assert len(chunks) == 2
    assert chunks[0].id == "ev_0"
    assert chunks[1].id == "ev_1"
    assert "Architected microservices" in chunks[0].text
    assert "Deployed containerized" in chunks[1].text




def test_multiple_meaningful_sentences_handled_correctly() -> None:
    text = """
    PROJECTS
    - Created an AI agent pipeline. Evaluated performance on benchmark datasets.
    """
    chunks = to_text_chunks(text, source="resume")
    assert len(chunks) == 1
    assert "AI agent pipeline" in chunks[0].text
    assert "benchmark datasets" in chunks[0].text


def test_blank_lines_do_not_create_empty_units() -> None:
    text = """

    EXPERIENCE


    - Developed backend endpoints with PostgreSQL.


    """
    chunks = split_into_chunks(text)
    assert len(chunks) == 1
    assert "PostgreSQL" in chunks[0]


def test_section_context_is_preserved() -> None:
    text = """
    PROJECTS
    - Built high throughput data ingestion using Kafka.

    EDUCATION
    - Master of Science in Computer Science from Stanford University.
    """
    chunks = to_text_chunks(text, source="resume")
    assert len(chunks) == 2
    assert chunks[0].section == "PROJECTS"
    assert chunks[1].section == "EDUCATION"


def test_technical_terms_and_punctuation_survive_normalization() -> None:
    text = """
    SKILLS
    - Experience in C++, C#, .NET, Node.js, Next.js, and CI/CD pipelines.
    - Deep expertise in PostgreSQL, Kubernetes, and REST API architecture.
    """
    chunks = split_into_chunks(text)
    assert len(chunks) == 2
    assert "C++" in chunks[0]
    assert "C#" in chunks[0]
    assert ".NET" in chunks[0]
    assert "Node.js" in chunks[0]
    assert "Next.js" in chunks[0]
    assert "CI/CD" in chunks[0]
    assert "PostgreSQL" in chunks[1]
    assert "Kubernetes" in chunks[1]
    assert "REST" in chunks[1]


def test_administrative_content_is_filtered() -> None:
    text = """
    Jane Doe
    jane.doe@example.com | (555) 123-4567 | linkedin.com/in/janedoe | github.com/janedoe
    Jan 2021 - Present
    Page 1 of 2
    EXPERIENCE
    - Built distributed backend systems using Go and Docker.
    """
    chunks = to_text_chunks(text, source="resume")
    assert len(chunks) == 1
    assert "distributed backend systems" in chunks[0].text


def test_long_coherent_bullets_handled_sensibly() -> None:
    sentence1 = "Designed and implemented a distributed event-driven pipeline processing millions of transactions daily."
    sentence2 = "Integrated Redis caching and PostgreSQL partitioning to reduce query latency by 45% across all regions."
    sentence3 = "Configured Docker containers and orchestrated deployment onto Amazon EKS with comprehensive monitoring."
    long_bullet = f"- {sentence1} {sentence2} {sentence3}"
    chunks = split_into_chunks(long_bullet, max_chars=180)
    assert len(chunks) >= 2
    for chunk in chunks:
        assert len(chunk) <= 180 or len(sentence1) > 180


def test_jd_headings_are_not_requirements() -> None:
    text = """
    REQUIREMENTS:
    QUALIFICATIONS:
    RESPONSIBILITIES:
    WHAT WE OFFER:
    """
    chunks = to_text_chunks(text, source="job")
    assert len(chunks) == 0


def test_jd_requirement_bullets_become_separate_requirements() -> None:
    text = """
    REQUIREMENTS:
    * 3+ years of experience with Python and FastAPI
    * Hands-on experience with Docker and Kubernetes
    * Proficiency in SQL and relational database design
    """
    chunks = to_text_chunks(text, source="job")
    assert len(chunks) == 3
    assert chunks[0].id == "req_0"
    assert chunks[1].id == "req_1"
    assert chunks[2].id == "req_2"
    assert "Python and FastAPI" in chunks[0].text
    assert "Docker and Kubernetes" in chunks[1].text
    assert "relational database design" in chunks[2].text


def test_jd_benefits_and_company_overview_filtered() -> None:
    text = """
    ABOUT US:
    We are a fast-growing financial technology company headquartered in New York.

    REQUIREMENTS:
    - 3+ years of experience developing backend web services in Go.

    BENEFITS:
    - Unlimited paid time off, 401(k) matching, and comprehensive health insurance.
    - Annual education budget and remote work stipend.
    """
    chunks = to_text_chunks(text, source="job")
    assert len(chunks) == 1
    assert "developing backend web services in Go" in chunks[0].text
    assert "Unlimited paid time off" not in [c.text for c in chunks]
    assert "fast-growing financial technology" not in [c.text for c in chunks]


def test_required_and_preferred_context_is_preserved() -> None:
    text = """
    REQUIRED QUALIFICATIONS:
    - Experience building APIs with Python and FastAPI.

    PREFERRED QUALIFICATIONS:
    - Familiarity with Kubernetes and Helm charts.
    """
    chunks = to_text_chunks(text, source="job")
    assert len(chunks) == 2
    req0 = chunks[0]
    req1 = chunks[1]

    assert req0.section == "REQUIRED QUALIFICATIONS"
    assert req1.section == "PREFERRED QUALIFICATIONS"

    imp0 = detect_importance(req0.text, section=req0.section)
    imp1 = detect_importance(req1.text, section=req1.section)

    assert imp0 == "required"
    assert imp1 == "preferred"
