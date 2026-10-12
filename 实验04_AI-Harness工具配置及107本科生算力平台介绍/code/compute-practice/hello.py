"""A standard-library-only program for the first GUI CPU job."""

import json
from pathlib import Path
import platform
import socket
import sys


def main():
    result = {
        "message": "hello from computing platform",
        "python": sys.version.split()[0],
        "executable": sys.executable,
        "cwd": str(Path.cwd()),
        "node": socket.gethostname(),
        "system": platform.system(),
    }
    output = Path("outputs/hello")
    output.mkdir(parents=True, exist_ok=True)
    (output / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2), flush=True)
    print("saved outputs/hello/result.json", flush=True)


if __name__ == "__main__":
    main()
