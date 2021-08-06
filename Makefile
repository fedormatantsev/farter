INTERMEDIATE_PATH:=intermediate
PYTHON:=python3
OPEN_API_PYTHON_CLIENT:=openapi-python-client
SPEC_URL:=https://raw.githubusercontent.com/TinkoffCreditSystems/invest-openapi/master/src/docs/swagger-ui/swagger.yaml

gen-tinkoff-client: tinkoff_investing.yaml
	mkdir -p $(INTERMEDIATE_PATH)
	cd $(INTERMEDIATE_PATH) && $(OPEN_API_PYTHON_CLIENT) generate --path tinkoff_investing.yaml --meta none --config ../scripts/openapi_python_client_config.yaml

tinkoff_investing.yaml:
	mkdir -p $(INTERMEDIATE_PATH)
	curl $(SPEC_URL) --output $(INTERMEDIATE_PATH)/tinkoff_investing.yaml
