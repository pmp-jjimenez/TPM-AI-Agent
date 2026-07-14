def main():
    print("TPM OPERATING SYSTEM")
    print("Version: 0.2-dev")
    print("Program Intelligence for Technical Program Managers")

    print("\nSelect an option:\n")

    print("1. Start a New Program")
    print("2. Manage an Active Program")
    print("3. Major Incident")
    print("4. Executive Review")
    print("5. Operational Readiness")
    print("0. Exit")

    from router import route

    option = input("\nChoose an option: ")

    route(option)

if __name__ == "__main__":
    main()
