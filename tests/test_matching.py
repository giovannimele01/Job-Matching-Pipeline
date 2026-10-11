from app.matching import compute_match
from app.schemas import CVProfile, JobProfile


def _cv(skills, interests, experience_years=None, summary="test"):
    return CVProfile(skills=skills, interests=interests, experience_years=experience_years, summary=summary)


def _job(requisiti, prospettive, titolo=None):
    return JobProfile(titolo=titolo, requisiti=requisiti, prospettive=prospettive)


def test_full_skill_and_interest_overlap_scores_100():
    cv = _cv(skills=["Python", "FastAPI"], interests=["AI"])
    job = _job(requisiti=["python", "fastapi"], prospettive=["ai"])

    result = compute_match(cv, job)

    assert result["lacune_tecniche"] == []
    assert result["allineamento_interessi"] == ["ai"]
    assert result["punteggio_match"] == 100.0


def test_partial_skill_gap_lists_missing_requisiti():
    cv = _cv(skills=["Python", "FastAPI", "Docker"], interests=["Mentoring"])
    job = _job(requisiti=["Python", "FastAPI", "Docker", "Kubernetes"], prospettive=["Crescita", "Mentoring"])

    result = compute_match(cv, job)

    assert result["lacune_tecniche"] == ["kubernetes"]
    assert result["allineamento_interessi"] == ["mentoring"]
    assert result["punteggio_match"] == 67.5


def test_no_interest_overlap_returns_empty_list():
    cv = _cv(skills=["Python"], interests=["Cucina"])
    job = _job(requisiti=["Python"], prospettive=["Crescita"])

    result = compute_match(cv, job)

    assert result["allineamento_interessi"] == []


def test_low_experience_flags_gap_when_job_has_requisiti():
    cv = _cv(skills=["Python"], interests=[], experience_years=0.5)
    job = _job(requisiti=["Python"], prospettive=[])

    result = compute_match(cv, job)

    assert result["lacune_esperienza"] == [
        "Esperienza lavorativa limitata rispetto ai requisiti del ruolo"
    ]


def test_sufficient_experience_does_not_flag_gap():
    cv = _cv(skills=["Python"], interests=[], experience_years=3)
    job = _job(requisiti=["Python"], prospettive=[])

    result = compute_match(cv, job)

    assert result["lacune_esperienza"] == []


def test_missing_experience_years_does_not_flag_gap():
    cv = _cv(skills=["Python"], interests=[], experience_years=None)
    job = _job(requisiti=["Python"], prospettive=[])

    result = compute_match(cv, job)

    assert result["lacune_esperienza"] == []


def test_low_experience_ignored_when_job_has_no_requisiti():
    cv = _cv(skills=["Python"], interests=[], experience_years=0.2)
    job = _job(requisiti=[], prospettive=[])

    result = compute_match(cv, job)

    assert result["lacune_esperienza"] == []


def test_empty_job_requisiti_and_prospettive_score_full_coverage():
    cv = _cv(skills=["Python"], interests=["AI"])
    job = _job(requisiti=[], prospettive=[])

    result = compute_match(cv, job)

    assert result["punteggio_match"] == 100.0


def test_case_and_whitespace_are_normalized():
    cv = _cv(skills=[" Python ", "FASTAPI"], interests=[])
    job = _job(requisiti=["python", "fastapi"], prospettive=[])

    result = compute_match(cv, job)

    assert result["lacune_tecniche"] == []
