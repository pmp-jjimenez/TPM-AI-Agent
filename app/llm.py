import json
import logging
import os
import socket
import urllib.error
import urllib.request


GEMINI_MODEL = "gemini-3.1-flash-lite"
GEMINI_TIMEOUT_SECONDS = 20
logger = logging.getLogger(__name__)


class ProviderExecutionError(RuntimeError):
    """Sanitized failure from the configured model-provider boundary."""

    def __init__(self, kind):
        super().__init__(kind)
        self.kind = kind


def execute_provider(prompt, timeout=GEMINI_TIMEOUT_SECONDS):
    """Execute one Gemini request or raise a classified, sanitized error."""
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ProviderExecutionError("missing_configuration")

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_MODEL}:generateContent?key={api_key}"
    )
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw_response = response.read().decode("utf-8")
    except (TimeoutError, socket.timeout) as error:
        logger.warning("Gemini request timed out")
        raise ProviderExecutionError("timeout") from error
    except urllib.error.HTTPError as error:
        logger.warning("Gemini provider returned HTTP status %s", error.code)
        raise ProviderExecutionError("provider_failure") from error
    except (urllib.error.URLError, OSError) as error:
        logger.warning("Gemini transport failed")
        raise ProviderExecutionError("transport_failure") from error

    try:
        result = json.loads(raw_response)
        text = result["candidates"][0]["content"]["parts"][0]["text"]
    except (json.JSONDecodeError, KeyError, IndexError, TypeError) as error:
        logger.warning("Gemini returned an unsupported response shape")
        raise ProviderExecutionError("malformed_provider_response") from error

    if not isinstance(text, str) or not text.strip():
        logger.warning("Gemini returned an empty response")
        raise ProviderExecutionError("empty_response")
    return text


def generate_response(prompt):
    try:
        return execute_provider(prompt)
    except ProviderExecutionError as error:
        if error.kind == "missing_configuration":
            return "ERROR: GEMINI_API_KEY is not configured."
        return f"ERROR calling Gemini API: {error.kind}"
