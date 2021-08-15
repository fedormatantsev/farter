INTERMEDIATE_PATH:=intermediate
VENV_PATH:=.venv

PYTHON:=python3
PIP:=pip3

SPEC_URL:=https://raw.githubusercontent.com/TinkoffCreditSystems/invest-openapi/master/src/docs/swagger-ui/swagger.yaml


venv:
	(\
		test -d $(VENV_PATH) || (\
			$(PYTHON) -m venv $(VENV_PATH);\
			source $(VENV_PATH)/bin/activate;\
			pip3 install openapi-python-client;\
		);\
	)


tinkoff_investing.yaml:
	mkdir -p $(INTERMEDIATE_PATH)
	curl $(SPEC_URL) --output $(INTERMEDIATE_PATH)/tinkoff_investing.yaml


gen-tinkoff-client: venv tinkoff_investing.yaml
	(\
		source $(VENV_PATH)/bin/activate;\
		cd $(INTERMEDIATE_PATH);\
		openapi-python-client generate --path tinkoff_investing.yaml --meta none --config ../scripts/openapi_python_client_config.yaml;\
	)
