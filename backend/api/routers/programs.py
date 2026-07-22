import logging

from fastapi import APIRouter, Depends

from backend.api.dependencies import (
    ProgramReader,
    get_intelligence_service,
    get_program_reader,
)
from backend.api.errors import APIError
from backend.api.models import IntelligenceResponse


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/programs", tags=["programs"])


@router.get("")
def get_programs(reader: ProgramReader = Depends(get_program_reader)):
    try:
        return reader.list_programs()
    except Exception as error:
        logger.exception("Unable to list programs", exc_info=error)
        raise APIError(
            500,
            "program_persistence_error",
            "Programs could not be loaded.",
        ) from error


@router.get("/{programId}")
def get_program(programId: str, reader: ProgramReader = Depends(get_program_reader)):
    try:
        program = reader.load_program(programId)
    except Exception as error:
        logger.exception("Unable to load program %r", programId, exc_info=error)
        raise APIError(
            500,
            "program_persistence_error",
            "The program could not be loaded.",
        ) from error

    if program is None:
        raise APIError(
            404,
            "program_not_found",
            f"Program '{programId}' was not found.",
        )

    return program


@router.get("/{programId}/intelligence", response_model=IntelligenceResponse, response_model_exclude_none=True)
def get_program_intelligence(
    programId: str,
    reader: ProgramReader = Depends(get_program_reader),
    service=Depends(get_intelligence_service),
):
    try:
        program = reader.load_program(programId)
    except Exception as error:
        logger.exception("Unable to load program %r for intelligence", programId, exc_info=error)
        raise APIError(
            500,
            "program_persistence_error",
            "The program could not be loaded.",
        ) from error

    if program is None:
        raise APIError(
            404,
            "program_not_found",
            f"Program '{programId}' was not found.",
        )

    try:
        return service.generate(program)
    except Exception as error:
        logger.exception("Unable to generate intelligence for program %r", programId, exc_info=error)
        raise APIError(
            500,
            "intelligence_generation_error",
            "Workspace intelligence could not be generated.",
        ) from error
