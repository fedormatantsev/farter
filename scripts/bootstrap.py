import shutil
import subprocess
import requests
import os
import sys

URL = 'https://tinkoffcreditsystems.github.io/invest-openapi/swagger-ui/swagger.yaml'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))
GENERATED_PATH = os.path.join(SCRIPT_PATH, 'generated')
API_FILE_NAME = 'tinkoff_api.yaml'
API_FILE_PATH = os.path.join(GENERATED_PATH, API_FILE_NAME)
TINKOFF_CLIENT_PATH = os.path.join(GENERATED_PATH, 'tinkoff_client')


def check_python_executable():
    executable_path = os.path.abspath(os.path.dirname(sys.executable))
    expected_path = os.path.join(SCRIPT_PATH, '..', 'venv', 'bin')

    if os.path.normpath(executable_path) != os.path.normpath(expected_path):
        print('Bootstrap script should be invoked using venv python executable.')
        print('Run\n\n python3 -m venv ./venv\n\n')
        exit(-1)


def clean_generated():
    shutil.rmtree(path=GENERATED_PATH, ignore_errors=True)


def load_tinkoff_api_spec():
    os.mkdir(GENERATED_PATH)
    r = requests.get(URL, allow_redirects=True)
    open(API_FILE_PATH, 'wb').write(r.content)


def gen_tinkoff_client():
    os.mkdir(TINKOFF_CLIENT_PATH)
    subprocess.call(
        f'swagger-codegen generate -l python '
        f'-i {API_FILE_PATH} -o {TINKOFF_CLIENT_PATH} '
        f'-DpackageName=tinkoff_client'.split(), stdout=None)


def install_tinkoff_client():
    prev_cwd = os.getcwd()
    os.chdir(TINKOFF_CLIENT_PATH)

    setup_py = os.path.join(TINKOFF_CLIENT_PATH, 'setup.py')
    subprocess.call(f'python {setup_py} install'.split())

    os.chdir(prev_cwd)


def main():
    check_python_executable()
    clean_generated()
    load_tinkoff_api_spec()
    gen_tinkoff_client()
    install_tinkoff_client()


if __name__ == '__main__':
    main()
