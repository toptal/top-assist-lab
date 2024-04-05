# ./oai_assistants/openai_assistant.py
from open_ai.assistants.utility import initiate_client
from open_ai.assistants.assistant_manager import AssistantManager
from open_ai.assistants.thread_manager import ThreadManager

from .templates import qa_assistant_template, knowledge_gap_assistant_template


def create_assistant(client, template):
    """
    Creates a new assistant based on the provided template.

    Parameters:
    client: OpenAI client instance used for assistant creation.
    template (dict): Template for the new assistant.

    Returns:
    Assistant: An instance of the created assistant.
    """
    assistant_manager = AssistantManager(client)
    return assistant_manager.create_assistant(
        template['model'],
        template['name'],
        template['instructions'],
        template['tools'],
        template['description']
    )


def chat_with_assistant(thread_manager):
    """
    Facilitates a chat interaction with an assistant using the provided thread manager.

    Parameters:
    thread_manager (ThreadManager): An instance of ThreadManager to handle the chat thread.

    Returns:
    None
    """
    print("Welcome to the Assistant Chat!")
    thread_manager.create_thread()

    while True:  # Main chat loop
        # Message input loop
        user_message = ""
        print("You: \nWrite your message, or write 'QUIT' to abort the chat.")
        while True:
            user_input = input()
            if user_input.lower() == 'quit':
                print("Exiting chat.")
                return  # Exit the entire chat function
            else:
                user_message += user_input + "\n"
                if user_input.lower() == 'done':
                    break

        if user_message.strip():
            thread_manager.add_message_and_wait_for_reply(user_message)
        else:
            print("No message entered.")

        # After processing, continue the main chat loop
        print("\nContinue chatting, or type 'QUIT' to exit.")


def chose_assistant(assistant_manager, assistants):
    """
    Allows the user to select an assistant from a list.

    Parameters:
    assistant_manager (AssistantManager): An instance of AssistantManager for managing assistants.
    assistants (list): A list of available assistants.

    Returns:
    str: The ID of the selected assistant, or None if the operation is canceled.
    """
    print("\nSelect an Assistant")
    print("-------------------")
    for index, assistant in enumerate(assistants, start=1):
        print(f"{index}. {assistant.name} (ID: {assistant.id})")
    print("0. Cancel - Return to the previous menu.")
    print("-------------------")

    assistant_index = input("Enter the number of the assistant you want to manage or '0' to cancel: ")
    if assistant_index == '0':
        print("Operation canceled.")
        return None

    try:
        assistant_index = int(assistant_index) - 1
        if 0 <= assistant_index < len(assistants):
            selected_assistant = assistants[assistant_index]
            assistant_id = selected_assistant.id
            assistant_manager.print_assistant_details(assistant_id)
            return assistant_id
        else:
            print("Invalid assistant number.")
            return None
    except ValueError:
        print("Invalid input. Please enter a number.")
        return None


def chose_assistant_action():
    """
    Presents a menu for the user to choose an action to perform on an assistant.

    Returns:
    str: The selected action as a string.
    """
    print("\nChoose an Action for the Assistant")
    print("------------------------------------")
    print("1. Chat - Chat with this assistant.")
    print("2. Update - Update this assistant's parameters.")
    print("3. Delete - Delete this assistant.")
    print("0. Cancel - Return to the previous menu.")
    print("------------------------------------")
    action = input("Choose an option (0-3): ")
    return action


def manage_assistants(client):
    """
    Provides a management interface for assistants.

    Parameters:
    client: OpenAI client instance used for managing assistants.

    Returns:
    None
    """
    assistant_manager = AssistantManager(client)
    assistants = assistant_manager.list_assistants().data

    if not assistants:
        print("No assistants available.")
        return

    assistant_id = chose_assistant(assistant_manager, assistants)

    if assistant_id is None:
        return

    action = chose_assistant_action()
    if action == '1':
        # Chat with assistant
        thread_manager = ThreadManager(client, assistant_id)
        chat_with_assistant(thread_manager)
    elif action == '2':
        # Update assistant parameters
        # Call the interactive update method from AssistantManager
        assistant_manager.update_assistant_interactively(assistant_id)
        print("Assistant updated successfully.")
    elif action == '3':
        # Delete the assistant
        delete_message = assistant_manager.delete_assistant(assistant_id)
        print(delete_message)
    elif action == '0':
        # exit menu
        print("Operation canceled.")
    else:
        print("Invalid action.")


def user_interaction(client):
    """
    Provides the main user interaction interface for managing assistants.

    Parameters:
    client: OpenAI client instance used for user interactions.

    Returns:
    None
    """
    while True:
        print("\nUser Interaction Menu:")
        print("--------------------------------")
        print("1. Manage Assistants - View, modify, or delete assistants.")
        print("2. Create a New Q&A Assistant - Start the process of creating a new assistant.")
        print("3. Create a New Knowledge Gap Assistant - Start the process of creating a new assistant.")
        print("0. Exit - Exit the user interaction menu.")
        print("--------------------------------")

        choice = input("Enter your choice (0-2): ")
        if choice == '1':
            manage_assistants(client)
        elif choice == '2':
            created_assistant = create_assistant(client, qa_assistant_template)
            print(f"New assistant created with ID: {created_assistant.id}")
        elif choice == '3':
            created_assistant = create_assistant(client, knowledge_gap_assistant_template)
            print(f"New assistant created with ID: {created_assistant.id}")
        elif choice == '0':
            print("Exiting user interaction menu.")
            break
        else:
            print("Invalid choice. Please select a valid option.")


def load_manage_assistants():
    client = initiate_client()
    user_interaction(client)


if __name__ == "__main__":
    load_manage_assistants()
