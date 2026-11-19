# Αρχιτεκτονική GSDA (Φάση 1)

```
Streamlit (app/) ──> AgentController ──> LLMProvider (Mock | Qwen3/OpenAI API)
                          │
                          └──> ConversationService ──> SQLite (data/gsda.db)
```

Ροή μηνύματος: UI → `AgentController.handle_message` → system prompt (base + mode + project context)
+ πρόσφατα N μηνύματα (`GSDA_CONTEXT_MAX_MESSAGES`) + νέο μήνυμα → provider → απάντηση →
αποθήκευση user+assistant στη SQLite → UI. Σε σφάλμα provider δεν αποθηκεύεται τίποτα.

| Module | Ρόλος |
|---|---|
| `gsda/agent/controller.py` | Κεντρικός controller, ανεξάρτητος από UI/provider |
| `gsda/agent/modes.py`, `prompts.py` | General Chat + 6 modes, system prompts |
| `gsda/llm/` | `LLMProvider` interface, Mock, Qwen (OpenAI SDK) |
| `gsda/projects/registry.py` | Research projects (προς το παρόν DEAP) |
| `gsda/conversations/` | SQLite repository + service (history, context window) |
| `gsda/config/settings.py` | Ρυθμίσεις από environment variables |

Μια συνομιλία κρατά το project και το mode της δημιουργίας· αλλαγή τους στο UI ξεκινά νέα συνομιλία.

## Αντιστοίχιση μελλοντικών 14 λειτουργιών (δεν υλοποιούνται στη Φάση 1)

| Επιλογή | Λειτουργίες |
|---|---|
| Literature Analysis | 9, 10, 14 |
| Hypothesis Generation | 12, 13, 14 |
| Experiment Planning | υποστήριξη σχεδιασμού πειραμάτων |
| Knowledge Transfer | μεταφορά μεθόδων/γνώσης |
| Results Analysis | 1–8 |
| Scientific Validation | 10, 11 |

1 Subject Identity vs Emotion · 2 Subject Intelligence & Failure Diagnosis · 3 Cross-Model Failure
Fingerprint · 4 Model Disagreement · 5 Modality Contribution · 6 Training Subject Utility · 7 Emotion Label
Ambiguity · 8 Subject Distribution Shift · 9 Literature-Guided Method Extractor · 10 Literature Protocol
Auditor · 11 Evidence & Reproducibility Graph · 12 Hypothesis Generator · 13 Hypothesis Prioritization ·
14 Research Gap & Novelty Detector.

Οι επόμενες φάσεις (2–10) ακολουθούν τον οδικό χάρτη του αρχικού σχεδίου.
