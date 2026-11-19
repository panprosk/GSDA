from __future__ import annotations

import streamlit as st

from app.components.i18n import LANGUAGES, current_language, t
from gsda.agent.modes import ALL_MODES, DEFAULT_MODE_ID, get_mode
from gsda.projects.registry import DEFAULT_PROJECT_ID, get_project, list_projects


def _reset_conversation() -> None:
    # Αλλαγή project/mode => νέα (lazy) συνομιλία, ώστε να μην αναμειγνύονται contexts.
    st.session_state["conversation_id"] = None


def _open_conversation(conv_id: str, project_id: str, mode_id: str) -> None:
    st.session_state["conversation_id"] = conv_id
    st.session_state["project_id"] = project_id
    st.session_state["mode_id"] = mode_id


def _delete_conversation(service, conv_id: str) -> None:
    service.delete(conv_id)
    if st.session_state.get("conversation_id") == conv_id:
        st.session_state["conversation_id"] = None


def render_sidebar(service, settings, controller) -> None:
    st.session_state.setdefault("project_id", DEFAULT_PROJECT_ID)
    st.session_state.setdefault("mode_id", DEFAULT_MODE_ID)
    projects = list_projects()

    with st.sidebar:
        st.header("GSDA")
        st.radio(
            t("language"),
            list(LANGUAGES),
            format_func=LANGUAGES.get,
            key="language",
            horizontal=True,
        )
        if st.button(t("new_conversation"), use_container_width=True, key="new_conversation"):
            _reset_conversation()
            st.rerun()

        st.selectbox(
            t("project"),
            [p.id for p in projects],
            format_func=lambda pid: get_project(pid).name,
            key="project_id",
            on_change=_reset_conversation,
        )
        lang = current_language()
        st.radio(
            t("mode"),
            [m.id for m in ALL_MODES],
            format_func=lambda mid: f"{get_mode(mid).icon} {get_mode(mid).name}",
            captions=[m.description(lang) for m in ALL_MODES],
            key="mode_id",
            on_change=_reset_conversation,
        )

        st.subheader(t("history"))
        history = service.history(st.session_state["project_id"])
        if not history:
            st.caption(t("no_history"))
        for c in history:
            active = c.id == st.session_state.get("conversation_id")
            col_open, col_del = st.columns([5, 1], vertical_alignment="center")
            col_open.button(
                (":material/chevron_right: " if active else "") + f"{get_mode(c.mode_id).icon} {c.title}",
                key=f"conv_{c.id}",
                use_container_width=True,
                on_click=_open_conversation,
                args=(c.id, c.project_id, c.mode_id),
            )
            with col_del.popover(":material/delete:", help=t("delete")):
                st.caption(t("delete_confirm"))
                st.button(
                    t("delete"),
                    key=f"del_{c.id}",
                    type="primary",
                    use_container_width=True,
                    on_click=_delete_conversation,
                    args=(service, c.id),
                )

        st.divider()
        if settings.provider == "mock":
            st.caption("Provider: mock")
        else:
            st.caption(f"Provider: {settings.provider} • {settings.model}")
            if controller is not None and st.button(t("check_conn"), key="check_conn"):
                ok, msg = controller.provider.check_available()
                (st.success if ok else st.error)(msg)
