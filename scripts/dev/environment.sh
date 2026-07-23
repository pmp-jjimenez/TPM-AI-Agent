#!/usr/bin/env bash

TPM_DEV_NODE_COMMAND="${TPM_DEV_NODE_COMMAND:-node}"
TPM_DEV_NPM_COMMAND="${TPM_DEV_NPM_COMMAND:-npm}"
TPM_DEV_LSOF_COMMAND="${TPM_DEV_LSOF_COMMAND:-lsof}"
TPM_DEV_PS_COMMAND="${TPM_DEV_PS_COMMAND:-ps}"

require_python() {
    if [ ! -x "$TPM_DEV_ROOT/.venv/bin/python" ]; then
        error "The Python virtual environment was not found at .venv/bin/python."
        printf 'Create or restore the project virtual environment before continuing.\n' >&2
        return 1
    fi
    return 0
}

require_node() {
    if ! command_available "$TPM_DEV_NODE_COMMAND"; then
        error "Node.js was not found. Install or configure Node.js before starting the frontend."
        return 1
    fi
    return 0
}

require_npm() {
    if ! command_available "$TPM_DEV_NPM_COMMAND"; then
        error "npm was not found. Install or configure npm before starting the frontend."
        return 1
    fi
    return 0
}

require_lsof() {
    if ! command_available "$TPM_DEV_LSOF_COMMAND"; then
        error "The lsof utility was not found. It is required to verify local service ports safely."
        printf 'Install or restore the standard macOS lsof utility before continuing.\n' >&2
        return 1
    fi
    return 0
}

validate_frontend_environment() {
    env_file="$TPM_DEV_ROOT/frontend/.env.local"
    if [ ! -f "$env_file" ]; then
        error "frontend/.env.local was not found."
        printf 'Create it locally with: VITE_API_BASE_URL=%s\n' "$TPM_DEV_BACKEND_URL" >&2
        return 1
    fi

    configured_value="$(
        sed -n 's/^[[:space:]]*VITE_API_BASE_URL[[:space:]]*=[[:space:]]*//p' "$env_file" |
            tail -n 1
    )"
    configured_value="$(printf '%s' "$configured_value" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
    case "$configured_value" in
        \"*\")
            configured_value="${configured_value#\"}"
            configured_value="${configured_value%\"}"
            ;;
        \'*\')
            configured_value="${configured_value#\'}"
            configured_value="${configured_value%\'}"
            ;;
    esac

    if [ -z "$configured_value" ]; then
        error "VITE_API_BASE_URL is not configured in frontend/.env.local."
        printf 'Add: VITE_API_BASE_URL=%s\n' "$TPM_DEV_BACKEND_URL" >&2
        return 1
    fi

    if "$TPM_DEV_ROOT/.venv/bin/python" - "$configured_value" <<'PY'
import sys
from urllib.parse import urlsplit

value = sys.argv[1]
if any(character.isspace() for character in value):
    raise SystemExit(1)

try:
    parsed = urlsplit(value)
    hostname = parsed.hostname
    parsed.port  # Validate malformed and out-of-range ports.
except ValueError:
    raise SystemExit(1)

valid = (
    parsed.scheme in {"http", "https"}
    and bool(parsed.netloc)
    and bool(hostname)
    and parsed.username is None
    and parsed.password is None
    and not parsed.query
    and not parsed.fragment
)
raise SystemExit(0 if valid else 1)
PY
    then
        return 0
    fi

    error "VITE_API_BASE_URL must be a valid absolute HTTP or HTTPS URL."
    printf 'Set it to %s for local development.\n' "$TPM_DEV_BACKEND_URL" >&2
    return 1
}

validate_start_prerequisites() {
    validate_repository || return 1
    require_python || return 1
    require_node || return 1
    require_npm || return 1
    require_lsof || return 1
    if [ ! -f "$TPM_DEV_ROOT/frontend/package.json" ]; then
        error "frontend/package.json was not found. Restore frontend dependencies and project files."
        return 1
    fi
    validate_frontend_environment || return 1
    return 0
}

print_environment_summary() {
    printf 'Environment\n'
    if [ -x "$TPM_DEV_ROOT/.venv/bin/python" ]; then
        printf -- '- Python virtual environment: available\n'
    else
        printf -- '- Python virtual environment: missing\n'
    fi
    if command_available "$TPM_DEV_NODE_COMMAND"; then
        printf -- '- Node: available\n'
    else
        printf -- '- Node: missing\n'
    fi
    if command_available "$TPM_DEV_NPM_COMMAND"; then
        printf -- '- npm: available\n'
    else
        printf -- '- npm: missing\n'
    fi
    printf -- '- Backend: %s\n' "$(service_state_word backend 8000 "$TPM_DEV_BACKEND_PID_FILE")"
    printf -- '- Frontend: %s\n' "$(service_state_word frontend 5173 "$TPM_DEV_FRONTEND_PID_FILE")"
    printf -- '- Git: %s (%s)\n' "$(git_branch_name)" "$(working_tree_description)"
}
