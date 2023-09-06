#!/usr/bin/env bash

poetry run isort --profile black src
poetry run black --line-length 120 --skip-magic-trailing-comma src
poetry run mypy src
poetry run bandit --recursive src
