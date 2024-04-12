# ./oai_assistants/assistant_manager.py
import json


class AssistantManager:
    """
    AssistantManager provides functionalities to manage the lifecycle of assistants.
    It includes creating, listing, loading, updating, and deleting assistants within the GPT-4-Turbo-Assistant environment.
    """
    def __init__(self, client):
        """
        Initialize the AssistantManager with a client to manage assistants.

        Parameters:
        client (OpenAI_Client): The client object used for assistant operations.
        """
        self.client = client.beta.assistants

    def create_assistant(self, model, name, instructions, tools, description=None, metadata=None):
        """
        Create an assistant without files.

        Args:
            model: ID of the model to use for the assistant.
            name (optional): The name of the assistant.
            instructions (optional): Instructions for the system using the assistant.
            description (optional): A descriptive text for the assistant.
            metadata (optional): Metadata in key-value format for the assistant.
            tools (optional): A list of tools enabled on the assistant.

        Returns:
            The newly created Assistant object.
        """
        response = self.client.create(
            model=model,
            name=name,
            instructions=instructions,
            description=description,
            metadata=metadata,
            tools=tools
        )
        return response

    def list_assistants(self):
        """
        List all assistants.

        Returns:
            A list of Assistant objects containing details about each assistant.
        """
        return self.client.list()

    def load_assistant(self, assistant_id):
        """
        Load an assistant's parameters by ID.

        Args:
            assistant_id: The unique identifier for the assistant.

        Returns:
            An Assistant object or details about the assistant.
        """
        return self.client.retrieve(assistant_id=assistant_id)

    def print_assistant_details(self, assistant_id):
        """
        Retrieve and display the parameters of a specific assistant by ID.

        Args:
            assistant_id: The unique identifier for the assistant.
        """
        assistant = self.load_assistant(assistant_id)
        assistant_details = assistant.model_dump()
        print(assistant_details)

    def update_assistant_interactively(self, assistant_id):
        """
        Interactively update an assistant's parameters.

        Args:
            assistant_id: The unique identifier for the assistant.
        """
        assistant = self.load_assistant(assistant_id)
        # Retrieve the assistant's existing parameters.
        updatable_params = {
            'name': assistant.name,
            'model': assistant.model,
            'instructions': assistant.instructions,
            'description': assistant.description,
            'metadata': assistant.metadata,
            'tools': assistant.tools
        }

        # Interactive update process
        for param_name, current_value in updatable_params.items():
            print(f'Current value of {param_name}: {current_value}')
            user_input = input(f'Press Enter to keep the current value or enter a new value for {param_name}: ').strip()
            # If the user enters a new value, update the parameter
            if user_input:
                if param_name in ['metadata', 'tools']:
                    # Convert the string input to a Python dictionary using json.loads()
                    try:
                        updatable_params[param_name] = json.loads(user_input)
                    except json.JSONDecodeError as e:
                        print(f'Error: Invalid JSON for {param_name}. Using the current value instead.')
                else:
                    updatable_params[param_name] = user_input

        # After all parameters are reviewed, update the assistant details
        update_response = self.client.update(assistant_id=assistant_id, **updatable_params)
        return update_response

    def delete_assistant(self, assistant_id):
        """
        Delete an assistant by ID.

        Args:
            assistant_id: The unique identifier for the assistant.

        Returns:
            A confirmation message indicating that the assistant was deleted.
        """
        response = self.client.delete(assistant_id=assistant_id)
        return "Assistant deleted successfully."
