# actions/info_message.py
# Note: Needs access to tts_engine if speech is enabled.
# We'll keep tts_engine initialization in the main script for simplicity,
# and access it via runner_instance if needed, or just use display_message.

def execute(data, variables, runner_instance):
    """
    Displays an informational message box to the user.
    """
    try:
        message_template = data.get("message", "No message provided.")
        speak = data.get("speak", False) # Check if speech is requested

        message = runner_instance._substitute_variables(message_template)

        print(f"Action 'Info Message': {message}")

        # Text-to-speech handling (optional)
        if speak and runner_instance.tts_engine:
            try:
                runner_instance.tts_engine.say(message)
                runner_instance.tts_engine.runAndWait()
            except Exception as e:
                print(f"Error during text-to-speech for Info Message: {e}")
                # Fallback to message box if speech fails
                runner_instance.display_message("Information", message)
        else:
            # Display standard message box (waits for OK)
            runner_instance.display_message("Information", message)

        return True
    except Exception as e:
        error_message = f"Error executing 'Info Message': {e}"
        print(error_message)
        # Avoid recursive error display if display_message itself fails
        # runner_instance.display_message("Action Error", error_message, error=True)
        return False