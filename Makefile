# Makefile

.DEFAULT_GOAL := help

.PHONY: help
help: ## this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'


export VIRTUAL_ENV := $(abspath ${VENV})
export PATH := ${VIRTUAL_ENV}/bin:${PATH}


.PHONY: clean
clean: # remove *.pyc files
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -type d | xargs rm -fr
	rm -r .mypy_cache 2>/dev/null || true
	rm -r .pytest_cache 2>/dev/null || true
	rm -r htmlcov 2>/dev/null || true
	rm -r .coverage 2>/dev/null || true

.PHONY: install-uv
install-uv:
	curl -LsSf https://astral.sh/uv/install.sh | sh

.PHONY: lock-upgrade
lock-upgrade:
	uv lock --upgrade

.PHONY: install
install: ## install dependencies
	@which uv > /dev/null 2>&1 || (echo "UV not found, installing..." && $(MAKE) install-uv)
	@if [ ! -d @VIRTUAL_ENV ]; then \
		uv venv --python 3.12.6; \
	fi
	uv pip install --extra=dev -r pyproject.toml

.PHONY: migrate
migrate: ## run alembic migrations
	cd app; alembic upgrade head

.PHONY: run
run: ## start server
	uv run app/main.py


.PHONY: format
format: ## format project files
	chmod +x ./lint.sh
# 	./lint.sh black
# 	./lint.sh ruff check --fix
# 	./lint.sh ruff check --select I --fix
# 	./lint.sh ruff format
	black .
	ruff check --fix
	ruff check --select I --fix
	ruff format

.PHONY: lint
lint: ## lint project files
	chmod +x ./lint.sh
	./lint.sh ruff check --diff
	./lint.sh ruff check --diff --select I
	./lint.sh ruff format --check --diff

.PHONY: test
test: ## run tests
	ENV_FOR_DYNACONF=test PYTHONPATH=$(shell pwd)/app ROOT_PATH_FOR_DYNACONF=$(shell pwd)/app pytest app


.PHONY: build-docker
build-docker: ## build docker container for partner
	docker-compose build

.PHONY: run-docker
run-docker: ## run partner with docker-compose
	docker-compose run web


.PHONY: build-and-run-docker
build-and-run-docker: build-docker run-docker ## build and run docker container

