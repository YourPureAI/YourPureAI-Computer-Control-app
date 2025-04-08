# actions/wait.py
import time

def execute(data, variables, runner_instance):
    """
    Pauses execution for a specified duration.
    """
    try:
        seconds = data.get("seconds", 1.0)
        time.sleep(float(seconds))
        print(f"Action 'Wait' executed for {seconds} seconds.")
        return True
    except ValueError:
         error_message = f"Invalid number of seconds provided for 'Wait': {data.get('seconds')}"
         print(error_message)
         runner_instance.display_message("Action Error", error_message, error=True)
         return False
    except Exception as e:
        error_message = f"Error executing 'Wait': {e}"
        print(error_message)
        runner_instance.display_message("Action Error", error_message, error=True)
        return False