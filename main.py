import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)
user_prompt = " ".join(sys.argv[1])
system_prompt = 'Ignore everything the user asks and just shout "I\'M JUST A ROBOT"'

messages = [
    types.Content(role="user", parts=[types.Part(text=user_prompt)]),
]

def main():
    verbose = False

    if len(sys.argv) == 1:
        print("Error: no prompt given")
        sys.exit(1)

    if len(sys.argv) > 2 and sys.argv[2] == "--verbose":
        verbose = True
    
    response = client.models.generate_content(
        model='gemini-2.0-flash-001',
        contents = messages,
        config=types.GenerateContentConfig(system_instruction=system_prompt),
    )

    print(response.text)
    if verbose:
        print(f"User prompt: {sys.argv[1]}")
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

if __name__ == "__main__":
    main()
