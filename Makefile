# Jukebox Makefile

VENV = .venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip

MAKEFLAGS += --no-print-directory

.PHONY: all $(MAKECMDGOALS)
.DEFAULT_GOAL := help

logo:		## Prints the Jukebox logo
	@echo
	@echo "		     _       _        _                		"
	@echo "		    | |_   _| | _____| |__   _____  __ 		"
	@echo "		 _  | | | | | |/ / _ \ '_ \ / _ \ \/ / 		"
	@echo "		| |_| | |_| |   <  __/ |_) | (_) >  <  		"
	@echo "		 \___/ \__,_|_|\_\___|_.__/ \___/_/\_\ 		"

help:
	@$(MAKE) logo
	@echo
	@echo "🦊 Usage: make [command] ..."
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

configure:	## Configures the poetry environment and the pre-commit hooks
	@echo
	@echo "🛠️ Configuring your environment"
	@poetry install --sync
	@poetry run pre-commit install
	@poetry run pre-commit install --hook-type pre-push

upgrade:	## Upgrades the poetry environment and the pre-commit hooks
	@echo
	@echo "🏗 Upgrading your environment"
	@poetry update --lock
	@poetry run pre-commit autoupdate
	@$(MAKE) configure

serve:		## Start a server for development purposes
	@$(MAKE) logo
	@$(MAKE) upgrade

	@echo
	@echo "🚀 Starting development server"
	@${PYTHON} -c "from jukebox.server import entrypoint; entrypoint()"
