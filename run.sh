#!/usr/bin/env bash
set -euo pipefail

DEFAULT_KEY='dev-fallback-key'

# --------------------------------
# Function to generate strong key
# --------------------------------
generate_secret_key() {
    python3 - <<'EOF'
import secrets
print(secrets.token_urlsafe(64))
EOF
}

# --------------------------------
# Function to replace default keys
# --------------------------------
replace_default_key() {
    VAR_NAME=$1

    CURRENT_KEY=$(grep "^$VAR_NAME=" "$ENV_FILE" | cut -d '=' -f2- || true)
    
    if [[ -z "$CURRENT_KEY" || "$CURRENT_KEY" == "$DEFAULT_KEY" ]]; then
        echo "Generating secure $VAR_NAME for production..."

        NEW_KEY=$(generate_secret_key)

        # Replace or append safely
        if grep -q "^$VAR_NAME=" "$ENV_FILE"; then
            sed -i "s|^$VAR_NAME=.*|$VAR_NAME=$NEW_KEY|" "$ENV_FILE"
        else
            echo "$VAR_NAME=$NEW_KEY" >> "$ENV_FILE"
        fi

        echo "$VAR_NAME written to $ENV_FILE"
        echo "⚠️  IMPORTANT: Back this up securely!"
    fi
}

ENVIRONMENT="${1:-}"
COMMAND="${2:-up}"

if [[ "$ENVIRONMENT" != "development" && "$ENVIRONMENT" != "production" ]]; then
    echo "Usage: $0 <development|production> [up|down|restart|logs]"
    exit 1
fi

ENV_FILE=".env.${ENVIRONMENT}"

COMPOSE_ARGS=()

case "$COMMAND" in
    up)
        COMPOSE_ARGS+=(up --build)
        [[ "$ENVIRONMENT" == "production" ]] && COMPOSE_ARGS+=(-d)
        ;;
    down)
        COMPOSE_ARGS+=(down)
        ;;
    restart)
        COMPOSE_ARGS+=(down)
        docker compose --env-file "$ENV_FILE" "${COMPOSE_ARGS[@]}"
        COMPOSE_ARGS=(up --build)
        [[ "$ENVIRONMENT" == "production" ]] && COMPOSE_ARGS+=(-d)
        ;;
    logs)
        COMPOSE_ARGS+=(logs -f)
        ;;
    *)
        echo "Unknown command: $COMMAND"
        exit 1
        ;;
esac

# --------------------------------
# Create env file if missing
# --------------------------------
if [[ ! -f "$ENV_FILE" ]]; then
    if [[ ! -f ".env.example" ]]; then
        echo "ERROR: .env.example not found"
        exit 1
    fi

    echo "Creating $ENV_FILE from .env.example"
    cp .env.example "$ENV_FILE"

    # --------------------------------
    # Environment-specific overrides
    # --------------------------------
    if [[ "$ENVIRONMENT" == "development" ]]; then
        sed -i \
        -e 's/^ENV=.*/ENV=development/' \
        -e 's/^LOG_LEVEL=.*/LOG_LEVEL=DEBUG/' \
        -e 's/^POSTGRES_DB=.*/POSTGRES_DB=opentenant_dev/' \
        -e 's/^SECRET_KEY=.*/SECRET_KEY=dev-secret-key/' \
        "$ENV_FILE"

    else
        sed -i \
        -e 's/^ENV=.*/ENV=production/' \
        -e 's/^LOG_LEVEL=.*/LOG_LEVEL=INFO/' \
        -e 's/^POSTGRES_DB=.*/POSTGRES_DB=opentenant/' \
        "$ENV_FILE"

        # Replace the default keys (if they haven't been already)
        replace_default_key SECRET_KEY
        replace_default_key POSTGRES_PASSWORD
    fi
fi

# --------------------------------
# Only apply docker override if not production
# --------------------------------
if [[ "$ENVIRONMENT" == "production" ]]; then
    export COMPOSE_FILE="docker-compose.yml"
else
    export COMPOSE_FILE="docker-compose.yml:docker-compose.override.yml"
fi

docker compose --env-file "$ENV_FILE" "${COMPOSE_ARGS[@]}"
