# Backend

This directory reserves the backend boundary for TPM Operating System.

The existing Python backend remains in `../app/` during the product-foundation sprint. Keeping it there preserves current module imports, test discovery, and the `python3 app/main.py` CLI entry point without compatibility shims or business-logic changes.

Future backend work may introduce an API and service-oriented packaging here through a dedicated, backward-compatible migration. No API framework or new runtime is implemented in this directory today.
