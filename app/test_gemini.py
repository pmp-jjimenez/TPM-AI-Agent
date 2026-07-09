from llm import generate_response

prompt = "You are a friendly AI. Say hello in one short sentence."

response = generate_response(prompt)

print("\n===== GEMINI RESPONSE =====\n")
print(response)