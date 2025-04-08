# actions/press_key.py
import pyautogui
import time

# List of keys supported by pyautogui.press() that we explicitly allow
# You can expand this list based on pyautogui's documentation if needed.
# See: https://pyautogui.readthedocs.io/en/latest/keyboard.html#keyboard-keys
SUPPORTED_KEYS = [
    'enter', 'return', 'tab', 'backspace', 'delete', 'esc', 'escape',
    'up', 'down', 'left', 'right',
    'pageup', 'pagedown', 'home', 'end',
    'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12',
    'space',
    'ctrlleft', 'ctrlright', 'altleft', 'altright', 'shiftleft', 'shiftright',
    'winleft', 'winright', # Windows key (might be 'command' on macOS)
    'printscreen', 'insert',
    # Add more special keys as required
]
# Add basic alphabet and numbers if you want to allow pressing single characters
# SUPPORTED_KEYS.extend(list('abcdefghijklmnopqrstuvwxyz0123456789'))


def execute(data, variables, runner_instance):
    """
    Presses a specified keyboard key.

    Args:
        data (dict): The action's data dictionary.
                     Expected keys: 'key' (string representing the key to press).
        variables (dict): The dictionary of current scenario variables (not used here).
        runner_instance (ScenarioRunner): The instance of the ScenarioRunner.

    Returns:
        bool: True if execution was successful, False otherwise.
    """
    if runner_instance.stop_execution_flag.is_set():
        print("Press Key: Execution cancelled before start.")
        return False

    key_to_press = data.get("key")

    if not key_to_press:
        error_message = "Error executing 'Press Key': No 'key' specified in action data."
        print(error_message)
        runner_instance.display_message("Action Error", error_message, error=True)
        return False

    key_to_press = str(key_to_press).lower() # Normalize to lowercase

    # Validate against our list of supported keys
    if key_to_press not in SUPPORTED_KEYS:
        error_message = f"Error executing 'Press Key': Key '{key_to_press}' is not supported or allowed. Allowed keys: {SUPPORTED_KEYS}"
        print(error_message)
        runner_instance.display_message("Action Error", error_message, error=True)
        return False

    try:
        print(f"Press Key: Pressing '{key_to_press}'")
        pyautogui.press(key_to_press)
        time.sleep(0.1) # Small delay after pressing the key
        return True

    except Exception as e:
        # Catch potential errors from pyautogui or unexpected issues
        error_message = f"Error executing 'Press Key' for key '{key_to_press}': {e}"
        import traceback
        print(error_message)
        traceback.print_exc()
        runner_instance.display_message("Action Error", error_message, error=True)
        return False