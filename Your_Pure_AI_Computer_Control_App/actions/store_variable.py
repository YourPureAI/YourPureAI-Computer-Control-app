# actions/store_variable.py
import pyperclip # To access clipboard content

def execute(data, variables, runner_instance):
    """
    Stores a value into a scenario variable, either from a specific value or the clipboard.

    Args:
        data (dict): The action's data dictionary.
                     Expected keys:
                       'name' (string): The name of the variable to create/update.
                       'source' (string: 'value' or 'clipboard').
                       'value' (string, optional): The value to store if source is 'value'.
        variables (dict): The dictionary of current scenario variables (this is modified).
        runner_instance (ScenarioRunner): The instance of the ScenarioRunner.

    Returns:
        bool: True if execution was successful, False otherwise.
    """
    if runner_instance.stop_execution_flag.is_set():
        print("Store Variable: Execution cancelled before start.")
        return False

    # --- Get Data ---
    variable_name = data.get("name")
    source = str(data.get("source", "")).lower() # Default to empty string, convert to lower
    value_template = data.get("value", "") # Value if source is 'value'

    # --- Validate Data ---
    if not variable_name:
        error_message = "Error executing 'Store Variable': Missing 'name' for the variable."
        print(error_message)
        runner_instance.display_message("Action Error", error_message, error=True)
        return False

    if source not in ["value", "clipboard"]:
        error_message = f"Error executing 'Store Variable': Invalid 'source' ('{source}'). Must be 'value' or 'clipboard'."
        print(error_message)
        runner_instance.display_message("Action Error", error_message, error=True)
        return False

    # --- Perform Storage ---
    try:
        final_value = None
        log_source_detail = ""

        if source == "value":
            # Substitute variables within the provided value itself
            final_value = runner_instance._substitute_variables(value_template)
            log_source_detail = f"from provided value '{value_template}' (resolved: '{final_value}')"

        elif source == "clipboard":
            # Get value from clipboard
            try:
                 final_value = pyperclip.paste()
                 if final_value is None: # pyperclip might return None on error
                     final_value = "" # Treat as empty string if paste fails slightly
                 log_source_detail = "from clipboard"
            except pyperclip.PyperclipException as clip_err:
                 error_message = f"Error executing 'Store Variable': Failed to read from clipboard: {clip_err}"
                 print(error_message)
                 runner_instance.display_message("Action Error", error_message, error=True)
                 return False # Fail if clipboard access fails

        # Store the final value in the variables dictionary
        variables[variable_name] = final_value
        print(f"Store Variable: Stored value into variable '{variable_name}' {log_source_detail}.")
        # Optionally print the actual stored value (be careful with sensitive data)
        # print(f"   -> Stored value: {final_value}")

        return True

    except Exception as e:
        # Catch potential errors during variable substitution or other unexpected issues
        error_message = f"Error executing 'Store Variable' for variable '{variable_name}': {e}"
        import traceback
        print(error_message)
        traceback.print_exc()
        runner_instance.display_message("Action Error", error_message, error=True)
        return False