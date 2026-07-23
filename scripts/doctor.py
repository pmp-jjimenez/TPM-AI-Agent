#!/usr/bin/env python3
import importlib
import os
import shutil
import sys
from pathlib import Path


REPO_ROOT = Path.cwd()
REQUIRED_DIRECTORIES = [
    "app",
    "data",
    "data/programs",
    "docs",
    "instructions",
    "knowledge",
    "playbooks",
    "templates",
    "tests",
]
CORE_MODULES = [
    "artifact_renderer",
    "executive_report",
    "font_assets",
    "memory",
    "prompt_builder",
    "context_loader",
    "executive",
    "workspace",
    "router",
    "engine",
    "llm",
]


class Doctor:
    def __init__(self):
        self.results = []

    def pass_(self, message):
        self.results.append(("PASS", message))
        print(f"[PASS] {message}")

    def warn(self, message):
        self.results.append(("WARN", message))
        print(f"[WARN] {message}")

    def fail(self, message):
        self.results.append(("FAIL", message))
        print(f"[FAIL] {message}")

    def has_failures(self):
        return any(status == "FAIL" for status, _ in self.results)

    def summary(self):
        counts = {"PASS": 0, "WARN": 0, "FAIL": 0}
        for status, _ in self.results:
            counts[status] += 1

        print("\nSummary")
        print(f"[PASS] {counts['PASS']}")
        print(f"[WARN] {counts['WARN']}")
        print(f"[FAIL] {counts['FAIL']}")

        if counts["FAIL"]:
            print("\nOverall: FAIL")
        elif counts["WARN"]:
            print("\nOverall: PASS with warnings")
        else:
            print("\nOverall: PASS")


def is_writable_directory(path):
    return path.is_dir() and os.access(str(path), os.W_OK)


def could_create_directory(path):
    parent = path.parent
    return parent.is_dir() and os.access(str(parent), os.W_OK)


def check_python_version(doctor):
    version = sys.version_info
    label = f"{version.major}.{version.minor}.{version.micro}"
    if version >= (3, 9):
        doctor.pass_(f"Python version is {label}.")
    else:
        doctor.fail(f"Python version is {label}; Python 3.9 or newer is required.")


def check_repo_root(doctor):
    markers = [
        REPO_ROOT / "app" / "main.py",
        REPO_ROOT / "docs" / "PRODUCT_VISION.md",
        REPO_ROOT / "docs" / "ARCHITECTURE.md",
    ]
    if all(path.exists() for path in markers):
        doctor.pass_("Current directory appears to be the repository root.")
    else:
        doctor.fail("Current directory does not appear to be the repository root.")


def check_required_directories(doctor):
    for relative_path in REQUIRED_DIRECTORIES:
        path = REPO_ROOT / relative_path
        if path.is_dir():
            doctor.pass_(f"Required directory exists: {relative_path}/")
        else:
            doctor.fail(f"Required directory is missing: {relative_path}/")


def check_imports(doctor):
    app_path = str(REPO_ROOT / "app")
    if app_path not in sys.path:
        sys.path.insert(0, app_path)

    for module_name in CORE_MODULES:
        try:
            importlib.import_module(module_name)
            doctor.pass_(f"Imported app module: {module_name}")
        except Exception as error:
            doctor.fail(f"Could not import app module {module_name}: {error}")


def check_programs_directory(doctor):
    path = REPO_ROOT / "data" / "programs"
    if not path.is_dir():
        doctor.fail("data/programs/ does not exist.")
    elif is_writable_directory(path):
        doctor.pass_("data/programs/ exists and is writable.")
    else:
        doctor.fail("data/programs/ exists but is not writable.")


def check_pdf_backend(doctor):
    try:
        from pdf_reportlab_renderer import EXPECTED_REPORTLAB_VERSION, inspect_pdf_backend

        readiness = inspect_pdf_backend()
    except Exception:
        doctor.fail("PDF backend readiness could not be inspected safely.")
        return

    if not readiness.reportlab_available:
        doctor.fail(
            f"ReportLab is not installed; install repository dependencies "
            f"(expected {EXPECTED_REPORTLAB_VERSION})."
        )
    elif readiness.installed_version != EXPECTED_REPORTLAB_VERSION:
        doctor.fail(
            f"ReportLab version is {readiness.installed_version or 'unknown'}; "
            f"expected {EXPECTED_REPORTLAB_VERSION}."
        )
    else:
        doctor.pass_(f"ReportLab version is {EXPECTED_REPORTLAB_VERSION}.")

    if readiness.font_assets_valid:
        doctor.pass_("Bundled Inter 4.1 font assets passed checksum validation.")
    else:
        doctor.fail("Bundled Inter 4.1 font assets are missing or invalid.")


def check_runtime_directory(doctor, relative_path):
    path = REPO_ROOT / relative_path
    if path.is_dir():
        if is_writable_directory(path):
            doctor.pass_(f"{relative_path}/ exists and is writable.")
        else:
            doctor.fail(f"{relative_path}/ exists but is not writable.")
    elif could_create_directory(path):
        doctor.pass_(f"{relative_path}/ does not exist but can be created from the repository root.")
    else:
        doctor.fail(f"{relative_path}/ does not exist and cannot be created from the repository root.")


def check_gemini_key(doctor):
    if os.getenv("GEMINI_API_KEY"):
        doctor.pass_("GEMINI_API_KEY is configured.")
    else:
        doctor.warn("GEMINI_API_KEY is not configured; AI calls will not work.")


def check_command(doctor, command_name, required):
    if shutil.which(command_name):
        doctor.pass_(f"{command_name} is available.")
    elif required:
        doctor.fail(f"{command_name} is not available on PATH.")
    else:
        doctor.warn(f"{command_name} is not available on PATH.")


def main():
    doctor = Doctor()

    check_python_version(doctor)
    check_repo_root(doctor)
    check_required_directories(doctor)
    check_imports(doctor)
    check_pdf_backend(doctor)
    check_programs_directory(doctor)
    check_runtime_directory(doctor, "reports")
    check_runtime_directory(doctor, "sessions")
    check_gemini_key(doctor)
    check_command(doctor, "git", required=True)
    check_command(doctor, "codex", required=False)
    check_command(doctor, "gh", required=False)

    doctor.summary()
    return 1 if doctor.has_failures() else 0


if __name__ == "__main__":
    sys.exit(main())
