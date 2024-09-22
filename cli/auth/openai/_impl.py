import os
from twitter.account import Account
import click
import typing as T
import json
from openai import OpenAI

from constants import TMP_OPENAI_TOKEN


def get_active_account() -> T.Optional[Account]:
    try:
        with open(TMP_OPENAI_TOKEN, "r") as token:
            code = json.load(token)
            return OpenAI(api_key=code["token"])
    except FileNotFoundError:
        click.echo("No active account found.")
        return None
    except Exception:
        click.echo("Failed to authenticate.")
        return None


def set_active_account() -> bool:
    click.echo("Setting active openai account...")
    api_key = click.prompt("Enter your OpenAI API Key")
    try:
        _set_active_account(api_key)
    except Exception as e:
        click.echo(click.style(str(e), fg="red"))
        click.echo(
            click.style(f"Failed to authenticate openai account {api_key}.", fg="red"),
            err=True,
        )
        return False
    click.echo("Active openai account successfully set.")
    return True


def remove_active_account() -> None:
    click.echo("Removing active openai account...")
    try:
        os.remove(TMP_OPENAI_TOKEN)
        click.echo("Active openai account successfully removed.")
    except FileNotFoundError:
        click.echo("No active openai account found.")


def _set_active_account(api_key: str) -> None:
    client = OpenAI(api_key=api_key)
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": "Tell a good joke in the form of a question. Do not yet give the answer.",
            }
        ],
    )
    click.echo(completion)
    os.makedirs(os.path.dirname(TMP_OPENAI_TOKEN), exist_ok=True)
    with open(TMP_OPENAI_TOKEN, "w") as file:
        file.write(json.dumps(dict({"token": api_key})))
