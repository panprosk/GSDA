from __future__ import annotations

import streamlit as st

from app.components.i18n import current_language, t
from gsda.agent.modes import SPECIALIST_MODES


def _select_mode(mode_id: str) -> None:
    st.session_state["mode_id"] = mode_id
    st.session_state["conversation_id"] = None


def render_welcome() -> None:
    st.markdown(t("welcome"))
    lang = current_language()
    current = st.session_state.get("mode_id")
    cols = st.columns(3)
    for i, mode in enumerate(SPECIALIST_MODES):
        active = mode.id == current
        prefix = "card_active_" if active else "card_"
        with cols[i % 3].container(key=f"{prefix}{mode.id}"):
            st.markdown(f"**{mode.icon} {mode.name}**")
            st.markdown(f'<div class="gsda-card-desc">{mode.description(lang)}</div>', unsafe_allow_html=True)
            st.button(
                t("selected") if active else t("select"),
                key=f"pick_{mode.id}",
                on_click=_select_mode,
                args=(mode.id,),
                type="primary" if active else "secondary",
                use_container_width=True,
            )
