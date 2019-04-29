import os
from .vault import VaultClient
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    def __init__(self) -> None:
        vault_token = os.getenv('VAULT_TOKEN')
        vault_secret = os.getenv('VAULT_SECRET')
        if vault_secret and vault_token:
            self.vault_client = VaultClient(token=os.getenv('VAULT_TOKEN'), secret=os.getenv('VAULT_SECRET'))
            self.bot_id = self.vault_client.get_secret('bot.id')
            self.bot_name = self.vault_client.get_secret('bot.name')
            self.bot_token = self.vault_client.get_secret('bot.token')


class Production(Config):
    DEBUG = False


class Staging(Config):
    DEVELOPMENT = True
    DEBUG = True


class Development(Config):
    DEVELOPMENT = True
    DEBUG = True

    def __init__(self) -> None:
        super().__init__()
        self.bot_id = os.getenv('BOT_ID')
        self.bot_name = os.getenv('BOT_NAME')
        self.bot_token = os.getenv('BOT_TOKEN')


class Testing(Config):
    TESTING = True
    DEBUG = True

