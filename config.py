import os
from pathlib import Path


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"
PROMPTS_DIR = BASE_DIR / "prompts"


# ---------------------------------------------------------
# Cursor CLI configuration
# ---------------------------------------------------------

# Cursor CLI executable.
# On Windows this will normally resolve to "agent"
# after the Cursor CLI has been installed and added to PATH.
CURSOR_CLI_COMMAND = os.getenv(
    "CURSOR_CLI_COMMAND",
    "agent",
)

# Optional Cursor model.
#
# Leave this empty to allow Cursor CLI to use its configured/default
# model. We can specify a particular Cursor-supported model later.
CURSOR_MODEL = os.getenv(
    "CURSOR_MODEL",
    "",
)


# ---------------------------------------------------------
# Cursor CLI execution settings
# ---------------------------------------------------------

# Maximum amount of time, in seconds, that Python will wait
# for a Cursor CLI request to finish.
CURSOR_TIMEOUT_SECONDS = int(
    os.getenv(
        "CURSOR_TIMEOUT_SECONDS",
        "180",
    )
)


# ---------------------------------------------------------
# Application configuration
# ---------------------------------------------------------

APPLICATION_NAME = "V&V Test Design Agent"
APPLICATION_VERSION = "1.0.0"


# ---------------------------------------------------------
# Ensure required directories exist
# ---------------------------------------------------------

INPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

PROMPTS_DIR.mkdir(
    parents=True,
    exist_ok=True,
)