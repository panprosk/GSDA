from __future__ import annotations

import httpx2 as httpx
import openai
import pytest

from gsda.agent.controller import AgentController
from gsda.agent.modes import ALL_MODES, SPECIALIST_MODES, get_mode
from gsda.agent.prompts import MODE_PROMPTS, build_system_prompt
from gsda.config.settings import Settings
from gsda.conversations.repository import ConversationRepository
from gsda.conversations.service import ConversationService
from gsda.llm import LLMError, MockProvider, QwenProvider, create_provider
from gsda.llm.base import LLMProvider, LLMResponse
from gsda.llm.mock_provider import MOCK_BANNER
from gsda.projects.registry import DEFAULT_PROJECT_ID, get_project


@pytest.fixture
def service(tmp_path):
    return ConversationService(ConversationRepository(str(tmp_path / "t.db")), context_max_messages=4)


class Recorder(LLMProvider):
    def __init__(self):
        self.calls = []

    def generate(self, messages):
        self.calls.append(messages)
        return LLMResponse("απάντηση", "rec", "rec")


# ---- Settings / provider ----
def test_settings_from_env_and_defaults():
    assert Settings.from_env({}).provider == "mock"
    s = Settings.from_env({
        "LLM_PROVIDER": "Qwen", "LLM_BASE_URL": "http://x/v1", "LLM_API_KEY": "secret",
        "LLM_MODEL": "m", "LLM_TIMEOUT_SECONDS": "5", "LLM_MAX_TOKENS": "7", "LLM_TEMPERATURE": "0.1",
    })
    assert (s.provider, s.base_url, s.model, s.timeout_seconds, s.max_tokens, s.temperature) == (
        "qwen", "http://x/v1", "m", 5.0, 7, 0.1)
    assert "secret" not in repr(s)


def test_mock_provider_is_labelled():
    r = MockProvider().generate([{"role": "user", "content": "γεια"}])
    assert r.is_mock and MOCK_BANNER in r.content


def test_create_provider_selection():
    assert isinstance(create_provider(Settings()), MockProvider)
    assert isinstance(create_provider(Settings(provider="qwen")), QwenProvider)
    with pytest.raises(LLMError):
        create_provider(Settings(provider="nope"))


def test_qwen_request_shape():
    p = QwenProvider(Settings(provider="qwen", model="Qwen/Qwen3-8B", max_tokens=9, temperature=0.2))
    req = p.build_request([{"role": "user", "content": "x"}])
    assert req["model"] == "Qwen/Qwen3-8B" and req["max_tokens"] == 9 and req["temperature"] == 0.2
    assert req["extra_body"]["chat_template_kwargs"]["enable_thinking"] is False


class _FakeCompletions:
    def __init__(self, exc):
        self.exc = exc

    def create(self, **kw):
        raise self.exc


class _FakeClient:
    def __init__(self, exc):
        self.chat = type("C", (), {"completions": _FakeCompletions(exc)})()


def test_truncated_answer_is_continued():
    class _Resp:
        def __init__(self, text, reason):
            msg = type("M", (), {"content": text})()
            self.choices = [type("Ch", (), {"message": msg, "finish_reason": reason})()]

    calls = []

    class _Comp:
        def create(self, **kw):
            calls.append(kw["messages"])
            return _Resp("part one ", "length") if len(calls) == 1 else _Resp("part two", "stop")

    client = type("C", (), {"chat": type("X", (), {"completions": _Comp()})()})()
    r = QwenProvider(Settings(provider="qwen"), client=client).generate([{"role": "user", "content": "x"}])
    assert r.content == "part one part two" and len(calls) == 2
    assert calls[1][-2] == {"role": "assistant", "content": "part one "}


_REQ = httpx.Request("POST", "http://x/v1/chat/completions")


@pytest.mark.parametrize("exc,needle", [
    (openai.APITimeoutError(request=_REQ), "Timeout"),
    (openai.APIConnectionError(request=_REQ), "σύνδεσης"),
])
def test_qwen_errors_are_not_silenced(exc, needle):
    p = QwenProvider(Settings(provider="qwen"), client=_FakeClient(exc))
    with pytest.raises(LLMError, match=needle):
        p.generate([{"role": "user", "content": "x"}])


def test_unreachable_qwen_does_not_fall_back_to_mock(tmp_path):
    s = Settings(provider="qwen", base_url="http://127.0.0.1:9/v1", timeout_seconds=2, api_key="topsecret")
    svc = ConversationService(ConversationRepository(str(tmp_path / "t.db")))
    ctl = AgentController(create_provider(s), svc)
    cid = svc.new_conversation(DEFAULT_PROJECT_ID, "general_chat").id
    with pytest.raises(LLMError) as ei:
        ctl.handle_message(cid, "γεια")
    assert "topsecret" not in str(ei.value)
    assert svc.messages(cid) == []


# ---- Prompts / modes ----
def test_seven_modes_with_prompts():
    assert len(SPECIALIST_MODES) == 6 and len(ALL_MODES) == 7
    ctx = get_project(DEFAULT_PROJECT_ID).context
    prompts = {build_system_prompt(m.id, ctx) for m in ALL_MODES}
    assert len(prompts) == 7 and set(MODE_PROMPTS) == {m.id for m in ALL_MODES}
    for p in prompts:
        assert "DEAP" in p and "Μην επινοείς" in p


def test_language_directive_in_prompt():
    ctx = get_project(DEFAULT_PROJECT_ID).context
    assert "ΑΠΟΚΛΕΙΣΤΙΚΑ στα ελληνικά" in build_system_prompt("general_chat", ctx, "el")
    en = build_system_prompt("general_chat", ctx, "en")
    assert "ENTIRELY in English" in en and "ΑΠΟΚΛΕΙΣΤΙΚΑ στα ελληνικά" not in en
    assert get_mode("general_chat").description("en").startswith("Free-form")


def test_delete_conversation_removes_messages_from_db(service):
    keep = service.new_conversation(DEFAULT_PROJECT_ID, "general_chat").id
    gone = service.new_conversation(DEFAULT_PROJECT_ID, "general_chat").id
    service.add_exchange(keep, "a", "b")
    service.add_exchange(gone, "c", "d")
    assert service.delete(gone) is True
    assert service.get(gone) is None and service.messages(gone) == []
    assert [m.content for m in service.messages(keep)] == ["a", "b"]
    assert service.delete(gone) is False
    conn = service.repo._connect()
    try:
        assert conn.execute("SELECT COUNT(*) FROM messages WHERE conversation_id=?", (gone,)).fetchone()[0] == 0
    finally:
        conn.close()


# ---- Memory ----
def test_conversation_roundtrip_and_isolation(service):
    a = service.new_conversation(DEFAULT_PROJECT_ID, "results_analysis")
    b = service.new_conversation(DEFAULT_PROJECT_ID, "general_chat")
    service.add_exchange(a.id, "q1", "a1")
    service.add_exchange(b.id, "other", "x")
    got = service.get(a.id)
    assert (got.project_id, got.mode_id) == (DEFAULT_PROJECT_ID, "results_analysis")
    assert [(m.role, m.content) for m in service.messages(a.id)] == [("user", "q1"), ("assistant", "a1")]
    assert len(service.messages(b.id)) == 2
    assert service.history()[0].id == b.id  # πιο πρόσφατη πρώτη


def test_context_is_limited_and_ordered(service):
    c = service.new_conversation(DEFAULT_PROJECT_ID, "general_chat")
    for i in range(5):
        service.add_exchange(c.id, f"u{i}", f"a{i}")
    assert [m.content for m in service.recent_context(c.id)] == ["u3", "a3", "u4", "a4"]


def test_invalid_project_or_mode_rejected(service):
    with pytest.raises(KeyError):
        service.new_conversation("nope", "general_chat")
    with pytest.raises(KeyError):
        service.new_conversation(DEFAULT_PROJECT_ID, "nope")


# ---- Controller ----
def test_controller_builds_context_and_saves(service):
    rec = Recorder()
    ctl = AgentController(rec, service)
    c = service.new_conversation(DEFAULT_PROJECT_ID, "hypothesis_generation")
    ctl.handle_message(c.id, "EEG-only F1 0.53")
    reply = ctl.handle_message(c.id, "Γιατί η διαφορά;")
    assert reply.response.content == "απάντηση"
    msgs = rec.calls[1]
    assert msgs[0]["role"] == "system" and "Hypothesis Generation" in msgs[0]["content"]
    assert [m["content"] for m in msgs[1:]] == ["EEG-only F1 0.53", "απάντηση", "Γιατί η διαφορά;"]
    assert len(service.messages(c.id)) == 4
    assert all("tools" not in str(k) for call in rec.calls for k in call)


def test_controller_uses_each_mode_prompt(service):
    rec = Recorder()
    ctl = AgentController(rec, service)
    for m in ALL_MODES:
        c = service.new_conversation(DEFAULT_PROJECT_ID, m.id)
        ctl.handle_message(c.id, "hi")
        assert MODE_PROMPTS[m.id] in rec.calls[-1][0]["content"]

