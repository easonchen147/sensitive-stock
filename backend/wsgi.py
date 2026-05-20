from __future__ import annotations

import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent
backend_root_str = str(BACKEND_ROOT)
if backend_root_str not in sys.path:
    sys.path.insert(0, backend_root_str)


def _create_application():
    from app import create_app

    return create_app()


application = _create_application()


if __name__ == "__main__":
    application.run(host="0.0.0.0", port=5000, debug=True)
