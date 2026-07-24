from app.schemas import CVProfile, JobProfile


def _normalize(items: list[str]) -> set[str]:
    return {item.strip().lower() for item in items if item.strip()}


def compute_match(cv: CVProfile, job: JobProfile) -> dict:
    cv_skills = _normalize(cv.skills)
    cv_interests = _normalize(cv.interests)
    job_requisiti = _normalize(job.requisiti)
    job_prospettive = _normalize(job.prospettive)

    lacune_tecniche = sorted(job_requisiti - cv_skills)
    allineamento_interessi = sorted(cv_interests & job_prospettive)

    lacune_esperienza: list[str] = []
    if cv.experience_years is not None and job_requisiti:
        # Segnala una lacuna generica di esperienza se il candidato ha meno di 1 anno
        # e il ruolo ha requisiti tecnici espliciti (euristica semplice, non l'unico segnale).
        if cv.experience_years < 1:
            lacune_esperienza.append("Esperienza lavorativa limitata rispetto ai requisiti del ruolo")

    if job_requisiti:
        skill_coverage = len(job_requisiti & cv_skills) / len(job_requisiti)
    else:
        skill_coverage = 1.0

    if job_prospettive:
        interest_coverage = len(allineamento_interessi) / len(job_prospettive)
    else:
        interest_coverage = 1.0

    punteggio_match = round((0.7 * skill_coverage + 0.3 * interest_coverage) * 100, 2)

    return {
        "lacune_tecniche": lacune_tecniche,
        "lacune_esperienza": lacune_esperienza,
        "allineamento_interessi": allineamento_interessi,
        "punteggio_match": punteggio_match,
    }
