#!/bin/bash

if [[ ! -e .env ]]; then
    echo "No .env file found! Copying from .env.example..."
    cp .env.example .env
fi

uv run flask --app src/OpenTenant_app run