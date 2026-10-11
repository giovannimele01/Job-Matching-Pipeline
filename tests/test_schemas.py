import pytest
from pydantic import ValidationError

from app.schemas import CVProfile, JobProfile, MatchReport


def test_cv_profile_experience_years_defaults_to_none():
    cv = CVProfile(skills=["Python"], interests=["AI"], summary="Backend developer")

    assert cv.experience_years is None


def test_cv_profile_requires_summary():
    with pytest.raises(ValidationError):
        CVProfile(skills=["Python"], interests=["AI"])


def test_job_profile_titolo_is_optional():
    job = JobProfile(requisiti=["Python"], prospettive=["Crescita"])

    assert job.titolo is None


def test_job_profile_requires_requisiti():
    with pytest.raises(ValidationError):
        JobProfile(prospettive=["Crescita"])


def test_match_report_round_trip():
    report = MatchReport(
        match_id="abc-123",
        punteggio_match=80.0,
        lacune_tecniche=["kubernetes"],
        lacune_esperienza=[],
        allineamento_interessi=["ai"],
        prompt_finale="Candidato promettente.",
        model_used="gemini-3.5-flash",
    )

    assert report.match_id == "abc-123"
    assert report.punteggio_match == 80.0
