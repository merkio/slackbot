import vault_client
from configparser import ConfigParser


class VaultClient:

    def __init__(self, token=None, secret=''):
        self._token = token
        self._secret = secret
        self.client = vault_client.instances.Production(rsa_auth=False, authorization=token)
        self.last_version = self.client.get_secret(secret)

    def get_version_value(self, version):
        data = self.client.get_version(version)
        return data['value']

    def get_last_value(self, secret):
        secret_data = self.client.get_secret(secret)
        version = secret_data['secret_versions'][0]['version']
        return self.get_version_value(version)

    def get_secret(self, key, section='DEFAULT'):
        secret_data = self.client.get_secret(self._secret)
        version = secret_data['secret_versions'][0]['version']
        data = self.client.get_version(version)
        config = ConfigParser()
        config.read_string(data['value']['properties'])
        return config[section][key]
