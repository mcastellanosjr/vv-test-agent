import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Type, TypeVar

from pydantic import BaseModel, ValidationError

from config import (
    BASE_DIR,
    CURSOR_CLI_COMMAND,
    CURSOR_MODEL,
    CURSOR_TIMEOUT_SECONDS,
)


T = TypeVar("T", bound=BaseModel)


def resolve_cursor_command() -> str:
    """
    Resolve the Cursor CLI command to its installed path.
    """

    resolved = shutil.which(CURSOR_CLI_COMMAND)

    if not resolved:
        raise RuntimeError(
            f"Cursor CLI command '{CURSOR_CLI_COMMAND}' "
            "could not be found on PATH.\n"
            "Verify that 'agent --version' works."
        )

    return resolved


def execute_cursor(prompt: str) -> str:
    """
    Execute a SHORT prompt through Cursor CLI.

    Large prompts are handled separately by run_cursor()
    using a temporary workspace file.
    """

    cursor_command = resolve_cursor_command()

    cursor_args = [
        cursor_command,
        "-p",
        prompt,
        "--output-format",
        "text",
    ]

    if CURSOR_MODEL:
        cursor_args.extend(
            [
                "--model",
                CURSOR_MODEL,
            ]
        )

    if os.name == "nt":
        cursor_command_line = subprocess.list2cmdline(
            cursor_args
        )

        command = [
            "cmd.exe",
            "/d",
            "/s",
            "/c",
            cursor_command_line,
        ]
    else:
        command = cursor_args

    try:
        result = subprocess.run(
            command,
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=CURSOR_TIMEOUT_SECONDS,
            check=False,
        )

    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(
            f"Cursor CLI timed out after "
            f"{CURSOR_TIMEOUT_SECONDS} seconds."
        ) from exc

    except OSError as exc:
        raise RuntimeError(
            "Operating system could not start Cursor CLI.\n"
            f"Error: {exc}"
        ) from exc

    if result.returncode != 0:
        raise RuntimeError(
            "Cursor CLI execution failed.\n\n"
            f"Exit code: {result.returncode}\n\n"
            f"STDOUT:\n{result.stdout}\n\n"
            f"STDERR:\n{result.stderr}"
        )

    response = result.stdout.strip()

    if not response:
        raise RuntimeError(
            "Cursor CLI completed successfully but "
            "returned an empty response."
        )

    return response


def run_cursor(prompt: str) -> str:
    """
    Execute a prompt through Cursor CLI.

    Small prompts are passed directly.

    Large prompts are written to a temporary file inside
    the project workspace. Cursor then receives only a short
    command telling it to read that file.

    This avoids Windows command-line quoting and length issues.
    """

    direct_prompt_limit = 1500

    if len(prompt) <= direct_prompt_limit:
        return execute_cursor(prompt)

    temp_directory = Path(BASE_DIR) / ".cursor_prompts"
    temp_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    temp_file = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            suffix=".txt",
            prefix="vv_prompt_",
            dir=temp_directory,
            delete=False,
        ) as file:
            file.write(prompt)
            temp_file = Path(file.name)

        relative_path = temp_file.relative_to(BASE_DIR)

        short_prompt = (
            f"Read the complete instructions from "
            f"'{relative_path.as_posix()}'. "
            f"Follow those instructions exactly. "
            f"Return only the requested final output."
        )

        return execute_cursor(short_prompt)

    finally:
        if temp_file and temp_file.exists():
            try:
                temp_file.unlink()
            except OSError:
                pass


def extract_json(response: str) -> str:
    """
    Extract JSON from a Cursor response.

    Handles:
    - raw JSON
    - Markdown JSON fences
    - minor text surrounding a JSON object
    """

    response = response.strip()

    if response.startswith("```"):
        lines = response.splitlines()

        if lines:
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        response = "\n".join(lines).strip()

    try:
        json.loads(response)
        return response
    except json.JSONDecodeError:
        pass

    object_start = response.find("{")
    object_end = response.rfind("}")

    if object_start != -1 and object_end != -1:
        candidate = response[
            object_start:object_end + 1
        ]

        try:
            json.loads(candidate)
            return candidate
        except json.JSONDecodeError:
            pass

    raise RuntimeError(
        "Cursor did not return valid JSON.\n\n"
        f"Cursor response:\n{response}"
    )


def run_cursor_structured(
    prompt: str,
    response_model: Type[T],
) -> T:
    """
    Execute Cursor CLI and validate its response
    against a Pydantic model.
    """

    schema = response_model.model_json_schema()

    structured_prompt = f"""
{prompt}

IMPORTANT OUTPUT REQUIREMENTS

Return ONLY one valid JSON object.

Do not return:
- Markdown
- explanations
- commentary
- code fences
- introductory text
- text after the JSON

The JSON must conform to the following schema:

{json.dumps(schema, indent=2)}

Before returning the result:
1. Verify that the output is valid JSON.
2. Verify that all required fields are present.
3. Verify that field types match the schema.
4. Return only the final JSON object.
"""

    response = run_cursor(
        structured_prompt
    )

    json_text = extract_json(
        response
    )

    try:
        return response_model.model_validate_json(
            json_text
        )

    except ValidationError as exc:
        raise RuntimeError(
            "Cursor returned valid JSON, but it does "
            "not conform to the required V&V data model.\n\n"
            f"Cursor response:\n{response}\n\n"
            f"Validation error:\n{exc}"
        ) from exc

    except ValueError as exc:
        raise RuntimeError(
            "Cursor returned content that could not "
            "be validated as JSON.\n\n"
            f"Cursor response:\n{response}"
        ) from exc