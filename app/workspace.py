from datetime import datetime

from memory import load_program, save_program
from executive import generate_executive_report
from schema import generate_item_id
from program_domain import create_action, create_dependency, create_issue, create_risk, utc_timestamp


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
    print("Dependencies:", len(program["dependencies"]))
    print("Decisions   :", len(program["decisions"]))
    print("Next Actions:", len(program["next_actions"]))


def add_risk(program):
    risk = input("\nDescribe the risk:\n\n")

    if not risk.strip():
        print("Risk cannot be empty.")
        return

    program["risks"].append(create_risk(
        risk,
        lifecycle_phase=program.get("phase"),
    ).to_dict())

    save_program(program)
    print("\nRisk added successfully.")


def add_issue(program):
    issue = input("\nIssue description:\n\n").strip()

    if not issue:
        print("Issue cannot be empty.")
        return

    owner = input("\nIssue owner:\n\n").strip()

    if not owner:
        print("Issue owner cannot be empty.")
        return

    while True:
        due_date = input("\nDue date (YYYY-MM-DD):\n\n").strip()

        try:
            datetime.strptime(due_date, "%Y-%m-%d")
            break
        except ValueError:
            print("Invalid date. Use YYYY-MM-DD.")

    program["issues"].append(create_issue(
        issue, owner=owner, due_date=due_date,
        lifecycle_phase=program.get("phase"),
    ).to_dict())

    save_program(program)
    print("\nIssue added successfully.")
    input("\nPress Enter to return to the workspace...")


def add_dependency(program):
    title = input("\nDependency description:\n\n").strip()
    if not title:
        print("Dependency cannot be empty.")
        return
    owner = input("\nDependency owner:\n\n").strip()
    if not owner:
        print("Dependency owner cannot be empty.")
        return
    dependency_type = input(
        "\nDependency type (internal, external, vendor, customer, technical, business):\n\n"
    ).strip().lower()
    if dependency_type not in {"internal", "external", "vendor", "customer", "technical", "business"}:
        print("Invalid dependency type.")
        return
    program["dependencies"].append(create_dependency(
        title, owner=owner, dependency_type=dependency_type,
        lifecycle_phase=program.get("phase"),
    ).to_dict())
    save_program(program)
    print("\nDependency added successfully.")


def get_open_issues(program):
    return [
        issue for issue in program["issues"]
        if issue.get("status") == "open"
    ]


def display_open_issues(open_issues):
    for number, issue in enumerate(open_issues, start=1):
        owner_value = issue.get("owner")
        owner = owner_value.get("display_name") if isinstance(owner_value, dict) else owner_value
        owner = owner or "Not assigned"
        due_date = issue.get("due_date") or "Not defined"

        print(f"\n{number}. {issue['title']}")
        print(f"   Owner   : {owner}")
        print(f"   Due date: {due_date}")
        print(f"   Status  : {issue['status']}")


def list_open_issues(program):
    open_issues = get_open_issues(program)

    if not open_issues:
        print("\nThere are no open issues.")
        input("\nPress Enter to return to the workspace...")
        return

    print("\nOpen Issues:")
    display_open_issues(open_issues)
    input("\nPress Enter to return to the workspace...")


def close_issue(program):
    open_issues = get_open_issues(program)

    if not open_issues:
        print("\nThere are no open issues to close.")
        return

    print("\nOpen Issues:")
    display_open_issues(open_issues)

    selection = input("\nWhich issue do you want to close?\n\n").strip()

    if not selection.isdigit():
        print("Invalid issue number.")
        input("\nPress Enter to return to the workspace...")
        return

    selected_number = int(selection)

    if selected_number < 1 or selected_number > len(open_issues):
        print("Invalid issue number.")
        input("\nPress Enter to return to the workspace...")
        return

    selected_object_id = open_issues[selected_number - 1]["object_id"]
    resolution_summary = input("\nResolution summary:\n\n").strip()
    if not resolution_summary:
        print("Resolution summary cannot be empty.")
        input("\nPress Enter to return to the workspace...")
        return

    issue = next(
        (item for item in program["issues"] if item.get("object_id") == selected_object_id),
        None,
    )
    if issue is None:
        print("Selected issue is no longer available.")
        return
    now = utc_timestamp()
    issue["status"] = "closed"
    issue["resolution_summary"] = resolution_summary
    issue["resolved_at"] = now
    issue["audit"]["updated_at"] = now

    save_program(program)
    print("\nIssue closed successfully.")
    input("\nPress Enter to return to the workspace...")


def add_decision(program):
    decision = input("\nDescribe the decision:\n\n")

    if not decision.strip():
        print("Decision cannot be empty.")
        return

    program["decisions"].append({
        "decision_id": generate_item_id("decision"),
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

    program["next_actions"].append(create_action(
        action,
        lifecycle_phase=program.get("phase"),
    ).to_dict())

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


def create_executive_report(program):
    report_path = generate_executive_report(program)

    print("\nExecutive report generated successfully.")
    print(f"Saved to: {report_path}")


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
        print("5. Generate Executive Report")
        print("6. Add Issue")
        print("7. List Open Issues")
        print("8. Close Issue")
        print("9. Add Dependency")
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
        elif option == "5":
            create_executive_report(program)
        elif option == "6":
            add_issue(program)
        elif option == "7":
            list_open_issues(program)
        elif option == "8":
            close_issue(program)
        elif option == "9":
            add_dependency(program)
        elif option == "0":
            print("\nExiting workspace.")
            break
        else:
            print("Invalid option.")
