from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class Mode:
    id: str
    name: str
    description_el: str
    icon: str
    future_functions: Tuple[int, ...] = ()
    description_en: str = ""

    def description(self, lang: str) -> str:
        return self.description_en if lang == "en" and self.description_en else self.description_el


_DESC_EN = {
    "general_chat": "Free-form scientific discussion with the Agent.",
    "literature_analysis": "Analysis of publications, methodologies, architectures and protocols.",
    "hypothesis_generation": "Creation and discussion of scientific hypotheses with justification.",
    "experiment_planning": "Experiments, variables, controls, metrics and falsification criteria.",
    "knowledge_transfer": "Transfer of knowledge and methods across models, datasets and fields.",
    "results_analysis": "Interpretation of results, model comparison, failure analysis, cross-subject generalization.",
    "scientific_validation": "Checking validity, methodology, evidence and reproducibility.",
}


GENERAL_CHAT = Mode(
    "general_chat", "General Chat", "Ελεύθερη επιστημονική συζήτηση με τον Agent.", ":material/chat:"
)

SPECIALIST_MODES: List[Mode] = [
    Mode("literature_analysis", "Literature Analysis",
         "Ανάλυση δημοσιεύσεων, μεθοδολογιών, αρχιτεκτονικών και πρωτοκόλλων.", ":material/menu_book:", (9, 10, 14)),
    Mode("hypothesis_generation", "Hypothesis Generation",
         "Δημιουργία και συζήτηση επιστημονικών υποθέσεων με αιτιολόγηση.", ":material/lightbulb:", (12, 13, 14)),
    Mode("experiment_planning", "Experiment Planning",
         "Πειράματα, μεταβλητές, έλεγχοι, μετρικές και κριτήρια διάψευσης.", ":material/science:"),
    Mode("knowledge_transfer", "Knowledge Transfer",
         "Μεταφορά γνώσης και μεθόδων μεταξύ μοντέλων, datasets και πεδίων.", ":material/swap_horiz:"),
    Mode("results_analysis", "Results Analysis",
         "Ερμηνεία αποτελεσμάτων, σύγκριση μοντέλων, ανάλυση αποτυχιών, cross-subject generalization.", ":material/bar_chart:",
         (1, 2, 3, 4, 5, 6, 7, 8)),
    Mode("scientific_validation", "Scientific Validation",
         "Έλεγχος εγκυρότητας, μεθοδολογίας, τεκμηρίωσης και αναπαραγωγιμότητας.", ":material/verified:", (10, 11)),
]

ALL_MODES: List[Mode] = [
    Mode(m.id, m.name, m.description_el, m.icon, m.future_functions, _DESC_EN[m.id])
    for m in [GENERAL_CHAT] + SPECIALIST_MODES
]
SPECIALIST_MODES = ALL_MODES[1:]
GENERAL_CHAT = ALL_MODES[0]
_BY_ID: Dict[str, Mode] = {m.id: m for m in ALL_MODES}
DEFAULT_MODE_ID = GENERAL_CHAT.id


def get_mode(mode_id: str) -> Mode:
    try:
        return _BY_ID[mode_id]
    except KeyError:
        raise KeyError(f"Άγνωστο mode: {mode_id!r}") from None
