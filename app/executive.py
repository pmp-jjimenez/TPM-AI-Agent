from datetime import datetime
from pathlib import Path


REPORT_DIR = Path("reports/executive")


def generate_executive_report(program):

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    report = f"""# Executive Status Report

Generated:
{datetime.now().strftime("%Y-%m-%d %H:%M")}

--------------------------------------------------

Program

{program['program_name']}

Current Phase

{program['phase']}

Overall Health

{program['health']}

Confidence

{program['confidence']}

--------------------------------------------------

Executive Summary

Program currently in {program['phase']}.

Current health is {program['health']}.

Open Risks: {len(program['risks'])}

Open Issues: {len(program['issues'])}

Pending Decisions: {len(program['decisions'])}

Open Actions: {len(program['next_actions'])}

--------------------------------------------------

Top Risks

"""

    if program["risks"]:

        for risk in program["risks"]:

            report += f"- {risk['description']}\n"

    else:

        report += "- No risks registered.\n"

    report += """

--------------------------------------------------

Recommended Executive Actions

"""

    if len(program["risks"]) > 0:

        report += "- Review mitigation plan for open risks.\n"

    if len(program["decisions"]) > 0:

        report += "- Close pending executive decisions.\n"

    if len(program["next_actions"]) > 0:

        report += "- Verify execution of committed actions.\n"

    if (
        len(program["risks"]) == 0
        and len(program["decisions"]) == 0
        and len(program["next_actions"]) == 0
    ):

        report += "- Continue program as planned.\n"

    filename = REPORT_DIR / f"{program['program_id']}_executive_status.md"

    with open(filename, "w", encoding="utf-8") as file:

        file.write(report)

    return filename