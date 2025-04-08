# actions/execute_command.py
import subprocess
import platform
import os
import urllib.parse

def execute(data, variables, runner_instance):
    """
    Executes one or more commands in the specified shell (cmd or powershell).
    ...
    """

    if runner_instance.stop_execution_flag.is_set():
        print("Execute Command: Execution cancelled before start.")
        return False

    # --- Basic Platform Check ---
    if platform.system() != "Windows":
        error_message = "Execute Command: This action currently only supports Windows."
        print(f"Warning: {error_message}")
        runner_instance.display_message("Action Error", error_message, error=True)
        return False

    # --- Get Data ---
    command_type = str(data.get("command_type", "")).lower()
    commands_template = data.get("commands", "")

    # --- Validate Data ---
    if not command_type:
        error_message = "Execute Command: Missing 'command_type' (should be 'cmd' or 'powershell')."
        print(error_message)
        runner_instance.display_message("Action Error", error_message, error=True)
        return False
    if command_type not in ["cmd", "powershell"]:
        error_message = f"Execute Command: Invalid 'command_type' ('{command_type}'). Must be 'cmd' or 'powershell'."
        print(error_message)
        runner_instance.display_message("Action Error", error_message, error=True)
        return False
    if not commands_template:
        error_message = "Execute Command: Missing 'commands' to execute."
        print(error_message)
        runner_instance.display_message("Action Error", error_message, error=True)
        return False

    # --- URL Encode variables starting with "enc_" ---
    for key in variables:
        if key.startswith("enc_"):
            original_value = variables[key]
            encoded_value = urllib.parse.quote(str(original_value), safe='')
            variables[key] = encoded_value

    # --- Substitute Variables ---
    try:
        commands_to_execute = runner_instance._substitute_variables(commands_template)
    except Exception as e:
        error_message = f"Execute Command: Error during variable substitution: {e}"
        print(error_message)
        runner_instance.display_message("Action Error", error_message, error=True)
        return False

    # --- Prepare Arguments for subprocess ---
    args = []
    shell_name = ""
    if command_type == "cmd":
        shell_name = "Command Prompt (cmd.exe)"
        args = ['cmd', '/d', '/c', commands_to_execute]
    elif command_type == "powershell":
        shell_name = "PowerShell"
        args = ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', commands_to_execute]

    print(f"Execute Command: Running via {shell_name}:")
    print(f"--- Start Command ---")
    print(commands_to_execute)
    print(f"--- End Command ---")

    # --- Execute Command ---
    try:
        startupinfo = None
        if platform.system() == "Windows":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            check=False,
            encoding='utf-8',
            errors='replace',
            startupinfo=startupinfo
        )

        print(f"Execute Command: Process finished with return code: {result.returncode}")
        if result.stdout:
            print("--- Command Output (stdout) ---")
            print(result.stdout.strip())
            print("-------------------------------")
        if result.stderr:
            print("--- Command Error Output (stderr) ---")
            print(result.stderr.strip())
            print("-----------------------------------")

        return True

    except FileNotFoundError:
        error_message = f"Execute Command: Error - {shell_name} executable not found. Is it installed and in your PATH?"
        print(error_message)
        runner_instance.display_message("Action Error", error_message, error=True)
        return False
    except OSError as e:
        error_message = f"Execute Command: OS error launching process: {e}"
        print(error_message)
        runner_instance.display_message("Action Error", error_message, error=True)
        return False
    except Exception as e:
        error_message = f"Execute Command: An unexpected error occurred: {e}"
        import traceback
        print(error_message)
        traceback.print_exc()
        runner_instance.display_message("Action Error", error_message, error=True)
        return False
