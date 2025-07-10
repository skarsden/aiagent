import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from call_function import available_functions, call_function

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)
user_prompt = " ".join(sys.argv[1])
system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""

config=types.GenerateContentConfig(
    tools=[available_functions], system_instruction=system_prompt
)

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
    
    try:
        for i in range(20):
            response = client.models.generate_content(
                model='gemini-2.0-flash-001',
                contents = messages,
                config=types.GenerateContentConfig(tools=[available_functions], system_instruction=system_prompt),
            )
            if response.text:
                print(response.text)
                break
            
            if response.candidates:
                for c in response.candidates:
                    function_call_content = c.content
                    messages.append(function_call_content)

            if verbose:
                print(f"User prompt: {sys.argv[1]}")
                print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
                print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

            function_responses = []
            for function_call_part in response.function_calls:
                function_call_result = call_function(function_call_part, verbose)
                if(not function_call_result.parts or not function_call_result.parts[0].function_response):
                    raise Exception("empty function call result")
                if verbose:
                    print(f"-> {function_call_result.parts[0].function_response.response}")
                function_responses.append(function_call_result.parts[0])
                responses_messages = types.Content(role="tool", parts=function_responses)
                messages.append(responses_messages)

            if not function_responses:
                raise Exception("no function response generated, exiting.")
    except Exception as e:
        return f'Error: {e}'

if __name__ == "__main__":
    main()
