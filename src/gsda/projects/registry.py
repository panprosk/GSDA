from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class ResearchProject:
    id: str
    name: str
    context: str


DEAP_CONTEXT = """\
Research Project: DEAP – Cross-Subject Emotion Recognition.
- Dataset: DEAP.
- Modalities: EEG, EDA/GSR, PPG/BVP.
- Στόχος: emotion recognition και cross-subject generalization.
- Υπάρχοντα μοντέλα του χρήστη: LSTM, CNN_MLP (Hybrid CNN-MLP), Cross-Attention Transformer, Mamba.
- Ερευνητική κατεύθυνση: subject variability, distribution shift, σύγκριση μοντέλων.
Σημείωση: Δεν σου έχουν δοθεί πραγματικά αποτελέσματα των μοντέλων. Αριθμητικά αποτελέσματα
θεωρούνται γνωστά μόνο αν τα αναφέρει ο χρήστης στη συνομιλία."""

_PROJECTS: List[ResearchProject] = [
    ResearchProject("deap_cross_subject", "DEAP – Cross-Subject Emotion Recognition", DEAP_CONTEXT),
]
_BY_ID: Dict[str, ResearchProject] = {p.id: p for p in _PROJECTS}

DEFAULT_PROJECT_ID = _PROJECTS[0].id


def list_projects() -> List[ResearchProject]:
    return list(_PROJECTS)


def get_project(project_id: str) -> ResearchProject:
    try:
        return _BY_ID[project_id]
    except KeyError:
        raise KeyError(f"Άγνωστο research project: {project_id!r}") from None
