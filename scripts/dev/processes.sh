#!/usr/bin/env bash

pid_is_numeric() {
    case "$1" in
        ""|*[!0-9]*) return 1 ;;
        *) return 0 ;;
    esac
}

pid_is_running() {
    pid_is_numeric "$1" && kill -0 "$1" 2>/dev/null
}

process_command() {
    command_output="$("$TPM_DEV_PS_COMMAND" -p "$1" -o command= 2>/dev/null)"
    command_status=$?
    if [ "$command_status" -ne 0 ] || [ -z "$command_output" ]; then
        return 2
    fi
    printf '%s\n' "$command_output"
    return 0
}

# Return codes for inspection helpers:
#   0 = data found / confirmed match
#   1 = confirmed absence / mismatch
#   2 = inspection unavailable or failed
capture_lsof() {
    inspection_error_file="$(mktemp "${TMPDIR:-/tmp}/tpm-dev-lsof.XXXXXX")" || return 2
    inspection_output="$("$TPM_DEV_LSOF_COMMAND" "$@" 2>"$inspection_error_file")"
    inspection_status=$?
    if [ "$inspection_status" -eq 0 ]; then
        rm -f "$inspection_error_file"
        printf '%s\n' "$inspection_output"
        return 0
    fi
    if [ "$inspection_status" -eq 1 ] && [ ! -s "$inspection_error_file" ]; then
        rm -f "$inspection_error_file"
        return 1
    fi
    rm -f "$inspection_error_file"
    return 2
}

process_working_directory() {
    lsof_output="$(capture_lsof -a -p "$1" -d cwd -Fn)"
    lsof_status=$?
    [ "$lsof_status" -eq 0 ] || return 2
    working_directory="$(printf '%s\n' "$lsof_output" | sed -n 's/^n//p' | head -n 1)"
    [ -n "$working_directory" ] || return 2
    printf '%s\n' "$working_directory"
    return 0
}

process_executable() {
    lsof_output="$(capture_lsof -a -p "$1" -d txt -Fn)"
    lsof_status=$?
    [ "$lsof_status" -eq 0 ] || return 2
    executable_path="$(printf '%s\n' "$lsof_output" | sed -n 's/^n//p' | head -n 1)"
    [ -n "$executable_path" ] || return 2
    printf '%s\n' "$executable_path"
    return 0
}

process_start_marker() {
    marker_output="$("$TPM_DEV_PS_COMMAND" -p "$1" -o lstart= 2>/dev/null)"
    marker_status=$?
    [ "$marker_status" -eq 0 ] || return 2
    marker_output="$(printf '%s\n' "$marker_output" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
    [ -n "$marker_output" ] || return 2
    printf '%s\n' "$marker_output"
    return 0
}

process_identity_signature() {
    identity_pid="$1"
    identity_command="$(process_command "$identity_pid")" || return 2
    identity_working_directory="$(process_working_directory "$identity_pid")" || return 2
    identity_executable="$(process_executable "$identity_pid")" || return 2
    identity_start_marker="$(process_start_marker "$identity_pid")" || return 2
    printf '%s|%s|%s|%s\n' \
        "$identity_command" \
        "$identity_working_directory" \
        "$identity_executable" \
        "$identity_start_marker"
    return 0
}

canonical_path() {
    if command_available realpath; then
        realpath "$1" 2>/dev/null
        return $?
    fi
    path_directory="$(dirname "$1")"
    path_name="$(basename "$1")"
    canonical_directory="$(cd "$path_directory" 2>/dev/null && pwd -P)" || return 1
    printf '%s/%s\n' "$canonical_directory" "$path_name"
}

configured_python_runtime_path() {
    "$TPM_DEV_ROOT/.venv/bin/python" -c \
        'import os, sys; print(os.path.realpath(sys.executable))' 2>/dev/null
}

backend_executable_matches() {
    command_text="$1"
    pid="$2"
    configured_python="$TPM_DEV_ROOT/.venv/bin/python"
    command_executable="${command_text%% *}"
    process_executable_path="$(process_executable "$pid")"
    executable_status=$?
    [ "$executable_status" -eq 0 ] || return 2

    if [ "$command_executable" = "$configured_python" ]; then
        return 0
    fi

    configured_runtime="$(configured_python_runtime_path)"
    [ -n "$configured_runtime" ] || return 2
    configured_runtime="$(canonical_path "$configured_runtime")" || return 2
    process_executable_path="$(canonical_path "$process_executable_path")" || return 2
    if [ "$process_executable_path" = "$configured_runtime" ]; then
        return 0
    fi

    # Apple's framework Python reports the Python.app executable in process
    # metadata rather than the virtual-environment launcher or sys.executable.
    runtime_directory="$(dirname "$(dirname "$configured_runtime")")"
    case "$process_executable_path" in
        "$runtime_directory"/Resources/Python.app/Contents/MacOS/Python) return 0 ;;
    esac
    return 1
}

frontend_executable_matches() {
    command_text="$1"
    pid="$2"
    command_executable="${command_text%% *}"
    configured_node="$(command -v "$TPM_DEV_NODE_COMMAND" 2>/dev/null)"
    [ -n "$configured_node" ] || return 2

    configured_node="$(canonical_path "$configured_node")" || return 2
    if [ "$command_executable" = "$TPM_DEV_NODE_COMMAND" ] ||
        [ "$(canonical_path "$command_executable")" = "$configured_node" ]; then
        process_executable_path="$(process_executable "$pid")"
        executable_status=$?
        [ "$executable_status" -eq 0 ] || return 2
        process_node="$(canonical_path "$process_executable_path")" || return 2
        [ "$process_node" = "$configured_node" ]
        return $?
    fi
    return 1
}

pid_matches_service() {
    service_name="$1"
    pid="$2"
    command_text="$(process_command "$pid")"
    command_status=$?
    [ "$command_status" -eq 0 ] || return 2
    working_directory="$(process_working_directory "$pid")"
    working_directory_status=$?
    [ "$working_directory_status" -eq 0 ] || return 2

    case "$service_name" in
        backend)
            [ "$working_directory" = "$TPM_DEV_ROOT" ] || return 1
            backend_executable_matches "$command_text" "$pid"
            executable_match_status=$?
            [ "$executable_match_status" -ne 2 ] || return 2
            [ "$executable_match_status" -eq 0 ] || return 1
            case "$command_text" in
                *" -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8000"*) return 0 ;;
            esac
            ;;
        frontend)
            [ "$working_directory" = "$TPM_DEV_ROOT/frontend" ] || return 1
            frontend_executable_matches "$command_text" "$pid"
            executable_match_status=$?
            [ "$executable_match_status" -ne 2 ] || return 2
            [ "$executable_match_status" -eq 0 ] || return 1
            case "$command_text" in
                *"$TPM_DEV_ROOT/frontend/node_modules/"*vite*" --host 127.0.0.1 --port 5173"*) return 0 ;;
            esac
            ;;
    esac
    return 1
}

port_pids() {
    listener_output="$(capture_lsof -nP -iTCP:"$1" -sTCP:LISTEN -t)"
    listener_status=$?
    if [ "$listener_status" -eq 0 ]; then
        printf '%s\n' "$listener_output" | sort -u
        return 0
    fi
    return "$listener_status"
}

port_is_occupied() {
    listener_pids="$(port_pids "$1")"
    listener_status=$?
    if [ "$listener_status" -eq 0 ]; then
        [ -n "$listener_pids" ]
        return $?
    fi
    return "$listener_status"
}

pid_owns_port() {
    expected_pid="$1"
    port="$2"
    listener_pids="$(port_pids "$port")"
    listener_status=$?
    [ "$listener_status" -eq 0 ] || return "$listener_status"
    for listener_pid in $listener_pids; do
        if [ "$listener_pid" = "$expected_pid" ]; then
            return 0
        fi
    done
    return 1
}

pid_belongs_to_tree() {
    candidate_pid="$1"
    ancestor_pid="$2"
    current_pid="$candidate_pid"
    depth=0
    while pid_is_numeric "$current_pid" && [ "$current_pid" -gt 1 ] && [ "$depth" -lt 12 ]; do
        if [ "$current_pid" = "$ancestor_pid" ]; then
            return 0
        fi
        current_pid="$("$TPM_DEV_PS_COMMAND" -p "$current_pid" -o ppid= 2>/dev/null | tr -d '[:space:]')"
        depth=$((depth + 1))
    done
    return 1
}

read_recorded_pid() {
    pid_file="$1"
    [ -f "$pid_file" ] || return 1
    IFS= read -r recorded_pid < "$pid_file"
    printf '%s' "$recorded_pid"
}

remove_pid_file() {
    pid_file="$1"
    [ ! -e "$pid_file" ] || rm -f "$pid_file"
}

write_pid_file() {
    pid_file="$1"
    pid="$2"
    temporary_file="$pid_file.tmp.$$"
    umask 077
    printf '%s\n' "$pid" > "$temporary_file" || return 1
    mv "$temporary_file" "$pid_file"
}

# Prints one of: running, stopped, stale PID, port conflict, inspection error.
# Stale metadata is removed after it is identified.
service_state_word() {
    service_name="$1"
    port="$2"
    pid_file="$3"
    recorded_pid="$(read_recorded_pid "$pid_file" 2>/dev/null)"
    pid_read_status=$?

    if [ "$pid_read_status" -eq 0 ]; then
        if ! pid_is_running "$recorded_pid"; then
            remove_pid_file "$pid_file"
            printf 'stale PID'
            return 0
        fi
        pid_matches_service "$service_name" "$recorded_pid"
        match_status=$?
        if [ "$match_status" -eq 2 ]; then
            printf 'inspection error'
            return 0
        fi
        if [ "$match_status" -eq 1 ]; then
            remove_pid_file "$pid_file"
            printf 'stale PID'
            return 0
        fi
        pid_owns_port "$recorded_pid" "$port"
        ownership_status=$?
        if [ "$ownership_status" -eq 2 ]; then
            printf 'inspection error'
            return 0
        fi
        if [ "$ownership_status" -eq 0 ]; then
            printf 'running'
            return 0
        fi
        remove_pid_file "$pid_file"
        printf 'stale PID'
        return 0
    fi

    port_is_occupied "$port"
    port_status=$?
    if [ "$port_status" -eq 2 ]; then
        printf 'inspection error'
    elif [ "$port_status" -eq 0 ]; then
        printf 'port conflict'
    else
        printf 'stopped'
    fi
}

wait_for_service() {
    service_name="$1"
    port="$2"
    launcher_pid="$3"
    attempts=0
    inspection_failed=0
    while [ "$attempts" -lt 50 ]; do
        listener_pids="$(port_pids "$port")"
        listener_status=$?
        if [ "$listener_status" -eq 2 ]; then
            inspection_failed=1
        else
            if [ "$listener_status" -eq 0 ]; then
                for listener_pid in $listener_pids; do
                    if pid_belongs_to_tree "$listener_pid" "$launcher_pid"; then
                        pid_matches_service "$service_name" "$listener_pid"
                        match_status=$?
                        if [ "$match_status" -eq 0 ]; then
                            printf '%s' "$listener_pid"
                            return 0
                        fi
                        [ "$match_status" -ne 2 ] || inspection_failed=1
                    fi
                done
            fi
            if ! pid_is_running "$launcher_pid" && [ "$listener_status" -eq 1 ]; then
                return 1
            fi
        fi
        attempts=$((attempts + 1))
        sleep 0.1
    done
    [ "$inspection_failed" -eq 0 ] || return 2
    return 1
}

cleanup_started_service() {
    service_name="$1"
    port="$2"
    launcher_pid="$3"
    launcher_start_marker="$4"
    listener_pids="$(port_pids "$port")"
    listener_status=$?
    if [ "$listener_status" -eq 0 ]; then
        for listener_pid in $listener_pids; do
            if pid_belongs_to_tree "$listener_pid" "$launcher_pid"; then
                pid_matches_service "$service_name" "$listener_pid"
                match_status=$?
                pid_owns_port "$listener_pid" "$port"
                ownership_status=$?
                if [ "$match_status" -eq 0 ] && [ "$ownership_status" -eq 0 ]; then
                    kill "$listener_pid" 2>/dev/null || true
                fi
            fi
        done
    fi
    if [ -n "$launcher_start_marker" ] &&
        pid_is_running "$launcher_pid" &&
        [ "$(process_start_marker "$launcher_pid")" = "$launcher_start_marker" ]; then
        kill "$launcher_pid" 2>/dev/null || true
    fi
}

start_backend() {
    cd "$TPM_DEV_ROOT" || return 1
    "$TPM_DEV_ROOT/.venv/bin/python" -m uvicorn backend.api.main:app \
        --host 127.0.0.1 --port 8000 >> "$TPM_DEV_BACKEND_LOG" 2>&1 &
    launcher_pid=$!
    launcher_start_marker="$(process_start_marker "$launcher_pid")"
    service_pid="$(wait_for_service backend 8000 "$launcher_pid")"
    wait_status=$?
    if [ "$wait_status" -ne 0 ]; then
        cleanup_started_service backend 8000 "$launcher_pid" "$launcher_start_marker"
        if [ "$wait_status" -eq 2 ]; then
            error "Backend startup could not be verified because process inspection failed. No PID metadata was written."
        else
            error "The backend did not start. Review $TPM_DEV_BACKEND_LOG for details."
        fi
        return 1
    fi
    if ! write_pid_file "$TPM_DEV_BACKEND_PID_FILE" "$service_pid"; then
        cleanup_started_service backend 8000 "$launcher_pid" "$launcher_start_marker"
        error "Backend PID metadata could not be saved. The new backend was stopped."
        return 1
    fi
    success "Backend started (PID $service_pid)."
    return 0
}

start_frontend() {
    cd "$TPM_DEV_ROOT/frontend" || return 1
    "$TPM_DEV_NPM_COMMAND" run dev -- --host 127.0.0.1 --port 5173 \
        >> "$TPM_DEV_FRONTEND_LOG" 2>&1 &
    launcher_pid=$!
    launcher_start_marker="$(process_start_marker "$launcher_pid")"
    service_pid="$(wait_for_service frontend 5173 "$launcher_pid")"
    wait_status=$?
    if [ "$wait_status" -ne 0 ]; then
        cleanup_started_service frontend 5173 "$launcher_pid" "$launcher_start_marker"
        if [ "$wait_status" -eq 2 ]; then
            error "Frontend startup could not be verified because process inspection failed. No PID metadata was written."
        else
            error "The frontend did not start. Review $TPM_DEV_FRONTEND_LOG for details."
        fi
        return 1
    fi
    if ! write_pid_file "$TPM_DEV_FRONTEND_PID_FILE" "$service_pid"; then
        cleanup_started_service frontend 5173 "$launcher_pid" "$launcher_start_marker"
        error "Frontend PID metadata could not be saved. The new frontend was stopped."
        return 1
    fi
    success "Frontend started (PID $service_pid)."
    return 0
}

wait_for_original_process_exit() {
    wait_pid="$1"
    wait_identity="$2"
    wait_attempts="${TPM_DEV_STOP_WAIT_ATTEMPTS:-50}"
    attempt=0

    while [ "$attempt" -lt "$wait_attempts" ]; do
        if ! pid_is_running "$wait_pid"; then
            return 0
        fi
        current_identity="$(process_identity_signature "$wait_pid")"
        identity_status=$?
        if [ "$identity_status" -eq 0 ]; then
            if [ "$current_identity" != "$wait_identity" ]; then
                return 0
            fi
        elif ! pid_is_running "$wait_pid"; then
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 0.1
    done

    if ! pid_is_running "$wait_pid"; then
        return 0
    fi
    current_identity="$(process_identity_signature "$wait_pid")"
    identity_status=$?
    if [ "$identity_status" -eq 0 ]; then
        [ "$current_identity" != "$wait_identity" ] && return 0
        return 1
    fi
    if ! pid_is_running "$wait_pid"; then
        return 0
    fi
    return 2
}

finish_confirmed_stop() {
    display_name="$1"
    pid_file="$2"
    port="$3"

    port_listeners="$(port_pids "$port")"
    port_status=$?
    remove_pid_file "$pid_file"
    if [ "$port_status" -eq 2 ]; then
        error "$display_name stopped, but release of port $port could not be verified because inspection failed."
        return 2
    fi
    if [ "$port_status" -eq 0 ] && [ -n "$port_listeners" ]; then
        error "$display_name stopped, but port $port is now owned by another process. No additional process was signaled."
        return 1
    fi
    success "$display_name stopped."
    return 0
}

stop_recorded_service() {
    service_name="$1"
    display_name="$2"
    pid_file="$3"
    port="$4"
    recorded_pid="$(read_recorded_pid "$pid_file" 2>/dev/null)"
    if [ $? -ne 0 ]; then
        success "$display_name is already stopped."
        return 0
    fi

    if ! pid_is_running "$recorded_pid"; then
        remove_pid_file "$pid_file"
        success "$display_name was already stopped; stale PID metadata was removed."
        return 0
    fi
    if ! command_available "$TPM_DEV_LSOF_COMMAND"; then
        error "$display_name state is unknown because lsof is unavailable. PID metadata was preserved and no signal was sent."
        return 2
    fi

    pid_matches_service "$service_name" "$recorded_pid"
    match_status=$?
    if [ "$match_status" -eq 2 ]; then
        error "$display_name state is unknown because process inspection failed. PID metadata was preserved and no signal was sent."
        return 2
    fi
    if [ "$match_status" -eq 1 ]; then
        remove_pid_file "$pid_file"
        warning "$display_name PID metadata did not match a console-owned service. The process was not stopped."
        return 0
    fi
    pid_owns_port "$recorded_pid" "$port"
    ownership_status=$?
    if [ "$ownership_status" -eq 2 ]; then
        error "$display_name state is unknown because port ownership inspection failed. PID metadata was preserved and no signal was sent."
        return 2
    fi
    if [ "$ownership_status" -eq 1 ]; then
        remove_pid_file "$pid_file"
        error "$display_name PID metadata is stale or unsafe: PID $recorded_pid does not own port $port. The process was not stopped."
        return 1
    fi

    original_identity="$(process_identity_signature "$recorded_pid")"
    identity_status=$?
    if [ "$identity_status" -ne 0 ] || [ -z "$original_identity" ]; then
        error "$display_name state is unknown because its process generation could not be inspected. PID metadata was preserved and no signal was sent."
        return 2
    fi

    # Revalidate immediately before TERM to minimize PID-reuse and port races.
    pid_matches_service "$service_name" "$recorded_pid"
    recheck_match_status=$?
    pid_owns_port "$recorded_pid" "$port"
    recheck_ownership_status=$?
    recheck_identity="$(process_identity_signature "$recorded_pid")"
    recheck_identity_status=$?
    if ! pid_is_running "$recorded_pid" ||
        [ "$recheck_match_status" -ne 0 ] ||
        [ "$recheck_ownership_status" -ne 0 ] ||
        [ "$recheck_identity_status" -ne 0 ] ||
        [ "$recheck_identity" != "$original_identity" ]; then
        if [ "$recheck_match_status" -eq 2 ] ||
            [ "$recheck_ownership_status" -eq 2 ] ||
            [ "$recheck_identity_status" -eq 2 ]; then
            error "$display_name ownership revalidation failed. PID metadata was preserved and no signal was sent."
            return 2
        fi
        remove_pid_file "$pid_file"
        error "$display_name process ownership changed before termination. The process was not stopped."
        return 1
    fi
    kill "$recorded_pid" 2>/dev/null || {
        error "$display_name could not be stopped. Check permissions for PID $recorded_pid."
        return 1
    }

    wait_for_original_process_exit "$recorded_pid" "$original_identity"
    term_wait_status=$?
    if [ "$term_wait_status" -eq 0 ]; then
        finish_confirmed_stop "$display_name" "$pid_file" "$port"
        return $?
    fi
    if [ "$term_wait_status" -eq 2 ]; then
        error "$display_name termination could not be confirmed because process inspection failed. PID metadata was preserved and KILL was not sent."
        return 2
    fi

    if pid_is_running "$recorded_pid"; then
        pid_matches_service "$service_name" "$recorded_pid"
        kill_match_status=$?
        pid_owns_port "$recorded_pid" "$port"
        kill_ownership_status=$?
        kill_identity="$(process_identity_signature "$recorded_pid")"
        kill_identity_status=$?
        if [ "$kill_match_status" -ne 0 ] ||
            [ "$kill_ownership_status" -ne 0 ] ||
            [ "$kill_identity_status" -ne 0 ] ||
            [ "$kill_identity" != "$original_identity" ]; then
            if [ "$kill_match_status" -eq 2 ] ||
                [ "$kill_ownership_status" -eq 2 ] ||
                [ "$kill_identity_status" -eq 2 ]; then
                error "$display_name inspection failed after TERM. PID metadata was preserved and KILL was not sent."
                return 2
            fi
            remove_pid_file "$pid_file"
            error "$display_name process identity or port ownership changed after TERM. KILL was not sent."
            return 1
        fi
        warning "$display_name did not stop gracefully; sending a forced termination only to recorded PID $recorded_pid."
        kill -KILL "$recorded_pid" 2>/dev/null || {
            error "$display_name is still running as PID $recorded_pid."
            return 1
        }
        wait_for_original_process_exit "$recorded_pid" "$original_identity"
        kill_wait_status=$?
        if [ "$kill_wait_status" -eq 1 ]; then
            error "$display_name forced termination could not be confirmed before the timeout. PID metadata was preserved."
            return 1
        fi
        if [ "$kill_wait_status" -eq 2 ]; then
            error "$display_name forced termination could not be confirmed because process inspection failed. PID metadata was preserved."
            return 2
        fi
    fi
    finish_confirmed_stop "$display_name" "$pid_file" "$port"
}

start_development() {
    validate_start_prerequisites || return 1

    backend_state="$(service_state_word backend 8000 "$TPM_DEV_BACKEND_PID_FILE")"
    frontend_state="$(service_state_word frontend 5173 "$TPM_DEV_FRONTEND_PID_FILE")"
    if [ "$backend_state" = "inspection error" ] || [ "$frontend_state" = "inspection error" ]; then
        error "Development services could not be inspected safely. Existing PID metadata was preserved; no service was started."
        printf 'Restore lsof access, then run ./tpm-dev status before trying again.\n' >&2
        return 1
    fi
    if [ "$backend_state" = "port conflict" ]; then
        error "Port 8000 is already used by a process not managed by this console."
        printf 'Stop or reconfigure that process, then run ./tpm-dev start again.\n' >&2
        return 1
    fi
    if [ "$frontend_state" = "port conflict" ]; then
        error "Port 5173 is already used by a process not managed by this console."
        printf 'Stop or reconfigure that process, then run ./tpm-dev start again.\n' >&2
        return 1
    fi

    mkdir -p "$TPM_DEV_RUNTIME_DIR" || {
        error "The runtime directory could not be created at $TPM_DEV_RUNTIME_DIR."
        return 1
    }
    started_backend=0
    if [ "$backend_state" = "running" ]; then
        info "Backend is already running under this console."
    else
        start_backend || return 1
        started_backend=1
    fi

    if [ "$frontend_state" = "running" ]; then
        info "Frontend is already running under this console."
    elif ! start_frontend; then
        if [ "$started_backend" -eq 1 ]; then
            warning "Frontend startup failed; stopping the backend started by this invocation."
            stop_recorded_service backend "Backend" "$TPM_DEV_BACKEND_PID_FILE" 8000
        fi
        return 1
    fi

    cat <<EOF

Backend:
$TPM_DEV_BACKEND_URL

Frontend:
$TPM_DEV_FRONTEND_URL

Logs:
$TPM_DEV_RUNTIME_DIR
EOF
    return 0
}

stop_development() {
    validate_repository || return 1
    frontend_result=0
    backend_result=0
    stop_recorded_service frontend "Frontend" "$TPM_DEV_FRONTEND_PID_FILE" 5173 || frontend_result=$?
    stop_recorded_service backend "Backend" "$TPM_DEV_BACKEND_PID_FILE" 8000 || backend_result=$?
    if [ "$frontend_result" -ne 0 ] || [ "$backend_result" -ne 0 ]; then
        return 1
    fi
    return 0
}

show_status() {
    validate_repository || return 1
    backend_state="$(service_state_word backend 8000 "$TPM_DEV_BACKEND_PID_FILE")"
    frontend_state="$(service_state_word frontend 5173 "$TPM_DEV_FRONTEND_PID_FILE")"
    cat <<EOF
TPM Operating System Developer Status

Backend:  $backend_state
URL:      $TPM_DEV_BACKEND_URL
Log:      $TPM_DEV_BACKEND_LOG

Frontend: $frontend_state
URL:      $TPM_DEV_FRONTEND_URL
Log:      $TPM_DEV_FRONTEND_LOG

Git branch:   $(git_branch_name)
Working tree: $(working_tree_description)
EOF
    return 0
}
