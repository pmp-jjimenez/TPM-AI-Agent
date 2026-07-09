from engine import analyze_new_program
def route(option):

    if option == "1":
        print("\n=== NEW PROGRAM ===\n")

        project = input("Describe your project:\n\n")

        print("\n----------------------------------")
        print("Project captured successfully.")
        print("----------------------------------")

        print(f"\nProject Description:\n{project}")
        analyze_new_program(project)

    elif option == "2":
        print("\nActive Program selected.")

    elif option == "3":
        print("\nMajor Incident selected.")

    elif option == "4":
        print("\nExecutive Review selected.")

    elif option == "5":
        print("\nOperational Readiness selected.")

    elif option == "0":
        print("\nGoodbye!")

    else:
        print("\nInvalid option.")