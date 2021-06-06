import yaml
import os


def _get_token(env_name: str) -> str:
    script_path = os.path.abspath(os.path.dirname(__file__))
    auth_token_path = os.path.join(script_path, '..', '..', 'data', 'auth_token.yaml')
    with open(auth_token_path, 'r') as auth_token_file:
        auth_token = yaml.load(auth_token_file, Loader=yaml.CFullLoader)
        return auth_token[env_name]


def get_sandbox_token() -> str:
    return _get_token('sandbox')


def get_production_token() -> str:
    return _get_token('sandbox')
