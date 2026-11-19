# Φάση 1 – Κατάσταση

Υλοποιημένα: Streamlit chat, General Chat + 6 modes, Research Project selector, New Conversation,
ιστορικό/επαναφορά, SQLite memory με όριο context, Agent Controller, Mock και Qwen3 provider,
tests (`pytest`, 17 tests).

Επαληθευμένο στην πράξη (Qwen3-8B FP16 στη V100 του Krylov, μέσω SSH tunnel):
`scripts/e2e_qwen_check.py` – απάντηση στα ελληνικά, διατήρηση context στην ίδια συνομιλία και
απομόνωση σε νέα συνομιλία με άλλο mode.

Δεν υλοποιούνται (μελλοντικές φάσεις): tools, RAG, Scientific Memory, Model/Dataset adapters, streaming.

Οδηγίες server/tunnel: [KRYLOV_SETUP.md](KRYLOV_SETUP.md).
