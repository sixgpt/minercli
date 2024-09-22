import click

import cli.auth.openai as openai_auth 


def register(auth: click.Group):
    @auth.group()
    def openai():
        """Manage OpenAI Authentication"""
        pass

    @openai.command()
    def login():
        """Set OpenAI API Key"""
        openai_auth.set_active_account()

    @openai.command()
    def logout():
        """Reset OpenAI API Key"""
        openai_auth.remove_active_account()
