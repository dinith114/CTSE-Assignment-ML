"""Local Ollama client utility for agent reasoning."""

from typing import Optional
import subprocess
import shutil
import os


def _resolve_ollama_executable() -> Optional[str]:
    """Find the Ollama executable on PATH or in common Windows install locations."""
    executable = shutil.which("ollama")
    if executable:
        return executable

    candidates = [
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Ollama", "ollama.exe"),
        os.path.join(os.environ.get("ProgramFiles", ""), "Ollama", "ollama.exe"),
        os.path.join(os.environ.get("ProgramFiles(x86)", ""), "Ollama", "ollama.exe"),
    ]
    for candidate in candidates:
        if candidate and os.path.exists(candidate):
            return candidate
    return None


def run_ollama(prompt: str, model: str = "llama3.2:3b", timeout: int = 30) -> Optional[str]:
    """
    Query a locally running Ollama model.

    Args:
        prompt: Prompt text to send.
        model: Local Ollama model name.
        timeout: Command timeout in seconds.

    Returns:
        Model output text, or None if unavailable.
    """
    try:
        ollama_executable = _resolve_ollama_executable()
        if not ollama_executable:
            return None

        result = subprocess.run(
            [ollama_executable, "run", model, prompt],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
        output = (result.stdout or "").strip()
        if output:
            return output
        return None
    except Exception:
        return None
