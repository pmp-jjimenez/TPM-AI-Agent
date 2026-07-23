#!/usr/bin/env bash

TPM_DEV_RUNTIME_DIR="${TPM_DEV_RUNTIME_DIR_OVERRIDE:-$TPM_DEV_ROOT/.tpm-dev}"
TPM_DEV_BACKEND_URL="http://127.0.0.1:8000"
TPM_DEV_FRONTEND_URL="http://localhost:5173"
TPM_DEV_BACKEND_LOG="$TPM_DEV_RUNTIME_DIR/backend.log"
TPM_DEV_FRONTEND_LOG="$TPM_DEV_RUNTIME_DIR/frontend.log"
TPM_DEV_BACKEND_PID_FILE="$TPM_DEV_RUNTIME_DIR/backend.pid"
TPM_DEV_FRONTEND_PID_FILE="$TPM_DEV_RUNTIME_DIR/frontend.pid"

info() {
    printf '%s\n' "$*"
}

success() {
    printf 'OK: %s\n' "$*"
}

warning() {
    printf 'Warning: %s\n' "$*" >&2
}

error() {
    printf 'Error: %s\n' "$*" >&2
}

print_menu_header() {
    cat <<'EOF'
========================================
 TPM Operating System
 Developer Console
========================================
EOF
}

validate_repository() {
    missing=""
    for path in app/main.py backend/api/main.py frontend/package.json; do
        if [ ! -f "$TPM_DEV_ROOT/$path" ]; then
            missing="$path"
            break
        fi
    done

    if [ -n "$missing" ]; then
        error "This does not appear to be a complete TPM Operating System repository."
        printf 'Missing: %s\nRun the console from the repository root or restore the missing file.\n' "$missing" >&2
        return 1
    fi
    return 0
}

command_available() {
    command -v "$1" >/dev/null 2>&1
}

git_branch_name() {
    git -C "$TPM_DEV_ROOT" symbolic-ref --quiet --short HEAD 2>/dev/null || printf 'detached HEAD'
}

working_tree_description() {
    tree_output="$(git -C "$TPM_DEV_ROOT" status --short 2>/dev/null)"
    if [ $? -ne 0 ]; then
        printf 'unavailable'
    elif [ -n "$tree_output" ]; then
        printf 'changes present'
    else
        printf 'clean'
    fi
}
