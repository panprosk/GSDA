from __future__ import annotations

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parents[1] / "app" / "main.py")


@pytest.fixture
def app(tmp_path, monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    monkeypatch.setenv("GSDA_DB_PATH", str(tmp_path / "ui.db"))
    at = AppTest.from_file(APP, default_timeout=30)
    at.run()
    assert not at.exception
    return at


def test_app_starts_with_modes_project_and_new_conversation(app):
    assert len(app.sidebar.radio[1].options) == 7
    assert app.sidebar.radio[1].value == "general_chat"
    assert app.sidebar.selectbox[0].label == "Ερευνητικό Project"
    assert any(b.label.endswith("Νέα συνομιλία") for b in app.sidebar.button)
    assert any("Mock" in w.value for w in app.warning)
    app.sidebar.radio[0].set_value("en").run()
    assert app.sidebar.selectbox[0].label == "Research Project"
    assert any(b.label.endswith("New Conversation") for b in app.sidebar.button)


def test_chat_history_and_mode_switch_starts_new_conversation(app):
    app.chat_input[0].set_value("Γεια σου").run()
    assert not app.exception
    assert any("MOCK" in m.value for m in app.markdown)
    conv1 = app.session_state["conversation_id"]
    assert conv1
    assert any("Γεια σου" in b.label for b in app.sidebar.button)

    app.sidebar.radio[1].set_value("results_analysis").run()
    assert app.session_state["conversation_id"] is None
    app.chat_input[0].set_value("Ανάλυση").run()
    conv2 = app.session_state["conversation_id"]
    assert conv2 and conv2 != conv1

    restore = next(b for b in app.sidebar.button if "Γεια σου" in b.label)
    restore.click().run()
    assert app.session_state["conversation_id"] == conv1
    assert app.session_state["mode_id"] == "general_chat"
