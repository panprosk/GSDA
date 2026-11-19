from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from gsda.agent.controller import AgentController
from gsda.config.settings import Settings
from gsda.conversations.repository import ConversationRepository
from gsda.conversations.service import ConversationService
from gsda.llm import LLMError, create_provider
from gsda.projects.registry import DEFAULT_PROJECT_ID

REQUESTS: list = []


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, obj):
        body = json.dumps(obj).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        self._send({"object": "list", "data": [{"id": "Qwen/Qwen3-8B", "object": "model"}]})

    def do_POST(self):
        payload = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        REQUESTS.append(payload)
        n = len(payload["messages"])
        self._send({
            "id": "x", "object": "chat.completion", "created": 0, "model": payload["model"],
            "choices": [{"index": 0, "finish_reason": "stop",
                         "message": {"role": "assistant", "content": f"<think>x</think>msgs={n}"}}],
        })


@pytest.fixture
def server():
    REQUESTS.clear()
    srv = HTTPServer(("127.0.0.1", 0), _Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{srv.server_port}/v1"
    srv.shutdown()


def test_real_http_roundtrip_keeps_context(server, tmp_path):
    s = Settings(provider="qwen", base_url=server, timeout_seconds=10, max_tokens=33, temperature=0.3)
    provider = create_provider(s)
    assert provider.check_available()[0]
    svc = ConversationService(ConversationRepository(str(tmp_path / "t.db")))
    ctl = AgentController(provider, svc)
    cid = svc.new_conversation(DEFAULT_PROJECT_ID, "results_analysis").id

    assert ctl.handle_message(cid, "πρώτο").response.content == "msgs=2"  # <think> αφαιρείται
    assert ctl.handle_message(cid, "δεύτερο").response.content == "msgs=4"
    assert REQUESTS[1]["max_tokens"] == 33 and REQUESTS[1]["temperature"] == 0.3
    assert REQUESTS[1]["model"] == "Qwen/Qwen3-8B"


def test_server_down_raises_clear_error(server):
    provider = create_provider(Settings(provider="qwen", base_url="http://127.0.0.1:9/v1", timeout_seconds=2))
    assert provider.check_available()[0] is False
    with pytest.raises(LLMError):
        provider.generate([{"role": "user", "content": "x"}])
