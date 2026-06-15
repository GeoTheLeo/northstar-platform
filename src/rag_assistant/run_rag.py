import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]

sys.path.append(
    str(project_root / "src")
)

from rag_assistant.chat.assistant import (
    ask_assistant,
)

print(
    "\nNorthStar AI Knowledge Assistant\n"
)

question = input(
    "Ask a question: "
)

response = ask_assistant(
    question
)

print(
    "\nRetrieved Knowledge:\n"
)

print(response)