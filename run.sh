#!/bin/bash

set -e

if [[ ! -e .env ]]; then
    echo "No .env file found! Copying from .env.example..."
    cp .env.example .env
fi

export PYTHONPATH=src

exec uv run gunicorn -c docker/app/gunicorn_conf.py wsgi:app
