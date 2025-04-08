# actions/paste_from_clipboard.py
import pyautogui
import time
import platform # To potentially add OS-specific keys later

def execute(data, variables, runner_instance):
    """
    Simulates pressing Ctrl+V (or Cmd+V on macOS) to paste content from the clipboard.

    Args:
        data (dict): The action's data dictionary (expected to be empty).
        variables (dict): The dictionary of current scenario variables (not used here).
        runner_instance (ScenarioRunner): The instance of the ScenarioRunner.

    Returns:
        bool: True if execution was successful, False otherwise.
    """
    if runner_instance.stop_execution_flag.is_set():
        print("Paste from Clipboard: Execution cancelled before start.")
        return False

    paste_key = 'ctrl' # Default for Windows/Linux
    if platform.system() == 'Darwin': # macOS uses Command key
        paste_key = 'command'

    try:
        print(f"Paste from Clipboard: Simulating '{paste_key}+v'")
        # Use pyautogui's hotkey function to press the combination
        pyautogui.hotkey(paste_key, 'v')

        # Add a small delay after pasting, though often less critical than after copy
        time.sleep(0.1)

        return True

    except Exception as e:
        # Catch potential errors from pyautogui or unexpected issues
        error_message = f"Error executing 'Paste from Clipboard': {e}"
        import traceback
        print(error_message)
        traceback.print_exc()
        runner_instance.display_message("Action Error", error_message, error=True)
        return False