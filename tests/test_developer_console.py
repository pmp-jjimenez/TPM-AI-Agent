import os
from pathlib import Path
import subprocess
import tempfile
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CONSOLE = REPOSITORY_ROOT / "tpm-dev"
SHELL_FILES = [CONSOLE, *sorted((REPOSITORY_ROOT / "scripts" / "dev").glob("*.sh"))]


class DeveloperConsoleTests(unittest.TestCase):
    def run_console(self, *arguments, root=None, extra_environment=None):
        environment = os.environ.copy()
        if root is not None:
            environment["TPM_DEV_ROOT_OVERRIDE"] = str(root)
        if extra_environment:
            environment.update(extra_environment)
        return subprocess.run(
            ["/bin/bash", str(CONSOLE), *arguments],
            cwd=REPOSITORY_ROOT,
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10,
            check=False,
        )

    def make_repository_fixture(self):
        temporary_directory = tempfile.TemporaryDirectory()
        root = Path(temporary_directory.name)
        for path in ("app/main.py", "backend/api/main.py", "frontend/package.json"):
            target = root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("{}\n" if target.suffix == ".json" else "# fixture\n")
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        return temporary_directory, root

    def run_environment_validation(self, root):
        python = root / ".venv/bin/python"
        python.parent.mkdir(parents=True, exist_ok=True)
        if not python.exists():
            python.symlink_to(REPOSITORY_ROOT / ".venv/bin/python")
        script = """
TPM_DEV_ROOT="$1"
TPM_DEV_RUNTIME_DIR_OVERRIDE="$1/.tpm-dev"
. "$2/common.sh"
. "$2/environment.sh"
validate_frontend_environment
"""
        return subprocess.run(
            [
                "/bin/bash",
                "-c",
                script,
                "environment-test",
                str(root),
                str(REPOSITORY_ROOT / "scripts" / "dev"),
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5,
            check=False,
        )

    def prepare_committed_repository_fixture(self, root):
        subprocess.run(["git", "-C", str(root), "add", "."], check=True)
        subprocess.run(
            [
                "git",
                "-C",
                str(root),
                "-c",
                "user.name=Developer Console Test",
                "-c",
                "user.email=developer-console@example.invalid",
                "commit",
                "-qm",
                "fixture baseline",
            ],
            check=True,
        )

    def run_working_tree_check(self, root, simulate_git_failure=False):
        script = """
TPM_DEV_ROOT="$1"
TPM_DEV_RUNTIME_DIR_OVERRIDE="$1/.tpm-dev"
. "$2/common.sh"
. "$2/environment.sh"
. "$2/quality.sh"
if [ "$3" = "fail" ]; then
    git() {
        printf 'simulated git status failure\\n' >&2
        return 37
    }
fi
check_working_tree_clean
"""
        return subprocess.run(
            [
                "/bin/bash",
                "-c",
                script,
                "working-tree-test",
                str(root),
                str(REPOSITORY_ROOT / "scripts" / "dev"),
                "fail" if simulate_git_failure else "normal",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5,
            check=False,
        )

    def run_committed_whitespace_check(self, root, release_base="v0.7.0"):
        script = """
TPM_DEV_ROOT="$1"
TPM_DEV_RUNTIME_DIR_OVERRIDE="$1/.tpm-dev"
TPM_DEV_RELEASE_BASE="$3"
. "$2/common.sh"
. "$2/environment.sh"
. "$2/quality.sh"
check_committed_release_whitespace
"""
        return subprocess.run(
            [
                "/bin/bash",
                "-c",
                script,
                "whitespace-test",
                str(root),
                str(REPOSITORY_ROOT / "scripts" / "dev"),
                release_base,
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5,
            check=False,
        )

    def commit_fixture_change(self, root, message="fixture change"):
        subprocess.run(["git", "-C", str(root), "add", "."], check=True)
        subprocess.run(
            [
                "git",
                "-C",
                str(root),
                "-c",
                "user.name=Developer Console Test",
                "-c",
                "user.email=developer-console@example.invalid",
                "commit",
                "-qm",
                message,
            ],
            check=True,
        )

    def run_backend_process_match(self, root, command, process_executable):
        script = """
TPM_DEV_ROOT="$1"
TPM_DEV_RUNTIME_DIR_OVERRIDE="$1/.tpm-dev"
. "$2/common.sh"
. "$2/environment.sh"
. "$2/processes.sh"
process_command() { printf '%s\\n' "$MOCK_PROCESS_COMMAND"; }
process_working_directory() { printf '%s\\n' "$TPM_DEV_ROOT"; }
process_executable() { printf '%s\\n' "$MOCK_PROCESS_EXECUTABLE"; }
configured_python_runtime_path() { printf '%s\\n' "$TPM_DEV_ROOT/.venv/bin/python"; }
canonical_path() { printf '%s\\n' "$1"; }
pid_matches_service backend 4242
"""
        environment = os.environ.copy()
        environment.update(
            {
                "MOCK_PROCESS_COMMAND": command,
                "MOCK_PROCESS_EXECUTABLE": process_executable,
            }
        )
        return subprocess.run(
            [
                "/bin/bash",
                "-c",
                script,
                "process-test",
                str(root),
                str(REPOSITORY_ROOT / "scripts" / "dev"),
            ],
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5,
            check=False,
        )

    def run_stop_safety_scenario(
        self, root, service, port, owned_port, scenario="normal"
    ):
        runtime = root / ".tpm-dev"
        runtime.mkdir(exist_ok=True)
        pid_file = runtime / f"{service}.pid"
        pid_file.write_text("4242\n")
        signal_log = root / f"{service}-signals.log"
        script = """
TPM_DEV_ROOT="$1"
TPM_DEV_RUNTIME_DIR_OVERRIDE="$1/.tpm-dev"
. "$2/common.sh"
. "$2/environment.sh"
. "$2/processes.sh"
MOCK_RUNNING=1
MOCK_REUSED=0
MOCK_KILL_SENT=0
MOCK_POST_KILL_CHECKS=0
pid_is_running() {
    if [ "$SCENARIO" = "delayed-kill" ] && [ "$MOCK_KILL_SENT" -eq 1 ]; then
        MOCK_POST_KILL_CHECKS=$((MOCK_POST_KILL_CHECKS + 1))
        [ "$MOCK_POST_KILL_CHECKS" -lt 3 ]
        return $?
    fi
    [ "$MOCK_RUNNING" -eq 1 ]
}
pid_matches_service() {
    [ "$SCENARIO" != "mismatch" ]
}
pid_owns_port() { [ "$2" = "$OWNED_PORT" ]; }
port_pids() {
    if [ "$SCENARIO" = "port-taken" ]; then
        printf '9999\\n'
        return 0
    fi
    return 1
}
process_identity_signature() {
    if [ "$SCENARIO" = "inspection-after-kill" ] &&
        [ "$MOCK_KILL_SENT" -eq 1 ]; then
        return 2
    fi
    if [ "$MOCK_REUSED" -eq 1 ]; then
        printf 'reused-process\\n'
    else
        printf 'original-process\\n'
    fi
}
sleep() { :; }
kill() {
    printf '%s\\n' "$*" >> "$SIGNAL_LOG"
    case "$SCENARIO:$1" in
        delayed-kill:-KILL) MOCK_KILL_SENT=1 ;;
        timeout:-KILL) MOCK_KILL_SENT=1 ;;
        reuse-after-kill:-KILL) MOCK_KILL_SENT=1; MOCK_REUSED=1 ;;
        inspection-after-kill:-KILL) MOCK_KILL_SENT=1 ;;
        delayed-kill:*) return 0 ;;
        timeout:*) return 0 ;;
        reuse-after-kill:*) return 0 ;;
        inspection-after-kill:*) return 0 ;;
        reuse:*) MOCK_REUSED=1 ;;
        *) MOCK_RUNNING=0 ;;
    esac
    return 0
}
stop_recorded_service "$SERVICE" "$SERVICE" "$PID_FILE" "$PORT"
"""
        environment = os.environ.copy()
        environment.update(
            {
                "OWNED_PORT": str(owned_port),
                "PID_FILE": str(pid_file),
                "PORT": str(port),
                "SCENARIO": scenario,
                "SERVICE": service,
                "SIGNAL_LOG": str(signal_log),
            }
        )
        result = subprocess.run(
            [
                "/bin/bash",
                "-c",
                script,
                "stop-safety-test",
                str(root),
                str(REPOSITORY_ROOT / "scripts" / "dev"),
            ],
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5,
            check=False,
        )
        signals = signal_log.read_text().splitlines() if signal_log.exists() else []
        return result, signals, pid_file

    def make_lsof_failure_fixture(self, operational_error=False):
        fixture, root = self.make_repository_fixture()
        bin_directory = root / "fixture-bin"
        bin_directory.mkdir()
        launch_marker = root / "service-launch-attempted"
        python = root / ".venv/bin/python"
        python.parent.mkdir(parents=True)
        python.write_text(
            "#!/bin/sh\n"
            "if [ \"$1\" = \"-\" ]; then\n"
            f"    exec '{REPOSITORY_ROOT / '.venv/bin/python'}' \"$@\"\n"
            "fi\n"
            f"printf 'launched\\n' > '{launch_marker}'\n"
            "exec sleep 30\n"
        )
        python.chmod(0o755)
        (root / "frontend/.env.local").write_text(
            "VITE_API_BASE_URL=http://127.0.0.1:8000\n"
        )
        if operational_error:
            lsof_command = bin_directory / "lsof-error"
            lsof_command.write_text(
                "#!/bin/sh\nprintf 'simulated lsof failure\\n' >&2\nexit 23\n"
            )
            lsof_command.chmod(0o755)
        else:
            lsof_command = bin_directory / "missing-lsof"
        overrides = {"TPM_DEV_LSOF_COMMAND": str(lsof_command)}
        return fixture, root, launch_marker, overrides

    def test_help_output_lists_supported_commands(self):
        result = self.run_console("help")
        self.assertEqual(result.returncode, 0, result.stderr)
        for command in (
            "start",
            "stop",
            "status",
            "test",
            "build",
            "release-check",
            "cli",
            "help",
        ):
            self.assertIn(command, result.stdout)

    def test_invalid_command_has_nonzero_exit_and_corrective_action(self):
        result = self.run_console("not-a-command")
        self.assertEqual(result.returncode, 2)
        self.assertIn("Unknown command", result.stderr)
        self.assertIn("./tpm-dev help", result.stderr)

    def test_repository_validation_fails_outside_complete_repository(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_console("status", root=Path(directory))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("complete TPM Operating System repository", result.stderr)
        self.assertIn("Missing:", result.stderr)

    def test_status_reports_services_stopped(self):
        fixture, root = self.make_repository_fixture()
        with fixture:
            result = self.run_console("status", root=root)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Backend:  stopped", result.stdout)
        self.assertIn("Frontend: stopped", result.stdout)

    def test_status_removes_stale_pid_metadata_and_reports_it(self):
        fixture, root = self.make_repository_fixture()
        with fixture:
            runtime = root / ".tpm-dev"
            runtime.mkdir()
            pid_file = runtime / "backend.pid"
            pid_file.write_text("99999999\n")
            result = self.run_console("status", root=root)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Backend:  stale PID", result.stdout)
            self.assertFalse(pid_file.exists())

    def test_missing_node_prerequisite_is_actionable_and_nonzero(self):
        fixture, root = self.make_repository_fixture()
        with fixture:
            python = root / ".venv/bin/python"
            python.parent.mkdir(parents=True)
            python.write_text("#!/bin/sh\nexit 0\n")
            python.chmod(0o755)
            result = self.run_console(
                "start",
                root=root,
                extra_environment={"TPM_DEV_NODE_COMMAND": "definitely-missing-node"},
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Node.js was not found", result.stderr)
        self.assertIn("Install or configure Node.js", result.stderr)

    def test_missing_lsof_prevents_start_before_any_service_launch(self):
        fixture, root, launch_marker, overrides = self.make_lsof_failure_fixture()
        with fixture:
            result = self.run_console("start", root=root, extra_environment=overrides)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("lsof utility was not found", result.stderr)
            self.assertFalse(launch_marker.exists())
            self.assertFalse((root / ".tpm-dev/backend.pid").exists())
            self.assertFalse((root / ".tpm-dev/frontend.pid").exists())

    def test_missing_frontend_environment_is_actionable_and_nonzero(self):
        fixture, root = self.make_repository_fixture()
        with fixture:
            python = root / ".venv/bin/python"
            python.parent.mkdir(parents=True)
            python.write_text("#!/bin/sh\nexit 0\n")
            python.chmod(0o755)
            result = self.run_console("start", root=root)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("frontend/.env.local was not found", result.stderr)
        self.assertIn("VITE_API_BASE_URL=http://127.0.0.1:8000", result.stderr)

    def test_frontend_environment_accepts_unquoted_and_matching_quotes(self):
        fixture, root = self.make_repository_fixture()
        with fixture:
            env_file = root / "frontend/.env.local"
            valid_values = (
                "VITE_API_BASE_URL=http://127.0.0.1:8000",
                "VITE_API_BASE_URL=http://localhost:8000",
                "VITE_API_BASE_URL=https://example.com",
                ' VITE_API_BASE_URL = "http://127.0.0.1:8000"  ',
                "VITE_API_BASE_URL='http://127.0.0.1:8000'",
                'VITE_API_BASE_URL="http://localhost:8000"',
                "VITE_API_BASE_URL='https://example.com'",
            )
            for value in valid_values:
                with self.subTest(value=value):
                    env_file.write_text(f"{value}\n")
                    result = self.run_environment_validation(root)
                    self.assertEqual(result.returncode, 0, result.stderr)

    def test_frontend_environment_rejects_empty_and_malformed_values(self):
        fixture, root = self.make_repository_fixture()
        with fixture:
            env_file = root / "frontend/.env.local"
            invalid_values = (
                "VITE_API_BASE_URL=",
                'VITE_API_BASE_URL=""',
                "VITE_API_BASE_URL=''",
                "VITE_API_BASE_URL=ftp://127.0.0.1:8000",
                "VITE_API_BASE_URL=http://",
                "VITE_API_BASE_URL=http://:8000",
                "VITE_API_BASE_URL=http://?query",
                "VITE_API_BASE_URL=https://#fragment",
                'VITE_API_BASE_URL="http://127.0.0.1:8000',
                "VITE_API_BASE_URL=http://127.0.0.1:8000 trailing",
            )
            for value in invalid_values:
                with self.subTest(value=value):
                    env_file.write_text(f"{value}\n")
                    result = self.run_environment_validation(root)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertNotIn("ftp://127.0.0.1:8000", result.stderr)

    def test_clean_working_tree_passes_release_status_check(self):
        fixture, root = self.make_repository_fixture()
        with fixture:
            self.prepare_committed_repository_fixture(root)
            result = self.run_working_tree_check(root)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Working tree is clean", result.stdout)

    def test_modified_tracked_file_fails_release_status_check(self):
        fixture, root = self.make_repository_fixture()
        with fixture:
            self.prepare_committed_repository_fixture(root)
            (root / "app/main.py").write_text("# modified fixture\n")
            result = self.run_working_tree_check(root)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("working tree is dirty", result.stderr)
        self.assertIn("app/main.py", result.stderr)

    def test_untracked_file_fails_release_status_check(self):
        fixture, root = self.make_repository_fixture()
        with fixture:
            self.prepare_committed_repository_fixture(root)
            (root / "temporary-untracked.txt").write_text("fixture\n")
            result = self.run_working_tree_check(root)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("working tree is dirty", result.stderr)
        self.assertIn("temporary-untracked.txt", result.stderr)

    def test_git_status_failure_preserves_nonzero_exit(self):
        fixture, root = self.make_repository_fixture()
        with fixture:
            result = self.run_working_tree_check(root, simulate_git_failure=True)
        self.assertEqual(result.returncode, 37)
        self.assertIn("Git could not inspect the working tree", result.stderr)
        self.assertIn("simulated git status failure", result.stderr)

    def test_backend_match_accepts_lowercase_repository_python_launcher(self):
        fixture, root = self.make_repository_fixture()
        with fixture:
            python = root / ".venv/bin/python"
            command = (
                f"{python} -m uvicorn backend.api.main:app "
                "--host 127.0.0.1 --port 8000"
            )
            result = self.run_backend_process_match(root, command, str(python))
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_backend_match_rejects_unrelated_python_or_uvicorn_process(self):
        fixture, root = self.make_repository_fixture()
        with fixture:
            command = (
                "/other/project/.venv/bin/python -m uvicorn "
                "backend.api.main:app --host 127.0.0.1 --port 8000"
            )
            result = self.run_backend_process_match(
                root, command, "/other/project/.venv/bin/python"
            )
        self.assertNotEqual(result.returncode, 0)

    def test_wait_for_service_retries_transient_inspection_errors(self):
        fixture, root = self.make_repository_fixture()
        with fixture:
            script = """
TPM_DEV_ROOT="$1"
TPM_DEV_RUNTIME_DIR_OVERRIDE="$1/.tpm-dev"
. "$2/common.sh"
. "$2/environment.sh"
. "$2/processes.sh"
INSPECTION_COUNTER="$1/inspection-attempts"
printf '0\\n' > "$INSPECTION_COUNTER"
port_pids() {
    inspection_attempts="$(cat "$INSPECTION_COUNTER")"
    inspection_attempts=$((inspection_attempts + 1))
    printf '%s\\n' "$inspection_attempts" > "$INSPECTION_COUNTER"
    if [ "$inspection_attempts" -lt 3 ]; then
        return 2
    fi
    printf '4242\\n'
}
pid_is_running() { return 0; }
pid_belongs_to_tree() { return 0; }
pid_matches_service() { return 0; }
sleep() { :; }
wait_for_service backend 8000 4242
"""
            result = subprocess.run(
                [
                    "/bin/bash",
                    "-c",
                    script,
                    "wait-test",
                    str(root),
                    str(REPOSITORY_ROOT / "scripts" / "dev"),
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5,
                check=False,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "4242")

    def test_stop_allows_recorded_service_that_owns_expected_port(self):
        fixture, root = self.make_repository_fixture()
        with fixture:
            result, signals, pid_file = self.run_stop_safety_scenario(
                root, "backend", 8000, 8000
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(signals, ["4242"])
            self.assertFalse(pid_file.exists())

    def test_stop_rejects_matching_pid_without_expected_port_for_both_services(self):
        for service, port in (("backend", 8000), ("frontend", 5173)):
            with self.subTest(service=service):
                fixture, root = self.make_repository_fixture()
                with fixture:
                    result, signals, pid_file = self.run_stop_safety_scenario(
                        root, service, port, 0
                    )
                    self.assertNotEqual(result.returncode, 0)
                    self.assertEqual(signals, [])
                    self.assertIn("stale or unsafe", result.stderr)
                    self.assertFalse(pid_file.exists())

    def test_stop_rejects_pid_that_owns_a_different_port(self):
        fixture, root = self.make_repository_fixture()
        with fixture:
            result, signals, pid_file = self.run_stop_safety_scenario(
                root, "backend", 8000, 9000
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(signals, [])
            self.assertIn("does not own port 8000", result.stderr)
            self.assertFalse(pid_file.exists())

    def test_missing_lsof_preserves_running_metadata_for_backend_and_frontend(self):
        fixture, root, _launch_marker, overrides = self.make_lsof_failure_fixture()
        with fixture:
            runtime = root / ".tpm-dev"
            runtime.mkdir()
            backend_pid_file = runtime / "backend.pid"
            frontend_pid_file = runtime / "frontend.pid"
            backend_pid_file.write_text(f"{os.getpid()}\n")
            frontend_pid_file.write_text(f"{os.getpid()}\n")

            status = self.run_console("status", root=root, extra_environment=overrides)
            self.assertEqual(status.returncode, 0, status.stderr)
            self.assertEqual(status.stdout.count("inspection error"), 2)
            self.assertTrue(backend_pid_file.exists())
            self.assertTrue(frontend_pid_file.exists())

            stop = self.run_console("stop", root=root, extra_environment=overrides)
            self.assertNotEqual(stop.returncode, 0)
            self.assertIn("lsof is unavailable", stop.stderr)
            self.assertTrue(backend_pid_file.exists())
            self.assertTrue(frontend_pid_file.exists())
            os.kill(os.getpid(), 0)

    def test_lsof_operational_error_preserves_metadata_and_reports_unknown(self):
        fixture, root, _launch_marker, overrides = self.make_lsof_failure_fixture(
            operational_error=True
        )
        with fixture:
            runtime = root / ".tpm-dev"
            runtime.mkdir()
            pid_file = runtime / "backend.pid"
            pid_file.write_text(f"{os.getpid()}\n")

            status = self.run_console("status", root=root, extra_environment=overrides)
            self.assertEqual(status.returncode, 0, status.stderr)
            self.assertIn("Backend:  inspection error", status.stdout)
            self.assertTrue(pid_file.exists())

            stop = self.run_console("stop", root=root, extra_environment=overrides)
            self.assertNotEqual(stop.returncode, 0)
            self.assertIn("process inspection failed", stop.stderr)
            self.assertTrue(pid_file.exists())
            os.kill(os.getpid(), 0)

    def test_start_does_not_overwrite_metadata_when_inspection_is_unknown(self):
        fixture, root, launch_marker, overrides = self.make_lsof_failure_fixture(
            operational_error=True
        )
        with fixture:
            runtime = root / ".tpm-dev"
            runtime.mkdir()
            pid_file = runtime / "backend.pid"
            original_metadata = f"{os.getpid()}\n"
            pid_file.write_text(original_metadata)

            result = self.run_console("start", root=root, extra_environment=overrides)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("could not be inspected safely", result.stderr)
            self.assertEqual(pid_file.read_text(), original_metadata)
            self.assertFalse(launch_marker.exists())
            self.assertFalse((runtime / "frontend.pid").exists())
            os.kill(os.getpid(), 0)

    def test_stop_does_not_kill_pid_reused_after_term(self):
        fixture, root = self.make_repository_fixture()
        with fixture:
            result, signals, pid_file = self.run_stop_safety_scenario(
                root, "backend", 8000, 8000, scenario="reuse"
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(signals, ["4242"])
            self.assertNotIn("-KILL 4242", signals)
            self.assertFalse(pid_file.exists())

    def test_stop_waits_for_delayed_exit_after_kill_for_both_services(self):
        for service, port in (("backend", 8000), ("frontend", 5173)):
            with self.subTest(service=service):
                fixture, root = self.make_repository_fixture()
                with fixture:
                    result, signals, pid_file = self.run_stop_safety_scenario(
                        root, service, port, port, scenario="delayed-kill"
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(signals, ["4242", "-KILL 4242"])
                    self.assertFalse(pid_file.exists())
                    self.assertIn(f"{service} stopped", result.stdout)

    def test_unconfirmed_kill_preserves_metadata_and_has_no_false_success(self):
        for service, port in (("backend", 8000), ("frontend", 5173)):
            with self.subTest(service=service):
                fixture, root = self.make_repository_fixture()
                with fixture:
                    result, signals, pid_file = self.run_stop_safety_scenario(
                        root, service, port, port, scenario="timeout"
                    )
                    self.assertNotEqual(result.returncode, 0)
                    self.assertEqual(signals, ["4242", "-KILL 4242"])
                    self.assertTrue(pid_file.exists())
                    self.assertIn("could not be confirmed before the timeout", result.stderr)
                    self.assertNotIn(f"{service} stopped", result.stdout)

    def test_pid_reused_after_kill_is_not_signaled_as_original_process(self):
        fixture, root = self.make_repository_fixture()
        with fixture:
            result, signals, pid_file = self.run_stop_safety_scenario(
                root, "backend", 8000, 8000, scenario="reuse-after-kill"
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(signals, ["4242", "-KILL 4242"])
            self.assertFalse(pid_file.exists())

    def test_unrelated_port_takeover_is_reported_without_signaling_new_owner(self):
        fixture, root = self.make_repository_fixture()
        with fixture:
            result, signals, pid_file = self.run_stop_safety_scenario(
                root, "backend", 8000, 8000, scenario="port-taken"
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(signals, ["4242"])
            self.assertNotIn("9999", " ".join(signals))
            self.assertFalse(pid_file.exists())
            self.assertIn("port 8000 is now owned by another process", result.stderr)

    def test_post_kill_inspection_failure_preserves_metadata(self):
        fixture, root = self.make_repository_fixture()
        with fixture:
            result, signals, pid_file = self.run_stop_safety_scenario(
                root, "frontend", 5173, 5173, scenario="inspection-after-kill"
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(signals, ["4242", "-KILL 4242"])
            self.assertTrue(pid_file.exists())
            self.assertIn("process inspection failed", result.stderr)

    def test_controlled_fixture_start_status_stop_cycle(self):
        fixture, root = self.make_repository_fixture()
        with fixture:
            bin_directory = root / "fixture-bin"
            bin_directory.mkdir()
            backend_state = root / "backend-listener.pid"
            frontend_state = root / "frontend-listener.pid"
            python = root / ".venv/bin/python"
            python.parent.mkdir(parents=True)
            npm = bin_directory / "npm"
            node = bin_directory / "node"
            fake_ps = bin_directory / "ps"
            fake_lsof = bin_directory / "lsof"

            python.write_text(
                "#!/bin/sh\n"
                "if [ \"$1\" = \"-\" ]; then\n"
                f"    exec '{REPOSITORY_ROOT / '.venv/bin/python'}' \"$@\"\n"
                "fi\n"
                f"printf '%s\\n' \"$$\" > '{backend_state}'\n"
                "exec sleep 30\n"
            )
            npm.write_text(
                f"#!/bin/sh\nprintf '%s\\n' \"$$\" > '{frontend_state}'\n"
                "exec sleep 30\n"
            )
            node.write_text("#!/bin/sh\nexit 0\n")
            fake_ps.write_text(
                f"""#!/bin/sh
pid="$2"
field="$4"
backend_pid="$(cat '{backend_state}' 2>/dev/null)"
frontend_pid="$(cat '{frontend_state}' 2>/dev/null)"
if [ "$field" = "command=" ]; then
    if [ "$pid" = "$backend_pid" ]; then
        printf '%s\\n' '{python} -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8000'
    elif [ "$pid" = "$frontend_pid" ]; then
        printf '%s\\n' '{node} {root}/frontend/node_modules/vite/bin/vite.js --host 127.0.0.1 --port 5173'
    fi
else
    printf '1\\n'
fi
"""
            )
            fake_lsof.write_text(
                f"""#!/bin/sh
arguments="$*"
backend_pid="$(cat '{backend_state}' 2>/dev/null)"
frontend_pid="$(cat '{frontend_state}' 2>/dev/null)"
case "$arguments" in
    *-iTCP:8000*) [ -n "$backend_pid" ] && kill -0 "$backend_pid" 2>/dev/null && printf '%s\\n' "$backend_pid" ;;
    *-iTCP:5173*) [ -n "$frontend_pid" ] && kill -0 "$frontend_pid" 2>/dev/null && printf '%s\\n' "$frontend_pid" ;;
    *"-d cwd"*)
        case "$arguments" in
            *"-p $backend_pid"*) printf 'p%s\\nfcwd\\nn{root}\\n' "$backend_pid" ;;
            *"-p $frontend_pid"*) printf 'p%s\\nfcwd\\nn{root}/frontend\\n' "$frontend_pid" ;;
        esac
        ;;
    *"-d txt"*)
        case "$arguments" in
            *"-p $backend_pid"*) printf 'p%s\\nftxt\\nn{python}\\n' "$backend_pid" ;;
            *"-p $frontend_pid"*) printf 'p%s\\nftxt\\nn{node}\\n' "$frontend_pid" ;;
        esac
        ;;
esac
"""
            )
            for executable in (python, npm, node, fake_ps, fake_lsof):
                executable.chmod(0o755)
            (root / "frontend/.env.local").write_text(
                "VITE_API_BASE_URL=http://127.0.0.1:8000\n"
            )

            overrides = {
                "TPM_DEV_NODE_COMMAND": str(node),
                "TPM_DEV_NPM_COMMAND": str(npm),
                "TPM_DEV_PS_COMMAND": str(fake_ps),
                "TPM_DEV_LSOF_COMMAND": str(fake_lsof),
            }
            try:
                start = self.run_console(
                    "start", root=root, extra_environment=overrides
                )
                self.assertEqual(start.returncode, 0, start.stderr)
                status = self.run_console(
                    "status", root=root, extra_environment=overrides
                )
                self.assertEqual(status.returncode, 0, status.stderr)
                self.assertIn("Backend:  running", status.stdout)
                self.assertIn("Frontend: running", status.stdout)
                stop = self.run_console("stop", root=root, extra_environment=overrides)
                self.assertEqual(stop.returncode, 0, stop.stderr)
                self.assertFalse((root / ".tpm-dev/backend.pid").exists())
                self.assertFalse((root / ".tpm-dev/frontend.pid").exists())
            finally:
                for state_file in (backend_state, frontend_state):
                    if state_file.exists():
                        pid = int(state_file.read_text().strip())
                        try:
                            os.kill(pid, 15)
                        except ProcessLookupError:
                            pass

    def test_stop_does_not_kill_a_recorded_unrelated_process(self):
        fixture, root = self.make_repository_fixture()
        with fixture:
            result, signals, pid_file = self.run_stop_safety_scenario(
                root, "backend", 8000, 8000, scenario="mismatch"
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("did not match a console-owned service", result.stderr)
            self.assertEqual(signals, [])
            self.assertFalse(pid_file.exists())

    def test_release_check_returns_nonzero_and_summary_on_validation_failure(self):
        fixture, root = self.make_repository_fixture()
        with fixture:
            (root / ".gitignore").write_text("frontend/.env.local\n")
            result = self.run_console(
                "release-check",
                root=root,
                extra_environment={
                    "TPM_DEV_NODE_COMMAND": "definitely-missing-node",
                    "TPM_DEV_NPM_COMMAND": "definitely-missing-npm",
                },
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Release-check summary", result.stdout)
        self.assertIn("Release check failed", result.stderr)
        self.assertIn("backend-tests", result.stderr)
        self.assertIn("frontend-tests", result.stderr)
        self.assertIn("frontend-build", result.stderr)
        self.assertIn("git-status", result.stderr)
        self.assertNotIn("All required release checks passed", result.stdout)

    def test_committed_release_whitespace_check_passes_clean_range(self):
        fixture, root = self.make_repository_fixture()
        with fixture:
            self.prepare_committed_repository_fixture(root)
            subprocess.run(["git", "-C", str(root), "tag", "v0.7.0"], check=True)
            (root / "app/main.py").write_text("# clean change\n")
            self.commit_fixture_change(root)
            result = self.run_committed_whitespace_check(root)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("passed whitespace validation", result.stdout)

    def test_committed_release_whitespace_check_rejects_trailing_whitespace(self):
        fixture, root = self.make_repository_fixture()
        with fixture:
            self.prepare_committed_repository_fixture(root)
            subprocess.run(["git", "-C", str(root), "tag", "v0.7.0"], check=True)
            (root / "app/main.py").write_text("# trailing whitespace  \n")
            self.commit_fixture_change(root)
            result = self.run_committed_whitespace_check(root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("contain whitespace errors", result.stderr)
        self.assertIn("trailing whitespace", result.stderr)

    def test_committed_release_whitespace_check_rejects_conflict_markers(self):
        fixture, root = self.make_repository_fixture()
        with fixture:
            self.prepare_committed_repository_fixture(root)
            subprocess.run(["git", "-C", str(root), "tag", "v0.7.0"], check=True)
            (root / "app/main.py").write_text(
                "<<<<<<< ours\n# first\n=======\n# second\n>>>>>>> theirs\n"
            )
            self.commit_fixture_change(root)
            result = self.run_committed_whitespace_check(root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("contain whitespace errors", result.stderr)
        self.assertIn("leftover conflict marker", result.stderr)

    def test_committed_release_whitespace_check_rejects_invalid_base(self):
        fixture, root = self.make_repository_fixture()
        with fixture:
            self.prepare_committed_repository_fixture(root)
            result = self.run_committed_whitespace_check(root, "missing-release")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("is not a valid commit or tag", result.stderr)

    def test_release_check_does_not_report_success_after_whitespace_failure(self):
        fixture, root = self.make_repository_fixture()
        with fixture:
            self.prepare_committed_repository_fixture(root)
            result = self.run_console(
                "release-check",
                root=root,
                extra_environment={
                    "TPM_DEV_RELEASE_BASE": "missing-release",
                    "TPM_DEV_NODE_COMMAND": "definitely-missing-node",
                    "TPM_DEV_NPM_COMMAND": "definitely-missing-npm",
                },
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("git-diff-check", result.stderr)
        self.assertNotIn("All required release checks passed", result.stdout)

    def test_shell_implementation_contains_no_broad_process_kill(self):
        forbidden = ("pkill", "killall")
        for shell_file in SHELL_FILES:
            contents = shell_file.read_text()
            for command in forbidden:
                self.assertNotIn(command, contents, f"{command} found in {shell_file}")

    def test_all_shell_files_pass_bash_syntax_validation(self):
        for shell_file in SHELL_FILES:
            result = subprocess.run(
                ["/bin/bash", "-n", str(shell_file)],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(result.returncode, 0, f"{shell_file}: {result.stderr}")


if __name__ == "__main__":
    unittest.main()
