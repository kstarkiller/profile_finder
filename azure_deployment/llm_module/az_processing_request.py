import os
from openai import AzureOpenAI
from llm_module.az_search import find_profiles_azure

LLM_gpt4 = "aiprofilesmatching-gpt-4-turbo"
# LLM_gpt4 = "gpt-4-turbo-1106-preview"
EMBEDDER = "aiprofilesmatching-text-embedding-3-large"

# Initialize the AzureOpenAI client
client = AzureOpenAI(
    api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-01",
    azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),  # type: ignore
)


def process_input(user_input: list, chat_history: list) -> tuple:
    """
    Process the user input and return the chatbot response.

    :param user_input: list of dict containing the user input and context (if any) as a string (e.g. [{"query": "Hello, how are you?", "context": ""}])
    :param chat_history: list of dict containing the chat history (user and assistant messages) as strings
    :return: str, list of dict
    """
    # Validate the user input
    if not user_input[-1]["query"].strip():
        return "Please enter a valid input.", chat_history

    # Check that chat_history contains only the initial context (system)
    # This is therefore the user's first request
    if len(chat_history) <= 1:
        # Check that the context is not empty or null
        if user_input[-1]["context"] != "":
            # Preprocess the user input
            profiles = find_profiles_azure(user_input, EMBEDDER)

            # Check if the list of profiles is not empty
            if len(profiles) != 0:
                # Convert profiles to string
                profiles = [str(profile) for profile in profiles]

                chat_history.append(
                    {
                        "role": "system",
                        "content": "Use the following profiles in this conversation: "
                        + ", ".join(profiles),
                    }
                )
            else:
                raise ValueError("No profiles found for the given input.")

    prompt = user_input[-1]["query"]

    # Add the new user input to the history
    chat_history.append({"role": "user", "content": prompt})

    # Create a chat completion request using the Azure OpenAI client
    try:
        completion = client.chat.completions.create(
            model=LLM_gpt4, messages=chat_history
        )

        # Retrieve the model's response
        if hasattr(completion, "choices") and len(completion.choices) > 0:
            first_choice = completion.choices[0]
            if hasattr(first_choice, "message") and hasattr(
                first_choice.message, "content"
            ):
                response = first_choice.message.content
                # Add the chatbot's response to the history
                chat_history.append({"role": "assistant", "content": response})

                return response, chat_history
            else:
                raise AttributeError("First choice message has no 'content' attribute")
        else:
            raise AttributeError(
                "'choices' attribute missing or empty in completion object"
            )

    except Exception as e:
        print(f"An error occurred: {e}")
        return "An error occurred while processing the input.", chat_history
