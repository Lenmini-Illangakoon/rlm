"""Accidental live-call prevention, NOT an adversarial Python security sandbox."""

import importlib.abc
import sys
from pathlib import Path

INSTALLED = False
BLOCKED = {"openai", "anthropic", "google.genai", "portkey_ai", "httpx", "requests"}


class ProviderBlocker(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if (fullname.startswith("rlm.clients.") and fullname != "rlm.clients.base_lm") or any(
            fullname == name or fullname.startswith(name + ".") for name in BLOCKED
        ):
            raise ImportError(f"Offline preparation forbids provider import: {fullname}")
        return None


def audit(event: str, args: tuple) -> None:
    if event in {"socket.connect", "socket.bind"}:
        address = args[1]
        if not isinstance(address, tuple) or address[0] != "127.0.0.1":
            raise PermissionError("Offline runner permits only literal IPv4 loopback sockets")
    if event == "socket.getaddrinfo" and args[0] not in {"127.0.0.1", None}:
        raise PermissionError("Offline runner forbids remote DNS")
    if event == "open" and isinstance(args[0], (str, bytes)):
        name = str(args[0]).replace("\\", "/").lower()
        base = Path(name).name
        if base == ".env" or base.startswith(".env.") or any(
            part in name for part in ("/.aws/", "/.ssh/", "/.codex/auth", "/credentials")
        ):
            raise PermissionError("Offline runner forbids credential-file access")


def install() -> None:
    global INSTALLED
    if INSTALLED:
        return
    if "rlm" in sys.modules:
        raise RuntimeError("Offline guard must be installed before importing rlm")
    import dotenv

    # The pinned package calls load_dotenv at import. Prevent discovery and reads.
    dotenv.load_dotenv = lambda *args, **kwargs: False
    sys.meta_path.insert(0, ProviderBlocker())
    sys.addaudithook(audit)
    INSTALLED = True
