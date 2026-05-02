"""Local Ollama client utility for agent reasoning."""

from typing import Optional
import subprocess
import shutil
import os
import logging


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
    logger = logging.getLogger(__name__)
    try:
        ollama_executable = _resolve_ollama_executable()
        if not ollama_executable:
            logger.debug("Ollama executable not found on PATH or common locations.")
            return None

        logger.debug(f"Using Ollama executable: {ollama_executable}")

        # First call uses the requested timeout; second call gives model load/generation more time.
        timeout_attempts = [timeout, max(timeout * 2, 60)]
        for attempt_index, attempt_timeout in enumerate(timeout_attempts, start=1):
            try:
                result = subprocess.run(
                    [ollama_executable, "run", model, prompt],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=attempt_timeout,
                    check=False,
                )

                stdout = (result.stdout or "").strip()
                stderr = (result.stderr or "").strip()

                if result.returncode != 0:
                    logger.warning(
                        f"Ollama returned non-zero exit code on attempt {attempt_index}: {result.returncode}"
                    )
                    if stderr:
                        logger.warning(f"Ollama stderr: {stderr}")

                if stdout:
                    logger.debug(f"Ollama returned stdout on attempt {attempt_index}")
                    return stdout

                if stderr:
                    logger.debug(f"Ollama produced no stdout; stderr: {stderr}")
                else:
                    logger.debug("Ollama produced no output")
                return None

            except subprocess.TimeoutExpired:
                logger.warning(
                    f"Ollama timed out on attempt {attempt_index} after {attempt_timeout}s for model '{model}'"
                )
                if attempt_index == len(timeout_attempts):
                    return None

        return None
    except Exception as e:
        logger.exception(f"Calling Ollama failed: {e}")
        return None
