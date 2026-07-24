import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, Column, DateTime, String, Text

from app.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class JobMatchResult(Base):
    __tablename__ = "job_match_results"

    id = Column(String, primary_key=True, default=_uuid)

    cv_skills = Column(JSON, nullable=False)
    cv_interests = Column(JSON, nullable=False)

    job_requisiti = Column(JSON, nullable=False)
    job_prospettive = Column(JSON, nullable=False)

    lacune_tecniche = Column(JSON, nullable=False)
    lacune_esperienza = Column(JSON, nullable=False)
    allineamento_interessi = Column(JSON, nullable=False)

    prompt_finale = Column(Text, nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    model_used = Column(String, nullable=False)
