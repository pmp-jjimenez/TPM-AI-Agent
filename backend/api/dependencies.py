"""Dependency boundaries between HTTP transport and existing application services."""

from typing import Any, Dict, List, Optional

from backend.api.compat import memory


class ProgramReader:
    """Read-only adapter over the existing program persistence service."""

    def list_programs(self) -> List[Dict[str, Any]]:
        return memory.list_programs()

    def load_program(self, program_id: str) -> Optional[Dict[str, Any]]:
        return memory.load_program(program_id)


_program_reader = ProgramReader()


def get_program_reader() -> ProgramReader:
    return _program_reader
