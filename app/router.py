from engine import analyze_new_program
from memory import create_program, list_programs
from persona_routing import calculate_persona_routing, display_persona_routing
from workspace import open_workspace


def route_and_display_personas(
    menu_mode,
    workflow_name,
    user_request=None,
    program=None,
    extra_signals=None,
):
    routing, fallback_used = calculate_persona_routing(
        menu_mode=menu_mode,
        workflow_name=workflow_name,
        user_request=user_request,
        program=program,
        extra_signals=extra_signals,
    )
    display_persona_routing(routing, fallback_used=fallback_used)
    return routing


def route(option):

    if option == "1":

        print("\n=== NEW PROGRAM ===\n")

        project = input("Describe your project:\n\n")

        if not project.strip():
            print("Project description required.")
            return

        program_name = input("\nProgram Name:\n\n")

        if not program_name.strip():
            print("Program name required.")
            return

        program = create_program(program_name, project)

        print("\nProgram created successfully.\n")

        persona_routing = route_and_display_personas(
            menu_mode="Start New Program",
            workflow_name="program_initiation",
            user_request=project,
            program=program,
            extra_signals=["new program", "initiation"],
        )

        analyze_new_program(project, persona_routing=persona_routing)

    elif option == "2":

        programs = list_programs()

        if not programs:
            print("\nNo programs available.")
            return

        print("\n========== ACTIVE PROGRAMS ==========\n")

        for index, program in enumerate(programs, start=1):

            print(
                f"{index}. {program['program_name']} | {program['phase']} | {program['health']}"
            )

        selection = input("\nSelect program number:\n\n")

        try:

            selected = programs[int(selection) - 1]

        except:

            print("Invalid selection.")
            return

        route_and_display_personas(
            menu_mode="Manage Active Program",
            workflow_name="active_program_workspace",
            user_request="Manage active program workspace",
            program=selected,
            extra_signals=["active program", "workspace"],
        )

        open_workspace(selected["program_id"])

    elif option == "3":

        route_and_display_personas(
            menu_mode="Major Incident",
            workflow_name="major_incident",
            user_request="Major incident response",
            extra_signals=["incident", "major incident"],
        )

        print("\nMajor Incident Mode")

    elif option == "4":

        route_and_display_personas(
            menu_mode="Executive Review",
            workflow_name="executive_review",
            user_request="Executive review",
            extra_signals=["executive", "review"],
        )

        print("\nExecutive Review")

    elif option == "5":

        route_and_display_personas(
            menu_mode="Operational Readiness",
            workflow_name="operational_readiness",
            user_request="Operational readiness review",
            extra_signals=["operational readiness", "readiness"],
        )

        print("\nOperational Readiness")

    elif option == "0":

        print("\nGoodbye")

    else:

        print("\nInvalid option")
