from __future__ import annotations

import streamlit as st

LANGUAGES = {"el": "Ελληνικά", "en": "English"}

_STRINGS = {
    "el": {
        "language": "Γλώσσα",
        "new_conversation": ":material/add: Νέα συνομιλία",
        "project": "Ερευνητικό Project",
        "mode": "Mode",
        "history": "Ιστορικό",
        "no_history": "Δεν υπάρχουν συνομιλίες ακόμη.",
        "delete": "Διαγραφή",
        "delete_confirm": "Η συνομιλία θα διαγραφεί οριστικά.",
        "check_conn": "Έλεγχος σύνδεσης",
        "welcome": "Καλώς ήρθες! Ξεκίνα μια ελεύθερη συζήτηση (**General Chat**) ή διάλεξε μία από τις "
                   "έξι εξειδικευμένες επιλογές από τα πλαίσια παρακάτω ή από την πλαϊνή μπάρα.",
        "select": "Επιλογή",
        "selected": ":material/check: Επιλεγμένο",
        "placeholder": "Γράψε το ερώτημά σου…",
        "thinking": "Το Qwen3 σκέφτεται…",
        "mock_warning": "Λειτουργία **Mock**: οι απαντήσεις δεν προέρχονται από Qwen3.",
        "mock_reply": ":material/warning: Mock απάντηση",
        "llm_error": "Σφάλμα LLM",
    },
    "en": {
        "language": "Language",
        "new_conversation": ":material/add: New Conversation",
        "project": "Research Project",
        "mode": "Mode",
        "history": "History",
        "no_history": "No conversations yet.",
        "delete": "Delete",
        "delete_confirm": "This conversation will be permanently deleted.",
        "check_conn": "Check connection",
        "welcome": "Welcome! Start a free conversation (**General Chat**) or pick one of the six "
                   "specialist options from the cards below or from the sidebar.",
        "select": "Select",
        "selected": ":material/check: Selected",
        "placeholder": "Type your question…",
        "thinking": "Qwen3 is thinking…",
        "mock_warning": "**Mock** mode: answers do not come from Qwen3.",
        "mock_reply": ":material/warning: Mock reply",
        "llm_error": "LLM error",
    },
}


def current_language() -> str:
    return st.session_state.get("language", "el")


def t(key: str) -> str:
    return _STRINGS[current_language()][key]
