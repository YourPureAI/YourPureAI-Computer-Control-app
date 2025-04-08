# actions/select_all.py
import pyautogui
import time
import platform # To determine the correct modifier key

def execute(data, variables, runner_instance):
    """
    Simulates pressing Ctrl+A (or Cmd+A on macOS) to select all content
    in the currently active input field or document.

    Args:
        data (dict): The action's data dictionary (expected to be empty).
        variables (dict): The dictionary of current scenario variables (not used here).
        runner_instance (ScenarioRunner): The instance of the ScenarioRunner.

    Returns:
        bool: True if execution was successful, False otherwise.
    """
    if runner_instance.stop_execution_flag.is_set():
        print("Select All: Execution cancelled before start.")
        return False

    modifier_key = 'ctrl' # Default for Windows/Linux
    if platform.system() == 'Darwin': # macOS uses Command key
        modifier_key = 'command'

    try:
        print(f"Select All: Simulating '{modifier_key}+a'")
        # Use pyautogui's hotkey function to press the combination
        pyautogui.hotkey(modifier_key, 'a')

        # Add a small delay to allow the application to process the selection
        time.sleep(0.15) # Slightly longer might be useful for select all

        return True

    except Exception as e:
        # Catch potential errors from pyautogui or unexpected issues
        error_message = f"Error executing 'Select All': {e}"
        import traceback
        print(error_message)
        traceback.print_exc()
        runner_instance.display_message("Action Error", error_message, error=True)
        return False