# actions/right_mouse_click.py
import pyautogui
import time

def execute(data, variables, runner_instance):
    """
    Executes a right mouse click at specified coordinates.

    Args:
        data (dict): The action's data dictionary from the scenario.
                     Expected keys: 'coordinates' (dict with 'x', 'y').
        variables (dict): The dictionary of current scenario variables (not used here).
        runner_instance (ScenarioRunner): The instance of the ScenarioRunner.

    Returns:
        bool: True if execution was successful, False otherwise.
    """
    if runner_instance.stop_execution_flag.is_set():
        print("Right Mouse Click: Execution cancelled before start.")
        return False

    try:
        # --- Get Coordinates ---
        coords = data.get("coordinates")
        if not coords or not isinstance(coords, dict):
             error_message = "Error executing 'Right Mouse Click': Missing or invalid 'coordinates' data."
             print(error_message)
             runner_instance.display_message("Action Error", error_message, error=True)
             return False

        x = coords.get("x")
        y = coords.get("y")

        if x is None or y is None:
            error_message = "Error executing 'Right Mouse Click': Missing 'x' or 'y' in 'coordinates'."
            print(error_message)
            runner_instance.display_message("Action Error", error_message, error=True)
            return False

        # Validate coordinate types (should be numbers)
        if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
             error_message = f"Error executing 'Right Mouse Click': Coordinates must be numbers (received x={x}, y={y})."
             print(error_message)
             runner_instance.display_message("Action Error", error_message, error=True)
             return False

        # --- Execute Click ---
        print(f"Right Mouse Click: Clicking at ({int(x)}, {int(y)})")
        # pyautogui handles float coordinates, but printing ints is cleaner
        pyautogui.click(x=int(x), y=int(y), button='right')
        time.sleep(0.1) # Small delay after click

        return True

    except Exception as e:
        # Catch potential errors from pyautogui or unexpected issues
        error_message = f"Error executing 'Right Mouse Click': {e}"
        import traceback
        print(error_message)
        traceback.print_exc()
        runner_instance.display_message("Action Error", error_message, error=True)
        return False