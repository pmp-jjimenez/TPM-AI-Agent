from context_loader import load_core_context
from prompt_builder import build_new_program_prompt
from llm import generate_response


def analyze_new_program(project_description, persona_routing=None):

    if not project_description.strip():
        print("\nERROR: Project description cannot be empty.")
        return

    context = load_core_context()

    print(f"\nLoaded TPM OS context: {len(context)} characters\n")

    prompt = build_new_program_prompt(
        project_description,
        context,
        persona_routing=persona_routing
    )

    print("AI-ready prompt created.")
    print(f"Prompt length: {len(prompt)} characters\n")

    with open("sessions/last_prompt.md", "w", encoding="utf-8") as file:
        file.write(prompt)

    print("Prompt saved to sessions/last_prompt.md")

    print("\nCalling Gemini...\n")

    ai_response = generate_response(prompt)

    print("\n===== TPM OS AI RESPONSE =====\n")

    print(ai_response)

    with open("sessions/last_response.md", "w", encoding="utf-8") as file:
        file.write(ai_response)

    print("\nAI response saved to sessions/last_response.md")
