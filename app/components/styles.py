from __future__ import annotations

import streamlit as st

_CSS = """
<style>
.block-container { padding-top: 2.5rem; max-width: 1200px; }
header[data-testid="stHeader"] { background: transparent; }

.gsda-hero { padding: 0.5rem 0 1.25rem 0; border-bottom: 1px solid rgba(128,128,128,.25); margin-bottom: 1.25rem; }
.gsda-hero h1 { font-size: 2rem; font-weight: 700; margin: 0; padding: 0; letter-spacing: -0.01em; }
.gsda-hero .gsda-sub { color: #6b7280; font-size: .95rem; margin-top: .25rem; }
.gsda-badges { margin-top: .75rem; display: flex; gap: .5rem; flex-wrap: wrap; }
.gsda-badge { display: inline-block; padding: .2rem .7rem; border-radius: 999px; font-size: .8rem;
  background: rgba(37,99,235,.08); color: #1d4ed8; border: 1px solid rgba(37,99,235,.25); }
.gsda-badge.mode { background: rgba(5,150,105,.08); color: #047857; border-color: rgba(5,150,105,.3); }

[class*="st-key-card_"] { border: 1px solid rgba(128,128,128,.3); border-radius: 12px; padding: 1rem 1.1rem;
  background: rgba(128,128,128,.04); transition: box-shadow .15s, border-color .15s; height: 100%; }
[class*="st-key-card_"]:hover { border-color: #2563eb; box-shadow: 0 4px 14px rgba(37,99,235,.12); }
[class*="st-key-card_"].gsda-active, [class*="st-key-card_active_"] { border: 2px solid #2563eb; background: rgba(37,99,235,.06); }
.gsda-card-title { font-weight: 600; font-size: 1.02rem; margin-bottom: .25rem; }
.gsda-card-desc { color: #6b7280; font-size: .88rem; min-height: 2.6rem; margin-bottom: .6rem; }

section[data-testid="stSidebar"] { border-right: 1px solid rgba(128,128,128,.2); }
section[data-testid="stSidebar"] h2 { font-size: 1.25rem; font-weight: 700; }

[data-testid="stChatMessage"] { border-radius: 12px; padding: .75rem 1rem; margin-bottom: .5rem; }
</style>
"""


def inject_styles() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)
