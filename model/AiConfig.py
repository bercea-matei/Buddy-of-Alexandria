import subprocess
import requests
import time
import shutil
import ollama


def full_local_ai_config() -> bool:
    if _ensure_ollama_running():
        if not _ensure_model_available():
            return False
        return True
    return False


def _ensure_ollama_running() -> bool:
    """
    Checks if Ollama is running. If not, tries to start it.
    Returns True if successful, False if Ollama is not installed.
    """
    ollama_url = "http://localhost:11434"

    try:
        response = requests.get(ollama_url)
        if response.status_code == 200:
            print("Ollama is already running.")
            return True
    except requests.ConnectionError:
        print("Ollama is not running. Attempting to start...")

    if shutil.which("ollama") is None:
        print("Error: Ollama executable not found in PATH.")
        print("Please install Ollama from https://ollama.com")
        return False

    try:
        subprocess.Popen(
            ["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

        print("Waiting for Ollama to start...")
        for _ in range(10):
            try:
                requests.get(ollama_url)
                print("Ollama started successfully!")
                return True
            except requests.ConnectionError:
                time.sleep(1)

        print("Timed out waiting for Ollama to start.")
        return False

    except Exception as e:
        print(f"Failed to launch Ollama: {e}")
        return False


def _ensure_model_available(model_name: str = "phi3:mini") -> bool:
    """
    Checks if the specific model is downloaded.
    If not, downloads it (this might take a while!).
    """
    print(f"Checking for model: {model_name}...")

    try:
        list_result = ollama.list()
        existing_models = [m["model"] for m in list_result["models"]]

        if model_name in existing_models:
            print(f"Model '{model_name}' is ready to use.")
            return True

        print(f"Model '{model_name}' not found. Downloading... (This may take time)")

        ollama.pull(model_name)

        print(f"Successfully downloaded '{model_name}'!")
        return True

    except Exception as e:
        print(f"Error checking/downloading model: {e}")
        return False
