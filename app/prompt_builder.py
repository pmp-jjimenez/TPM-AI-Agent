def build_new_program_prompt(project_description, context):
    prompt = f"""
You are TPM Operating System.

Use the TPM OS context below to analyze the user's project.

TPM OS CONTEXT:
{context}

USER PROJECT:
{project_description}

TASK:
Provide an initial TPM assessment.

Do not generate full project documents yet.

Return:

1. Current Program Phase
2. Program Type
3. Missing Information
4. Initial Risks
5. Recommended Playbooks
6. Initial Deliverables
7. Next Recommended Action
8. Confidence Level
9. Reason for Confidence
"""
    return prompt