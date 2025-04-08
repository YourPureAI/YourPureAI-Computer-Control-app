# actions/left_mouse_click.py
import pyautogui
import time

def execute(data, variables, runner_instance):
    """
    Executes a left mouse click at specified coordinates.

    Args:
        data (dict): The action's data dictionary from the scenario.
                     Expected keys: 'coordinates' (dict with 'x', 'y').
        variables (dict): The dictionary of current scenario variables.
        runner_instance (ScenarioRunner): The instance of the ScenarioRunner.

    Returns:
        bool: True if execution was successful, False otherwise.
    """
    try:
        coords = data.get("coordinates", {})
        x = coords.get("x", 0)
        y = coords.get("y", 0)

        # You can access runner methods/attributes if needed:
        # runner_instance.display_message("Debug", f"Clicking at {x},{y}")

        pyautogui.click(x=x, y=y, button='left')
        time.sleep(0.1) # Small delay after click
        print(f"Action 'Left Mouse Click' executed at ({x}, {y}).")
        return True
    except Exception as e:
        error_message = f"Error executing 'Left Mouse Click': {e}"
        print(error_message)
        # Use runner's display_message for user feedback
        runner_instance.display_message("Action Error", error_message, error=True)
        return False # Indicate failure