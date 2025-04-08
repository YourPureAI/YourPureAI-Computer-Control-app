# actions/copy_to_clipboard.py
import pyautogui
import time
import platform # To potentially add OS-specific keys later

def execute(data, variables, runner_instance):
    """
    Simulates pressing Ctrl+C (or Cmd+C on macOS) to copy selected content to the clipboard.

    Args:
        data (dict): The action's data dictionary (expected to be empty).
        variables (dict): The dictionary of current scenario variables (not used here).
        runner_instance (ScenarioRunner): The instance of the ScenarioRunner.

    Returns:
        bool: True if execution was successful, False otherwise.
    """
    if runner_instance.stop_execution_flag.is_set():
        print("Copy to Clipboard: Execution cancelled before start.")
        return False

    copy_key = 'ctrl' # Default for Windows/Linux
    if platform.system() == 'Darwin': # macOS uses Command key
        copy_key = 'command'

    try:
        print(f"Copy to Clipboard: Simulating '{copy_key}+c'")
        # Use pyautogui's hotkey function to press the combination
        pyautogui.hotkey(copy_key, 'c')

        # It's crucial to wait briefly after issuing the command
        # for the OS and application to process it and update the clipboard.
        time.sleep(0.2) # Adjust if needed, 200ms is usually sufficient

        return True

    except Exception as e:
        # Catch potential errors from pyautogui or unexpected issues
        error_message = f"Error executing 'Copy to Clipboard': {e}"
        import traceback
        print(error_message)
        traceback.print_exc()
        runner_instance.display_message("Action Error", error_message, error=True)
        return False