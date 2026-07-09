from engine import analyze_new_program
from memory import create_program, list_programs
from workspace import open_workspace


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

        create_program(program_name, project)

        print("\nProgram created successfully.\n")

        analyze_new_program(project)

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

        open_workspace(selected["program_id"])

    elif option == "3":

        print("\nMajor Incident Mode")

    elif option == "4":

        print("\nExecutive Review")

    elif option == "5":

        print("\nOperational Readiness")

    elif option == "0":

        print("\nGoodbye")

    else:

        print("\nInvalid option")