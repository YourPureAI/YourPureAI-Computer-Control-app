# actions/show_form.py
import tkinter as tk # Need tkinter for the FormDialog if defined here

# If FormDialog stays in scenario_executor.py, we call it via runner_instance.
# If you move FormDialog here, you need to import ttk etc.

def execute(data, variables, runner_instance):
    """
    Displays a form to the user and collects input into variables.
    Relies on FormDialog being accessible via runner_instance.
    """
    try:
        fields = data.get("fields", [])
        if not fields:
            print("Warning: Show Form action has no fields defined.")
            return True # Not an error, just nothing to do

        print(f"Action 'Show Form' with fields: {[f.get('name', '') for f in fields]}")

        # Use the FormDialog class accessible through the runner instance
        form = runner_instance.FormDialog(runner_instance.root, fields, variables)

        if form.cancelled:
            print("Form cancelled by user.")
            runner_instance.stop_execution_flag.set() # Signal to stop scenario
            return False # Indicate cancellation/failure to proceed
        else:
            print("Form processed. Variables updated:", variables)
            return True

    except Exception as e:
        error_message = f"Error executing 'Show Form': {e}"
        print(error_message)
        runner_instance.display_message("Action Error", error_message, error=True)
        return False