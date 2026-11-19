"""Ελάχιστος OpenAI-compatible server για Qwen3 (Transformers, FP16).

Τρέχει στον Krylov, μόνο στο 127.0.0.1. Εκθέτει GET /v1/models και POST /v1/chat/completions (χωρίς streaming).
Ρυθμίσεις μέσω env: GSDA_LLM_MODEL, GSDA_LLM_PORT, GSDA_LLM_API_KEY (προαιρετικό).
"""
from __future__ import annotations

import os
import threading
import time
import uuid
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

import torch
import uvicorn
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, ConfigDict
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_NAME = os.environ.get("GSDA_LLM_MODEL", "Qwen/Qwen3-8B")
PORT = int(os.environ.get("GSDA_LLM_PORT", "8000"))
API_KEY = os.environ.get("GSDA_LLM_API_KEY", "")

_lock = threading.Lock()  # μία γεννήτρια τη φορά στη GPU
_state: Dict[str, Any] = {}


@asynccontextmanager
async def lifespan(_: FastAPI):
    load_model()
    yield


app = FastAPI(title="GSDA Qwen3 server", lifespan=lifespan)


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="allow")
    model: Optional[str] = None
    messages: List[Dict[str, Any]]
    max_tokens: Optional[int] = 1024
    temperature: Optional[float] = 0.6
    top_p: Optional[float] = 0.8
    chat_template_kwargs: Optional[Dict[str, Any]] = None


def check_auth(authorization: Optional[str] = Header(default=None)) -> None:
    if API_KEY and authorization != f"Bearer {API_KEY}":
        raise HTTPException(status_code=401, detail="Invalid API key")


def load_model() -> None:
    if not torch.cuda.is_available():
        raise RuntimeError("Δεν βρέθηκε CUDA GPU.")
    _state["tok"] = AutoTokenizer.from_pretrained(MODEL_NAME)
    _state["model"] = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME, torch_dtype=torch.float16, device_map={"": 0}  # FP16: η V100 δεν υποστηρίζει BF16
    ).eval()


@app.get("/health")
def health() -> dict:
    return {"status": "ok" if "model" in _state else "loading"}


@app.get("/v1/models", dependencies=[Depends(check_auth)])
def models() -> dict:
    return {"object": "list", "data": [{"id": MODEL_NAME, "object": "model", "owned_by": "local"}]}


@app.post("/v1/chat/completions", dependencies=[Depends(check_auth)])
def chat(req: ChatRequest) -> dict:
    tok, model = _state["tok"], _state["model"]
    kwargs = req.chat_template_kwargs or {}
    text = tok.apply_chat_template(
        req.messages, tokenize=False, add_generation_prompt=True,
        enable_thinking=bool(kwargs.get("enable_thinking", False)),
    )
    inputs = tok([text], return_tensors="pt").to(model.device)
    temp = req.temperature or 0.0
    gen_kwargs: Dict[str, Any] = {"max_new_tokens": req.max_tokens or 1024}
    if temp > 0:
        gen_kwargs.update(do_sample=True, temperature=temp, top_p=req.top_p or 0.8, top_k=20)
    else:
        gen_kwargs.update(do_sample=False)

    with _lock, torch.inference_mode():
        out = model.generate(**inputs, **gen_kwargs)
    new_ids = out[0][inputs.input_ids.shape[1]:]
    content = tok.decode(new_ids, skip_special_tokens=True).strip()
    n_in, n_out = int(inputs.input_ids.shape[1]), int(new_ids.shape[0])
    return {
        "id": f"chatcmpl-{uuid.uuid4().hex[:12]}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": MODEL_NAME,
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": content},
            "finish_reason": "length" if n_out >= gen_kwargs["max_new_tokens"] else "stop",
        }],
        "usage": {"prompt_tokens": n_in, "completion_tokens": n_out, "total_tokens": n_in + n_out},
    }


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="info")
