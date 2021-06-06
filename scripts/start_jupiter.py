import os
import subprocess
import sys

PROJECT_ROOT = os.path.normpath(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
ML_PATH = os.path.join(PROJECT_ROOT, 'ml')
ML_SRC_PATH = os.path.join(ML_PATH, 'src')


def check_python_executable():
    executable_path = os.path.abspath(os.path.dirname(sys.executable))
    expected_path = os.path.join(PROJECT_ROOT, 'venv', 'bin')

    if os.path.normpath(executable_path) != os.path.normpath(expected_path):
        print('Bootstrap script should be invoked using venv python executable.')
        print('Run\n\n python3 -m venv ./venv\n\n')
        exit(-1)


def main():
    check_python_executable()
    python_path = os.getenv('PYTHONPATH')
    os.putenv('PYTHONPATH', python_path + f':{ML_SRC_PATH}')
    os.chdir(ML_PATH)
    subprocess.call('jupyter notebook'.split())


if __name__ == '__main__':
    main()
