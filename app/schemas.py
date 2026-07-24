from typing import Optional

from pydantic import BaseModel, Field


class CVProfile(BaseModel):
    """Profilo estratto dal CV del candidato."""

    skills: list[str] = Field(description="Competenze tecniche e trasversali del candidato")
    interests: list[str] = Field(description="Interessi professionali o settoriali del candidato")
    experience_years: Optional[float] = Field(
        default=None, description="Anni di esperienza lavorativa complessivi, se deducibili"
    )
    summary: str = Field(description="Breve sintesi del profilo del candidato")


class JobProfile(BaseModel):
    """Profilo estratto dalla job description."""

    titolo: Optional[str] = Field(default=None, description="Titolo della posizione")
    requisiti: list[str] = Field(description="Requisiti tecnici e competenze richieste")
    prospettive: list[str] = Field(
        description="Prospettive di crescita, responsabilità o interessi che il ruolo offre"
    )


class MatchReport(BaseModel):
    """Risultato del match tra CV e job description."""

    match_id: str
    punteggio_match: float = Field(description="Punteggio di compatibilità 0-100")
    lacune_tecniche: list[str] = Field(description="Competenze richieste dal ruolo assenti nel CV")
    lacune_esperienza: list[str] = Field(
        description="Eventuali scostamenti di esperienza rispetto ai requisiti"
    )
    allineamento_interessi: list[str] = Field(
        description="Interessi del candidato allineati con le prospettive del ruolo"
    )
    prompt_finale: str = Field(description="Report narrativo finale generato dall'LLM")
    model_used: str
