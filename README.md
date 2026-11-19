# GSDA – Φάση 1 (Chat + Qwen3)

Streamlit chat interface με κεντρικό Agent Controller, SQLite conversation memory,
Mock provider και Qwen3 provider (OpenAI-compatible API).

## Εγκατάσταση (Windows)

```powershell
cd C:\Users\nipro\Desktop\GSDA
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements-dev.txt
copy .env.example .env
```

## Εκκίνηση με Mock (προεπιλογή)

```powershell
.\.venv\Scripts\python -m streamlit run app\main.py
```

## Tests

```powershell
.\.venv\Scripts\python -m pytest
```

## Σύνδεση με Qwen3 στον Krylov

Βλ. [docs/KRYLOV_SETUP.md](docs/KRYLOV_SETUP.md). Συνοπτικά: άνοιξε SSH tunnel
(`ssh -L 8000:127.0.0.1:8000 krylov`), και στο `.env` όρισε `LLM_PROVIDER=qwen`.
Αν το Qwen3 δεν είναι διαθέσιμο, εμφανίζεται σφάλμα· **δεν γίνεται σιωπηλό fallback σε Mock**.

## Ενημέρωση στον Krylov μέσω Git

```bash
ssh krylov
cd /scratch/st1084601/GSDA
git pull origin main
```

(Το GSDA δεν έχει ακόμη Git repository/remote· δημιουργείται όταν το εγκρίνεις.)

## Τεκμηρίωση

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/PHASE1.md](docs/PHASE1.md)
