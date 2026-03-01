"""Interactive prompts for CLI."""

import click
from rich.prompt import Prompt, Confirm
from typing import Optional, List


def confirm_action(message: str, default: bool = False) -> bool:
    """Prompt user for confirmation.

    Args:
        message: Confirmation message
        default: Default value if user just presses Enter

    Returns:
        True if confirmed, False otherwise
    """
    return click.confirm(message, default=default)


def prompt_text(
    message: str,
    default: Optional[str] = None,
    required: bool = True
) -> Optional[str]:
    """Prompt user for text input.

    Args:
        message: Prompt message
        default: Default value
        required: Whether input is required

    Returns:
        User input or None
    """
    if required:
        return Prompt.ask(message, default=default)
    else:
        return Prompt.ask(message, default=default or "")


def prompt_choice(
    message: str,
    choices: List[str],
    default: Optional[str] = None
) -> str:
    """Prompt user to choose from a list.

    Args:
        message: Prompt message
        choices: List of valid choices
        default: Default choice

    Returns:
        Selected choice
    """
    return Prompt.ask(
        message,
        choices=choices,
        default=default
    )


def prompt_password(message: str = "Password") -> str:
    """Prompt user for password (hidden input).

    Args:
        message: Prompt message

    Returns:
        Password input
    """
    return Prompt.ask(message, password=True)
