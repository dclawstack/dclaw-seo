"""Export the OpenAPI schema to backend/openapi.json.

Usage: python scripts/export_openapi.py
"""

import json
from pathlib import Path

from app.main import app


def main() -> None:
    out = Path(__file__).resolve().parent.parent / "openapi.json"
    out.write_text(json.dumps(app.openapi(), indent=2))
    print(f"Wrote {out} ({len(app.openapi()['paths'])} paths)")


if __name__ == "__main__":
    main()
