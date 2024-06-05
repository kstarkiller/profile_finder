
import os
from pprint import pprint
from openai import AzureOpenAI
      
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
    api_version="2024-02-01",
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    )

deployment = "aiprofilesmatching-gpt4"

prompt = "start"
ending_chat = ["exit", "quit", "stop", "end", "close", "finish", "bye", "goodbye"]

messages = []

while True:
    prompt = input("Enter your question: ")

    messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

    completion = client.chat.completions.create(
        model=deployment,
        messages=messages,
        max_tokens=100,
        stop=None,
    )

    response = completion.choices[0].message.content


    if prompt.lower() in ending_chat:
        print(response + "\n")
        break

    print(response + "\n")

    messages.append(
        {
            "role": "assistant",
            "content": response,
        }
    )