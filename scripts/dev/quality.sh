#!/usr/bin/env bash

run_backend_tests() {
    validate_repository || return 1
    require_python || return 1
    info "Running backend tests..."
    cd "$TPM_DEV_ROOT" || return 1
    PYTHONDONTWRITEBYTECODE=1 "$TPM_DEV_ROOT/.venv/bin/python" \
        -m unittest discover -s tests -v
}

run_frontend_tests() {
    validate_repository || return 1
    require_node || return 1
    require_npm || return 1
    info "Running frontend tests..."
    cd "$TPM_DEV_ROOT/frontend" || return 1
    "$TPM_DEV_NPM_COMMAND" test -- --reporter=dot
}

run_tests() {
    backend_result=0
    frontend_result=0
    run_backend_tests || backend_result=$?
    run_frontend_tests || frontend_result=$?

    printf '\nTest summary\n'
    if [ "$backend_result" -eq 0 ]; then
        success "Backend tests passed."
    else
        error "Backend tests failed (exit $backend_result)."
    fi
    if [ "$frontend_result" -eq 0 ]; then
        success "Frontend tests passed."
    else
        error "Frontend tests failed (exit $frontend_result)."
    fi
    if [ "$backend_result" -ne 0 ] || [ "$frontend_result" -ne 0 ]; then
        return 1
    fi
    return 0
}

build_frontend() {
    validate_repository || return 1
    require_node || return 1
    require_npm || return 1
    info "Building the production frontend..."
    cd "$TPM_DEV_ROOT/frontend" || return 1
    "$TPM_DEV_NPM_COMMAND" run build
}

check_secret_like_files() {
    findings_file="${TMPDIR:-/tmp}/tpm-dev-secret-check.$$"
    find "$TPM_DEV_ROOT" \
        \( -path "$TPM_DEV_ROOT/.git" -o \
           -path "$TPM_DEV_ROOT/.venv" -o \
           -path "$TPM_DEV_ROOT/.tpm-dev" -o \
           -path "$TPM_DEV_ROOT/frontend/node_modules" -o \
           -path "$TPM_DEV_ROOT/frontend/dist" \) -prune -o \
        -type f \( -name '.env' -o -name '.env.*' -o -name '*.pem' -o \
                   -name '*.key' -o -iname '*secret*' \) -print > "$findings_file"

    result=0
    while IFS= read -r candidate; do
        [ -n "$candidate" ] || continue
        relative_path="${candidate#"$TPM_DEV_ROOT/"}"
        if [ "$relative_path" = "frontend/.env.local" ] &&
            git -C "$TPM_DEV_ROOT" check-ignore -q -- "$relative_path" &&
            ! git -C "$TPM_DEV_ROOT" ls-files --error-unmatch -- "$relative_path" >/dev/null 2>&1; then
            continue
        fi
        error "Secret-like or local environment file requires review: $relative_path"
        result=1
    done < "$findings_file"
    rm -f "$findings_file"

    if [ "$result" -ne 0 ]; then
        printf 'Remove, ignore, or explicitly review these files before release.\n' >&2
        return 1
    fi
    success "No unexpected local environment or secret-like files found."
    return 0
}

check_frontend_env_ignored() {
    if git -C "$TPM_DEV_ROOT" ls-files --error-unmatch -- frontend/.env.local >/dev/null 2>&1; then
        error "frontend/.env.local is tracked. Remove it from Git before release."
        return 1
    fi
    if ! git -C "$TPM_DEV_ROOT" check-ignore -q -- frontend/.env.local; then
        error "frontend/.env.local is not ignored."
        printf 'Add frontend/.env.local to .gitignore before release.\n' >&2
        return 1
    fi
    success "frontend/.env.local is ignored and untracked."
    return 0
}

check_working_tree_clean() {
    status_output="$(git -C "$TPM_DEV_ROOT" status --short 2>&1)"
    git_status=$?
    if [ "$git_status" -ne 0 ]; then
        error "Git could not inspect the working tree."
        [ -z "$status_output" ] || printf '%s\n' "$status_output" >&2
        return "$git_status"
    fi
    if [ -n "$status_output" ]; then
        error "The working tree is dirty. Commit, stash, or remove these changes before release:"
        printf '%s\n' "$status_output" >&2
        return 1
    fi
    success "Working tree is clean."
    return 0
}

resolve_release_base() {
    if [ -n "${TPM_DEV_RELEASE_BASE:-}" ]; then
        release_base="$TPM_DEV_RELEASE_BASE"
    else
        release_base="$(git -C "$TPM_DEV_ROOT" describe \
            --tags --abbrev=0 --match 'v[0-9]*' HEAD^ 2>/dev/null)"
        describe_status=$?
        if [ "$describe_status" -ne 0 ] || [ -z "$release_base" ]; then
            error "Git could not determine the previous version tag for the release check."
            printf 'Set TPM_DEV_RELEASE_BASE to a valid release commit or tag and try again.\n' >&2
            return 1
        fi
    fi

    if ! git -C "$TPM_DEV_ROOT" rev-parse --verify \
        "${release_base}^{commit}" >/dev/null 2>&1; then
        error "Release base '$release_base' is not a valid commit or tag."
        return 1
    fi
    if ! git -C "$TPM_DEV_ROOT" merge-base --is-ancestor \
        "$release_base" HEAD >/dev/null 2>&1; then
        error "Release base '$release_base' is not an ancestor of HEAD."
        return 1
    fi

    printf '%s\n' "$release_base"
}

check_committed_release_whitespace() {
    release_base="$(resolve_release_base)" || return $?
    whitespace_output="$(git -C "$TPM_DEV_ROOT" diff \
        --check "$release_base..HEAD" 2>&1)"
    whitespace_status=$?
    if [ "$whitespace_status" -ne 0 ]; then
        error "Committed changes since $release_base contain whitespace errors."
        [ -z "$whitespace_output" ] || printf '%s\n' "$whitespace_output" >&2
        return "$whitespace_status"
    fi
    success "Committed changes since $release_base passed whitespace validation."
    return 0
}

release_step() {
    step_name="$1"
    shift
    info ""
    info "== $step_name =="
    "$@"
}

run_release_check() {
    validate_repository || return 1
    failed_steps=""

    release_step "1. Backend tests" run_backend_tests ||
        failed_steps="$failed_steps backend-tests"
    release_step "2. Frontend tests" run_frontend_tests ||
        failed_steps="$failed_steps frontend-tests"
    release_step "3. Frontend production build" build_frontend ||
        failed_steps="$failed_steps frontend-build"
    release_step "4. Committed release whitespace validation" check_committed_release_whitespace ||
        failed_steps="$failed_steps git-diff-check"
    release_step "5. Git working-tree status" check_working_tree_clean ||
        failed_steps="$failed_steps git-status"
    release_step "6. Local environment and secret-like file check" check_secret_like_files ||
        failed_steps="$failed_steps secret-check"
    release_step "7. frontend/.env.local tracking check" check_frontend_env_ignored ||
        failed_steps="$failed_steps frontend-env-check"

    printf '\nRelease-check summary\n'
    if [ -n "$failed_steps" ]; then
        error "Release check failed:$failed_steps"
        printf 'Resolve the reported failures and run ./tpm-dev release-check again.\n' >&2
        return 1
    fi
    success "All required release checks passed."
    info "No commit or push was performed."
    return 0
}
