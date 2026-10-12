from functools import lru_cache
from typing import Any

from fastapi import HTTPException
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai.chat_models import ChatGoogleGenerativeAIError

from app.config import settings
from app.schemas import CVProfile, JobProfile


def _invoke_llm(chain, payload: dict) -> Any:
    try:
        return chain.invoke(payload)
    except ChatGoogleGenerativeAIError as exc:
        cause = exc.__cause__
        if getattr(cause, "code", None) == 429:
            raise HTTPException(
                status_code=429,
                detail=(
                    "Limite di richieste del modello Gemini raggiunto "
                    f"(modello: {settings.google_model}). Riprova tra qualche minuto."
                ),
            ) from exc
        raise HTTPException(
            status_code=502,
            detail=f"Errore nella comunicazione con il modello Gemini: {exc}",
        ) from exc


@lru_cache
def get_llm(temperature: float = 0.0) -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=settings.google_model,
        google_api_key=settings.google_api_key,
        temperature=temperature,
    )


CV_EXTRACTION_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Sei un assistente che estrae informazioni strutturate da un curriculum. "
            "Analizza il testo ed estrai competenze, interessi ed esperienza in modo fedele al contenuto.",
        ),
        ("human", "Testo del CV:\n\n{text}"),
    ]
)

JOB_EXTRACTION_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Sei un assistente che estrae informazioni strutturate da una job description. "
            "Estrai titolo, requisiti richiesti e prospettive/opportunità offerte dal ruolo.",
        ),
        ("human", "Testo della job description:\n\n{text}"),
    ]
)

NARRATIVE_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Sei un recruiter esperto. Scrivi un report narrativo breve (max 200 parole) che spiega "
            "il livello di compatibilità tra candidato e ruolo, evidenziando punti di forza, lacune "
            "e prospettive di crescita in modo costruttivo.",
        ),
        (
            "human",
            "Profilo candidato: {cv_profile}\n\n"
            "Profilo ruolo: {job_profile}\n\n"
            "Lacune tecniche: {lacune_tecniche}\n"
            "Lacune esperienza: {lacune_esperienza}\n"
            "Allineamento interessi: {allineamento_interessi}\n"
            "Punteggio match: {punteggio_match}/100",
        ),
    ]
)


def extract_cv_profile(text: str) -> CVProfile:
    chain = CV_EXTRACTION_PROMPT | get_llm().with_structured_output(CVProfile)
    return _invoke_llm(chain, {"text": text})


def extract_job_profile(text: str) -> JobProfile:
    chain = JOB_EXTRACTION_PROMPT | get_llm().with_structured_output(JobProfile)
    return _invoke_llm(chain, {"text": text})


def generate_narrative(
    cv_profile: CVProfile,
    job_profile: JobProfile,
    lacune_tecniche: list[str],
    lacune_esperienza: list[str],
    allineamento_interessi: list[str],
    punteggio_match: float,
) -> str:
    chain = NARRATIVE_PROMPT | get_llm(temperature=0.4)
    response = _invoke_llm(
        chain,
        {
            "cv_profile": cv_profile.model_dump_json(),
            "job_profile": job_profile.model_dump_json(),
            "lacune_tecniche": lacune_tecniche,
            "lacune_esperienza": lacune_esperienza,
            "allineamento_interessi": allineamento_interessi,
            "punteggio_match": punteggio_match,
        },
    )
    return response.text()
