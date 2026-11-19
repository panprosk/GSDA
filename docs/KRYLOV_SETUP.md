# Qwen3-8B στον Krylov

Εγκατάσταση που έγινε (host `krylov100`, V100-PCIE-32GB, χωρίς scheduler, `/scratch` μη εγγράψιμο):

- Φάκελος: `~/gsda_llm/{venv,models,server,logs}` (ξεχωριστός από το thesis).
- Python 3.11.13, `torch==2.6.0+cu118`, `transformers==4.51.3`, `huggingface_hub>=0.34,<1.0`, accelerate, safetensors, fastapi, uvicorn.
- Μοντέλο `Qwen/Qwen3-8B` σε FP16 (~18.4 GB GPU) με `HF_HOME=~/gsda_llm/models`.
- Server: `server/qwen_server.py` (OpenAI-compatible, μόνο `127.0.0.1:8000`).

## Ενημέρωση του server στον Krylov (Windows PowerShell, φάκελος GSDA)

```powershell
scp server\qwen_server.py krylov:gsda_llm/server/qwen_server.py
```

## Εκκίνηση server (στον Krylov, σε tmux ώστε να μη σταματά με την αποσύνδεση)

```bash
tmux new -s qwen
export HF_HOME=~/gsda_llm/models
~/gsda_llm/venv/bin/python ~/gsda_llm/server/qwen_server.py
# Ctrl+B, μετά D για αποσύνδεση.  Επιστροφή: tmux attach -t qwen
```

Η GPU είναι κοινόχρηστη μηχανή· έλεγξε με `nvidia-smi` πριν την εκκίνηση.

## SSH tunnel (Windows PowerShell, αφήνεται ανοιχτό)

```powershell
ssh -L 8000:127.0.0.1:8000 krylov
```

## Ρύθμιση GSDA (.env)

```env
LLM_PROVIDER=qwen
LLM_BASE_URL=http://127.0.0.1:8000/v1
LLM_MODEL=Qwen/Qwen3-8B
```

Το κουμπί «Έλεγχος σύνδεσης» στο sidebar καλεί `GET /v1/models`.
Γρήγορος έλεγχος χωρίς UI: `.\.venv\Scripts\python scripts\e2e_qwen_check.py`.
