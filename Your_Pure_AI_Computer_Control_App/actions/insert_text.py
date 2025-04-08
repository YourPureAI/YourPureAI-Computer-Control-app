# actions/insert_text.py
import pyautogui

def execute(data, variables, runner_instance):
    """
    Inserts text, substituting variables.
    """
    try:
        text_to_insert_template = data.get("text", "")
        # Use the runner's variable substitution method
        text_to_insert = runner_instance._substitute_variables(text_to_insert_template)

        pyautogui.write(text_to_insert, interval=0.01)
        print(f"Action 'Insert Text' executed with text: {text_to_insert[:50]}...") # Log truncated text
        return True
    except Exception as e:
        error_message = f"Error executing 'Insert Text': {e}"
        print(error_message)
        runner_instance.display_message("Action Error", error_message, error=True)
        return False