"""
NorthStar AI Knowledge Assistant Entry Point.
"""

from dotenv import load_dotenv

from rag_assistant.chat.assistant import ask_assistant

load_dotenv()


def main() -> None:
    """Launch the NorthStar AI Knowledge Assistant."""

    print("\nNorthStar AI Knowledge Assistant\n")

    question = input("Ask a question: ")

    response = ask_assistant(question)

    print("\nRetrieved Knowledge:\n")
    print(response)


if __name__ == "__main__":
    main()
