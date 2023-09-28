# Jukebox Makefile

VENV = .venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip

MAKEFLAGS += --no-print-directory

.PHONY: all $(MAKECMDGOALS)
# .DEFAULT_GOAL := help

.logo:
	@echo
	@echo "		     _       _        _                		"
	@echo "		    | |_   _| | _____| |__   _____  __ 		"
	@echo "		 _  | | | | | |/ / _ \ '_ \ / _ \ \/ / 		"
	@echo "		| |_| | |_| |   <  __/ |_) | (_) >  <  		"
	@echo "		 \___/ \__,_|_|\_\___|_.__/ \___/_/\_\ 		"

# Development mode
serve:				.logo .update-deps .start-dev-server
client:				.logo

# Production mode
install:			.logo .install-deps
start-web:			.logo .start-prod-server

# Client Setup
build-client:		.logo
deploy-client:		.logo .start-client


# Private targets

.update-deps:
	@echo
	@echo "🏗  Upgrading your environment"
	@poetry update --lock
	@poetry install --sync
	@poetry run pre-commit autoupdate
	@poetry run pre-commit install
	@poetry run pre-commit install --hook-type pre-push

.install-deps:
	@echo
	@echo "🏗  Setting up your environment"
	@poetry install --sync

.start-dev-server:
	@echo
	@echo "🚀 Starting development server"
	@${PYTHON} -c "from jukebox.server import dev_server_entrypoint as entrypoint; entrypoint()"

.start-prod-server:
	@echo
	@echo "🚀 Starting production server"
	@${PYTHON} -c "from jukebox.server import prod_server_entrypoint as entrypoint; entrypoint()"

.start-client:
	@echo
	@echo "📱 Running client application"
	@flutter run
