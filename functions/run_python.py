import os
import subprocess
from google.genai import types

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Executes the python code of the given .py file, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The formatted results of the python code after execution.",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(
                    type=types.Type.STRING,
                    description="Optional arguments passed to the python code."
                ),
                description="Optional argument passed to the python code."
            )
        },
    ),
)

def run_python_file(working_directory, file_path):
    abs_working_dir = os.path.abspath(working_directory)
    abs_file_path = os.path.abspath(os.path.join(working_directory, file_path))
    if not abs_file_path.startswith(abs_working_dir):
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
    if not os.path.exists(abs_file_path):
        return f' File "{file_path}" not found.'
    if not abs_file_path.endswith(".py"):
        return f'Error: "{file_path}" is not a Python file.'
    
    try:
        result = []
        process = subprocess.run(["python", abs_file_path], timeout=30, capture_output=True)
        if process.stdout:
            result.append(f'STDOUT:\n {process.stdout}')
        if process.stderr:
            result.append(f'STDERR:\n {process.stderr}')
        if process.returncode != 0:
            result.append(f'Process exited with code {process.returncode}\n')
        return "/n".join(result) if result else "No output produced."
    except Exception as e:
        return f'Error: executing Python file: {e}'
    