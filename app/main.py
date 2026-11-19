from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (ROOT / "src", ROOT):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import streamlit as st
from dotenv import load_dotenv

from app.components.i18n import current_language, t
from app.components.sidebar import render_sidebar
from app.components.styles import inject_styles
from app.components.welcome import render_welcome
from gsda.agent.controller import AgentController
from gsda.agent.modes import get_mode
from gsda.config.settings import Settings
from gsda.conversations.repository import ConversationRepository
from gsda.conversations.service import ConversationService
from gsda.llm import LLMError, create_provider
from gsda.projects.registry import get_project


def _db_path(settings: Settings) -> str:
    p = Path(settings.db_path)
    return str(p if p.is_absolute() else ROOT / p)


def _get_controller() -> tuple[AgentController, ConversationService, Settings]:
    if "controller" not in st.session_state:
        load_dotenv(ROOT / ".env")
        settings = Settings.from_env()
        service = ConversationService(
            ConversationRepository(_db_path(settings)), settings.context_max_messages
        )
        try:
            provider = create_provider(settings)
            st.session_state["provider_error"] = None
        except LLMError as e:
            provider, st.session_state["provider_error"] = None, str(e)
        st.session_state["settings"] = settings
        st.session_state["service"] = service
        st.session_state["controller"] = AgentController(provider, service) if provider else None
    return st.session_state["controller"], st.session_state["service"], st.session_state["settings"]


def main() -> None:
    st.set_page_config(page_title="GSDA", page_icon=":material/biotech:", layout="wide")
    controller, service, settings = _get_controller()

    st.session_state.setdefault("conversation_id", None)
    st.session_state.setdefault("language", "el")
    render_sidebar(service, settings, controller)

    project_id = st.session_state["project_id"]
    mode_id = st.session_state["mode_id"]
    mode = get_mode(mode_id)

    inject_styles()
    st.markdown(
        '<div class="gsda-hero"><h1>GSDA</h1>'
        '<div class="gsda-sub">General Scientific Discovery Agent</div>'
        '<div class="gsda-badges">'
        f'<span class="gsda-badge">Project: {get_project(project_id).name}</span>'
        f'<span class="gsda-badge mode">Mode: {mode.name}</span>'
        "</div></div>",
        unsafe_allow_html=True,
    )

    if settings.provider == "mock":
        st.warning(t("mock_warning"))
    if st.session_state.get("provider_error"):
        st.error(st.session_state["provider_error"])
        return

    conv_id = st.session_state["conversation_id"]
    messages = service.messages(conv_id) if conv_id else []

    if not messages:
        render_welcome()
    for m in messages:
        with st.chat_message(m.role):
            st.markdown(m.content)

    prompt = st.chat_input(t("placeholder"))
    if not prompt:
        return

    if conv_id is None:
        conv_id = service.new_conversation(project_id, mode_id).id
        st.session_state["conversation_id"] = conv_id

    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        try:
            with st.spinner(t("thinking") if settings.provider != "mock" else "Mock…"):
                reply = controller.handle_message(conv_id, prompt, current_language())
            st.markdown(reply.response.content)
            if reply.response.is_mock:
                st.caption(t("mock_reply"))
            st.rerun()
        except LLMError as e:
            st.error(f"{t('llm_error')}: {e}")


main()
