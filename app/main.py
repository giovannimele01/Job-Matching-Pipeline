from fastapi import Depends, FastAPI, UploadFile
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db, init_db
from app.extraction import extract_text
from app.llm import extract_cv_profile, extract_job_profile, generate_narrative
from app.matching import compute_match
from app.models import JobMatchResult
from app.schemas import MatchReport

app = FastAPI(title="Job Matcher Pipeline")


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "model": settings.google_model}


@app.post("/match", response_model=MatchReport)
async def match(
    cv: UploadFile,
    job_desc: UploadFile,
    db: Session = Depends(get_db),
) -> MatchReport:
    cv_text = await extract_text(cv)
    job_text = await extract_text(job_desc)

    cv_profile = extract_cv_profile(cv_text)
    job_profile = extract_job_profile(job_text)

    match_data = compute_match(cv_profile, job_profile)

    prompt_finale = generate_narrative(
        cv_profile=cv_profile,
        job_profile=job_profile,
        **match_data,
    )

    result = JobMatchResult(
        cv_skills=cv_profile.skills,
        cv_interests=cv_profile.interests,
        job_requisiti=job_profile.requisiti,
        job_prospettive=job_profile.prospettive,
        lacune_tecniche=match_data["lacune_tecniche"],
        lacune_esperienza=match_data["lacune_esperienza"],
        allineamento_interessi=match_data["allineamento_interessi"],
        prompt_finale=prompt_finale,
        model_used=settings.google_model,
    )
    db.add(result)
    db.commit()
    db.refresh(result)

    return MatchReport(
        match_id=result.id,
        punteggio_match=match_data["punteggio_match"],
        lacune_tecniche=match_data["lacune_tecniche"],
        lacune_esperienza=match_data["lacune_esperienza"],
        allineamento_interessi=match_data["allineamento_interessi"],
        prompt_finale=prompt_finale,
        model_used=settings.google_model,
    )
