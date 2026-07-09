from memory import load_program, save_program


def show_summary(program):
    print("\n====================================")
    print("        PROGRAM WORKSPACE")
    print("====================================")
    print(f"Name       : {program['program_name']}")
    print(f"Phase      : {program['phase']}")
    print(f"Health     : {program['health']}")
    print(f"Confidence : {program['confidence']}")
    print("\nRisks       :", len(program["risks"]))
    print("Issues      :", len(program["issues"]))
    print("Decisions   :", len(program["decisions"]))
    print("Next Actions:", len(program["next_actions"]))


def add_risk(program):
    risk = input("\nDescribe the risk:\n\n")

    if not risk.strip():
        print("Risk cannot be empty.")
        return

    program["risks"].append({
        "description": risk,
        "status": "Open"
    })

    save_program(program)
    print("\nRisk added successfully.")


def add_decision(program):
    decision = input("\nDescribe the decision:\n\n")

    if not decision.strip():
        print("Decision cannot be empty.")
        return

    program["decisions"].append({
        "description": decision,
        "status": "Open"
    })

    save_program(program)
    print("\nDecision added successfully.")


def add_action(program):
    action = input("\nDescribe the next action:\n\n")

    if not action.strip():
        print("Action cannot be empty.")
        return

    program["next_actions"].append({
        "description": action,
        "status": "Open"
    })

    save_program(program)
    print("\nAction added successfully.")


def update_health(program):
    print("\nSelect health:")
    print("1. Green")
    print("2. Yellow")
    print("3. Red")

    option = input("\nChoose option:\n\n")

    if option == "1":
        program["health"] = "Green"
    elif option == "2":
        program["health"] = "Yellow"
    elif option == "3":
        program["health"] = "Red"
    else:
        print("Invalid option.")
        return

    save_program(program)
    print("\nHealth updated successfully.")


def open_workspace(program_id):
    program = load_program(program_id)

    if not program:
        print("Program not found.")
        return

    while True:
        show_summary(program)

        print("\nOptions:")
        print("1. Add Risk")
        print("2. Add Decision")
        print("3. Add Next Action")
        print("4. Update Health")
        print("0. Exit Workspace")

        option = input("\nChoose an option:\n\n")

        if option == "1":
            add_risk(program)
        elif option == "2":
            add_decision(program)
        elif option == "3":
            add_action(program)
        elif option == "4":
            update_health(program)
        elif option == "0":
            print("\nExiting workspace.")
            break
        else:
            print("Invalid option.")