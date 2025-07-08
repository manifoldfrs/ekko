# Ekko - Developer Convenience Makefile
# Usage examples:
#   make dev          # full setup: venv -> install -> pre-commit -> neo4j up
#   make format       # run black + isort on codebase
#   make lint         # ruff static checks
#   make test         # pytest suite
#   make stop         # stop docker services
#   make clean        # remove caches and pyc

PYTHON        ?= python3
VENV_DIR      ?= .venv
PIP           := $(VENV_DIR)/bin/pip
ACTIVATE      := . $(VENV_DIR)/bin/activate
DOCKER_COMPOSE := docker compose

# Environment
$(VENV_DIR):
	@echo ">> Creating virtualenv in $(VENV_DIR)"
	$(PYTHON) -m venv $(VENV_DIR)

venv: $(VENV_DIR)

install: venv
	@echo ">> Installing Python dependencies"
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo ">> Downloading SpaCy language model"
	$(VENV_DIR)/bin/python -m spacy download en_core_web_sm

precommit: venv
	@echo ">> Installing & running pre-commit hooks"
	$(VENV_DIR)/bin/pre-commit install

# Neo4j via Docker Compose
neo4j:
	@echo ">> Launching Neo4j (docker-compose)"
	$(DOCKER_COMPOSE) up -d neo4j

stop:
	@echo ">> Stopping docker services"
	$(DOCKER_COMPOSE) down

# Aggregate workflows
dev: install precommit neo4j
	@echo ">> Dev environment ready 🎉"
	@echo "   Neo4j Browser -> http://localhost:7474  (user: neo4j / password: password)"

# Code Quality
format: venv
	@echo ">> Auto-formatting with black and isort"
	$(VENV_DIR)/bin/black .
	$(VENV_DIR)/bin/isort .

lint: venv
	@echo ">> Linting and formatting with black and isort"
	$(VENV_DIR)/bin/black .
	$(VENV_DIR)/bin/isort .

test: venv
	@echo ">> Running pytest"
	PYTHONPATH=. $(VENV_DIR)/bin/pytest

# Utilities
clean:
	@echo ">> Cleaning caches"
	rm -rf **/__pycache__ .pytest_cache .ruff_cache
