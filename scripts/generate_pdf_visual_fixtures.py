"""Generate deterministic, review-only PDF fixtures under the ignored reports tree."""

from datetime import date
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))

from artifact_design import DEFAULT_ARTIFACT_DESIGN_SYSTEM
from artifact_renderer import RenderContext
from executive_artifact import compose_executive_status_artifact
from executive_report import ReportMetadataInput, build_executive_report_view_model
from pdf_reportlab_renderer import ReportLabPdfRenderer


OUTPUT_DIR = ROOT / "reports" / "pdf-visual-fixtures"
METADATA = ReportMetadataInput(
    report_date=date(2026, 7, 23),
    generated_at="2026-07-23T12:00:00-06:00",
    locale="en-US",
    timezone="America/Mexico_City",
    report_id="visual-review-2026-07-23",
)
CONTEXT = RenderContext(
    "en-US",
    deterministic_test_mode=True,
    title="Executive Status Report",
    author="TPM Operating System",
    creator="TPM Operating System",
    producer="ReportLab 5.0.0",
)


def base_program(**overrides):
    value = {
        "program_id": "visual-review",
        "program_name": "Executive Artifact Visual Review",
        "description": "Deterministic visual review fixture.",
        "customer": "Example Customer",
        "phase": "Execution",
        "health": "Green",
        "confidence": "High",
        "risks": [],
        "issues": [],
        "dependencies": [],
        "decisions": [],
        "next_actions": [],
        "relationships": [],
        "metadata": {"updated_at": "2026-07-22T12:00:00+00:00"},
    }
    value.update(overrides)
    return value


def scenarios():
    long_text = "Long executive evidence wraps safely across pages. " * 40
    return {
        "01-sparse": {
            "program_id": "sparse",
            "risks": [],
            "issues": [],
            "dependencies": [],
            "decisions": [],
            "next_actions": [],
        },
        "02-healthy-compact": base_program(
            risks=[{"description": "Monitored delivery exposure", "status": "monitoring"}],
            next_actions=[{"description": "Confirm weekly readiness", "priority": "medium"}],
        ),
        "03-warning": base_program(
            health="Yellow",
            confidence="Medium",
            risks=[{"description": "Vendor timeline", "priority": "high"}],
        ),
        "04-critical": base_program(
            health="Red",
            confidence="Low",
            issues=[{"description": "Production access blocked", "status": "blocked", "severity": "critical"}],
        ),
        "05-long-multipage": base_program(
            health="Yellow",
            risks=[
                {"description": f"Long risk {index}", "priority": "high", "mitigation_plan": long_text}
                for index in range(10)
            ],
        ),
        "06-missing-data": base_program(
            program_name=None,
            customer=None,
            phase=None,
            health=None,
            confidence=None,
            risks=[{"description": "Risk without optional fields"}],
        ),
        "07-special-characters": base_program(
            program_name="Programa México & España <2026>\nLínea ejecutiva",
            customer="Compañía Ágil",
            risks=[{"description": "Riesgo & control <pendiente>", "mitigation_plan": "Revisión áéíóú"}],
        ),
        "08-omitted-records": base_program(
            health="Yellow",
            risks=[{"description": f"Ordered risk {index}", "priority": "high"} for index in range(14)],
        ),
    }


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    renderer = ReportLabPdfRenderer()
    for name, source in scenarios().items():
        model = build_executive_report_view_model(source, report_metadata=METADATA)
        artifact = compose_executive_status_artifact(model)
        result = renderer.render(
            artifact,
            design_system=DEFAULT_ARTIFACT_DESIGN_SYSTEM,
            render_context=CONTEXT,
        )
        destination = OUTPUT_DIR / f"{name}.pdf"
        destination.write_bytes(result.payload)
        print(destination.relative_to(ROOT))


if __name__ == "__main__":
    main()
