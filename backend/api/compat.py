"""Minimal import bridge to the existing script-oriented application modules."""

import sys
from pathlib import Path


APP_DIR = Path(__file__).resolve().parents[2] / "app"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from application_version import APPLICATION_VERSION  # noqa: E402
import memory  # noqa: E402


__all__ = ["APPLICATION_VERSION", "memory"]
