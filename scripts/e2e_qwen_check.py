"""Χειροκίνητη end-to-end δοκιμή GSDA <-> Qwen3 μέσω tunnel (δεν τρέχει στο pytest)."""
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dotenv import load_dotenv

from gsda.agent.controller import AgentController
from gsda.config.settings import Settings
from gsda.conversations.repository import ConversationRepository
from gsda.conversations.service import ConversationService
from gsda.llm import create_provider

load_dotenv(ROOT / ".env")
s = Settings.from_env()
print("provider:", s.provider, "| url:", s.base_url, "| model:", s.model)
provider = create_provider(s)
print("check_available:", provider.check_available())

svc = ConversationService(ConversationRepository(str(Path(tempfile.mkdtemp()) / "e2e.db")), s.context_max_messages)
ctl = AgentController(provider, svc)

c1 = svc.new_conversation("deap_cross_subject", "general_chat").id
print("\n[General Chat] 1:", ctl.handle_message(c1, "Τι σημαίνει cross-subject generalization στο DEAP; Απάντησε σε 2 προτάσεις.").response.content)
print("\n[General Chat] 2 (memory):", ctl.handle_message(c1, "Το EEG-only έχει F1 0.53 και το EEG+EDA+PPG 0.50. Γιατί υπάρχει αυτή η διαφορά; Σύντομα.").response.content)
print("\n[General Chat] 3 (memory):", ctl.handle_message(c1, "Ποιοι ήταν οι δύο αριθμοί που σου έδωσα;").response.content)

c2 = svc.new_conversation("deap_cross_subject", "experiment_planning").id
print("\n[Experiment Planning] new conv (no old context):", ctl.handle_message(c2, "Ποιους αριθμούς F1 σου είπα νωρίτερα; Αν δεν ξέρεις, πες το.").response.content)
