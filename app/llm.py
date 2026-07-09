import json
import os
import urllib.request


def generate_response(prompt):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return "ERROR: GEMINI_API_KEY is not configured."

    model = "gemini-3.1-flash-lite"
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={api_key}"
    )

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(request) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as error:
        return f"ERROR calling Gemini API: {error}"