# ./main.py
from confluence.importer import tui_choose_space, import_space
from interactions.identify_knowledge_gap import identify_knowledge_gaps
from interactions.vectorize_and_store import vectorize_interactions_and_store_in_db
from open_ai.assistants.openai_assistant import load_manage_assistants
from open_ai.assistants.query_assistant_from_documents import query_assistant_with_context
from vector.chroma import retrieve_relevant_documents
from vector.create_interaction_db import VectorInteractionManager
from visualize.pages import load_confluence_pages_spacial_distribution


def answer_question_with_assistant(question):
    relevant_document_ids = retrieve_relevant_documents(question)
    response, thread_id = query_assistant_with_context(question, relevant_document_ids)
    return response, thread_id


def ask_question():
    print("\nEnter your question (type 'done' on a new line to submit, 'quit' to cancel):")
    lines = []
    while True:
        line = input()
        if line.lower() == "done":
            return "\n".join(lines)
        elif line.lower() == "quit":
            return None
        else:
            lines.append(line)


def main_menu():
    while True:
        print("\nMain Menu:")
        print("1. Load New Documentation Space")
        print("2. Ask a Question to GPT-4T Assistant")
        print("3. Create a vector db for interactions")
        print("4. Manage assistants")
        print("5. Identify knowledge gaps")
        print("6. Visualize Confluence Pages Spacial Distribution")
        print("0. Cancel/Quit")
        choice = input("Enter your choice (0-6): ")

        if choice == "1":
            print("Loading new documentation space...")
            space_key, space_name = tui_choose_space()
            if space_key and space_name:
                import_space(space_key, space_name)
            print()
            print(f"Space '{space_name}' retrieval and indexing complete.")

        elif choice == "2":
            question = ask_question()
            if question:
                answer, thread_id = answer_question_with_assistant(question)
                print(f"\nThread ID: {thread_id}\nAnswer: {answer}")

        elif choice == "3":
            print("Creating vector db for interactions")
            vectorize_interactions_and_store_in_db()
            VectorInteractionManager().add_to_vector()

        elif choice == "4":
            load_manage_assistants()

        elif choice == "5":
            context = input("Enter the context you want to identifying knowledge gaps in\nex:(billing reminders): ")
            identify_knowledge_gaps(context)

        elif choice == "6":
            print("Starting 3D visualization process...")
            load_confluence_pages_spacial_distribution()

        elif choice == "0":
            print("Exiting program.")
            break
        else:
            print("Invalid choice. Please enter 0, 1, 2, 3, 4, 5, or 6.")


if __name__ == "__main__":
    main_menu()
