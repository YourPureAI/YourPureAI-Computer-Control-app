# scenario_executor.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
import time
import threading
import pyperclip
import pyautogui
import keyboard # Still potentially needed for wait('enter') etc. if used
import re
import importlib # <-- Add this import
import pyttsx3

# --- Configuration ---
SCENARIO_DIR = "scenarios"
ALLOWED_SCENARIOS_FILE = "allowed_scenarios.json"
ACTIONS_CONFIG_FILE = "actions_config.json" # <-- New config file
ACTIONS_DIR = "actions" # <-- Directory containing action modules
CLIPBOARD_TRIGGER_PREFIX = "Execute_Computer_Command_Your_Pure_AI-"
POLLING_INTERVAL_SECONDS = 1

# --- Global Variables ---
last_clipboard_content = ""
execution_lock = threading.Lock()
actions_config = {} # <-- Store loaded action mappings

# --- Text-to-Speech Engine ---
tts_engine = None
try:
    tts_engine = pyttsx3.init()
except Exception as e:
    print(f"Warning: Could not initialize text-to-speech engine: {e}")
    tts_engine = None

# --- Helper Functions ---

def display_message(title, message, error=False, parent=None):
    # Ensure a hidden root window exists for messagebox
    temp_root = None
    effective_parent = parent

    if not parent:
        try:
            # Attempt to get the default root if it exists
            if tk._default_root:
                effective_parent = tk._default_root
            else:
                 # If not, create a temporary hidden one
                 temp_root = tk.Tk()
                 temp_root.withdraw()
                 effective_parent = temp_root
        except (AttributeError, RuntimeError): # Catch cases where root doesn't exist or is destroyed
             # If getting/checking default root fails, create a temporary hidden one
             temp_root = tk.Tk()
             temp_root.withdraw()
             effective_parent = temp_root


    if error:
        messagebox.showerror(title, message, parent=effective_parent)
    else:
        messagebox.showinfo(title, message, parent=effective_parent)

    # Destroy the temporary root window ONLY if we created it here
    if temp_root:
        try:
            temp_root.destroy()
        except tk.TclError:
            pass # Ignore if already destroyed


def load_config_file(filepath, description):
    """Loads and returns data from a JSON config file."""
    if not os.path.exists(filepath):
        display_message("Config Error", f"{description} file not found: '{filepath}'", error=True)
        raise FileNotFoundError(f"{description} file not found: '{filepath}'")
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        display_message("Config Error", f"Error decoding {description} file: '{filepath}'. Check format.", error=True)
        raise json.JSONDecodeError(f"Error decoding {description} file.", filepath, 0)
    except Exception as e:
        display_message("Config Error", f"Failed to load {description} file '{filepath}': {e}", error=True)
        raise IOError(f"Failed to load {description} file '{filepath}': {e}")


def load_allowed_scenarios():
    return load_config_file(ALLOWED_SCENARIOS_FILE, "Allowed scenarios")

def load_actions_config():
    """Loads the action type to module mapping."""
    global actions_config
    try:
        actions_config = load_config_file(ACTIONS_CONFIG_FILE, "Actions config")
        print("Actions configuration loaded.")
    except Exception:
        # Error already displayed by load_config_file
        actions_config = {} # Ensure it's an empty dict on error
        print("Failed to load actions configuration. Executor may not function correctly.")
        # Decide if you want to exit here or try to continue
        # exit(1) # Or handle more gracefully


def get_scenario_details(requested_name, allowed_scenarios):
    # ... (keep this function as it is) ...
    for scenario_info in allowed_scenarios:
        if scenario_info.get("name") == requested_name:
            if not scenario_info.get("allowed", False):
                raise PermissionError(f"Scenario '{requested_name}' is not allowed.")

            scenario_filename = scenario_info.get("alias") or requested_name
            scenario_path = os.path.join(SCENARIO_DIR, f"{scenario_filename}.json")

            if not os.path.exists(scenario_path):
                 raise FileNotFoundError(f"Scenario file '{scenario_path}' not found (resolved from name/alias '{requested_name}').")

            return scenario_path
    raise ValueError(f"Scenario '{requested_name}' not found in '{ALLOWED_SCENARIOS_FILE}'.")


def load_scenario(scenario_path):
    # ... (keep this function as it is) ...
    try:
        with open(scenario_path, 'r') as f:
            scenario_data = json.load(f)
            if "actions" not in scenario_data:
                raise ValueError("Scenario file is missing the 'actions' list.")
            return scenario_data["actions"]
    except json.JSONDecodeError:
        raise ValueError(f"Error decoding scenario file '{scenario_path}'.")
    except Exception as e:
        # Catch other potential issues like read errors
        raise IOError(f"Could not read scenario file '{scenario_path}': {e}")


# --- Overlay and Form Dialog Classes (Keep them here for now) ---
class HighlightOverlay(tk.Toplevel):
     # ... (keep this class definition as it is) ...
    def __init__(self, parent, x, y, width, height, color="green", thickness=3):
        super().__init__(parent)
        self.overrideredirect(True)  # Remove window decorations (title bar, borders)
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.lift()  # Keep window on top
        self.wm_attributes("-topmost", True)
        # Make window transparent (may be OS-dependent)
        try:
            # Try a common transparent color first
            transparent_color = 'white' # Or 'systemTransparent' on macOS, may vary
            self.wm_attributes("-transparentcolor", transparent_color)
            self.config(bg=transparent_color) # Color to be made transparent
            self.canvas = tk.Canvas(self, bg=transparent_color, highlightthickness=0) # Use transparent background
        except tk.TclError:
            print("Warning: '-transparentcolor' attribute may not be supported. Trying alpha.")
            self.config(bg=color) # Fallback bg color for canvas if alpha fails too
            self.canvas = tk.Canvas(self, bg=color, highlightthickness=0)
            # Fallback: Slightly transparent alpha (might not work everywhere)
            try:
                self.attributes("-alpha", 0.5) # 0.0 (invisible) to 1.0 (opaque)
            except tk.TclError:
                print("Warning: Alpha attribute also not supported. Overlay will be solid.")
                # If alpha also fails, the window will be solid color.

        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Draw the rectangle border *inside* the canvas
        self.canvas.create_rectangle(
            thickness / 2, thickness / 2,
            width - thickness / 2, height - thickness / 2, # Adjust coords for thickness
            outline=color, width=thickness
        )
        self.update() # Ensure drawing is complete
        self._clicked_in_bounds = threading.Event()
        self.bind("<Button-1>", self._on_click) # Bind click to the window

    def _on_click(self, event):
        print("Highlight clicked!")
        self._clicked_in_bounds.set()
        # No need to close here, let the action logic decide when to close

    def wait_for_click_in_bounds(self, timeout=None):
        print("Waiting for click inside highlight...")
        clicked = self._clicked_in_bounds.wait(timeout)
        print(f"Wait finished. Clicked: {clicked}")
        return clicked

    def close(self):
        # Ensure cleanup happens in the main thread if necessary, or handle TclError
        try:
            self.destroy()
        except tk.TclError as e:
            print(f"Error destroying highlight overlay (may already be destroyed): {e}")

class FormDialog(tk.Toplevel):
     # ... (keep this class definition as it is) ...
    def __init__(self, parent, fields, variables_dict):
        super().__init__(parent)
        self.title("Please Fill Out Form")
        self.transient(parent) # Associate with parent window (hidden root)
        self.grab_set() # Make modal
        self.geometry("450x350") # Adjust as needed

        self.fields = fields
        self.variables = variables_dict
        self.entries = {}
        self.cancelled = True # Assume cancelled unless Process is clicked

        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Scrollable Frame for Fields ---
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        # --- End Scrollable Frame ---


        for field in self.fields:
            field_name = field.get("name", "unknown_field")
            description = field.get("description", field_name) # Use name if no description

            row_frame = ttk.Frame(scrollable_frame) # Add fields to scrollable frame
            row_frame.pack(fill=tk.X, pady=5, padx=5)

            lbl = ttk.Label(row_frame, text=f"{description}:", width=15, anchor='w')
            lbl.pack(side=tk.LEFT, padx=(0, 5))

            entry = ttk.Entry(row_frame, width=30)
            entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
            self.entries[field_name] = entry

        button_frame = ttk.Frame(self) # Place buttons outside the scrollable area
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 15), padx=15)

        # Center buttons
        button_frame.column_configure(0, weight=1)
        button_frame.column_configure(1, weight=1)
        button_frame.column_configure(2, weight=1) # Spacer

        process_button = ttk.Button(button_frame, text="Process", command=self.on_process, width=10)
        process_button.grid(row=0, column=0, sticky='e', padx=5)

        cancel_button = ttk.Button(button_frame, text="Cancel", command=self.on_cancel, width=10)
        cancel_button.grid(row=0, column=1, sticky='w', padx=5)


        self.protocol("WM_DELETE_WINDOW", self.on_cancel) # Handle closing window with 'X'

        self.update_idletasks() # Ensure window size is calculated
        # Center the window
        parent_geo = self.master.winfo_geometry() # Get geometry of parent (hidden root)
        parent_x = self.master.winfo_rootx()
        parent_y = self.master.winfo_rooty()

        self_width = self.winfo_reqwidth()
        self_height = self.winfo_reqheight()

        # Calculate position
        position_right = int(parent_x + (self.master.winfo_width() / 2) - (self_width / 2))
        position_down = int(parent_y + (self.master.winfo_height() / 2) - (self_height / 2))

        # Fallback if master info isn't useful (e.g., withdrawn) - center on screen
        if self.master.winfo_width() < 50: # Heuristic for withdrawn window
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            position_right = int(screen_width / 2 - self_width / 2)
            position_down = int(screen_height / 2 - self_height / 2)


        self.geometry(f"+{position_right}+{position_down}")

        self.wait_window() # Block execution until dialog is closed

    def on_process(self):
        for field_name, entry_widget in self.entries.items():
            self.variables[field_name] = entry_widget.get()
        self.cancelled = False
        self.destroy()

    def on_cancel(self):
        self.cancelled = True
        self.destroy()

# --- Scenario Runner ---
class ScenarioRunner:
    def __init__(self, actions, initial_variables):
        self.actions = actions
        self.variables = initial_variables if initial_variables else {}
        self.root = tk.Tk() # Hidden root for dialogs/overlays
        self.root.withdraw()
        # Make helpers available to action modules via the runner instance
        self.display_message = display_message
        self.HighlightOverlay = HighlightOverlay
        self.FormDialog = FormDialog
        self.tts_engine = tts_engine # Pass engine instance
        self.stop_execution_flag = threading.Event() # Flag for cancellation

    def _substitute_variables(self, text):
        # ... (keep this function as it is) ...
        if not isinstance(text, str):
            return text # Only substitute in strings

        def replace_match(match):
            var_name = match.group(1)
            # Return the variable value as a string, or the original match if not found
            return str(self.variables.get(var_name, match.group(0)))

        pattern = re.compile(r'\$\{(\w+)\}')
        return pattern.sub(replace_match, text)

    def _run_action(self, action):
        """Loads and executes a single action from its module."""
        action_type = action.get("type")
        data = action.get("data", {})
        print(f"Attempting action: {action_type}")

        if self.stop_execution_flag.is_set():
            print("Execution cancelled.")
            return False # Stop processing further actions

        module_name = actions_config.get(action_type)
        if not module_name:
            error_msg = f"Unknown action type '{action_type}'. Check scenario and actions_config.json."
            print(f"Error: {error_msg}")
            self.display_message("Scenario Error", error_msg, error=True, parent=self.root)
            return False # Stop scenario on unknown action

        try:
            # Construct the full module path (e.g., 'actions.left_mouse_click')
            module_path = f"{ACTIONS_DIR}.{module_name}"
            # Dynamically import the module
            action_module = importlib.import_module(module_path)

            # Get the 'execute' function from the module
            if not hasattr(action_module, 'execute'):
                 raise AttributeError(f"Module '{module_path}' does not have an 'execute' function.")

            execute_func = getattr(action_module, 'execute')

            # Call the action's execute function, passing necessary context
            # The action's execute function should return True/False
            success = execute_func(data, self.variables, self)
            return success

        except ModuleNotFoundError:
            error_msg = f"Action module not found: '{module_path}.py'. Ensure file exists in '{ACTIONS_DIR}' and is listed correctly in actions_config.json."
            print(f"Error: {error_msg}")
            self.display_message("Scenario Error", error_msg, error=True, parent=self.root)
            return False
        except AttributeError as e: # Catch missing 'execute' function
             error_msg = f"Error in action module '{module_path}': {e}"
             print(f"Error: {error_msg}")
             self.display_message("Scenario Error", error_msg, error=True, parent=self.root)
             return False
        except Exception as e:
            # Catch errors *during* the execution of the action's code
            error_message = f"Error executing action '{action_type}' (module: {module_name}): {e}"
            import traceback
            print(f"Error: {error_message}")
            traceback.print_exc() # Print full traceback for debugging
            # Display error via runner's method (which might fail if root is destroyed)
            try:
                self.display_message("Scenario Execution Error", error_message, error=True, parent=self.root)
            except Exception as display_e:
                print(f"Failed to display error message box: {display_e}")
            return False # Stop scenario on action error

    def run(self):
        """Runs all actions in the scenario."""
        print("--- Starting Scenario Execution ---")
        self.stop_execution_flag.clear() # Reset cancellation flag for this run

        success = True
        for i, action in enumerate(self.actions):
            print(f"\nStep {i+1}/{len(self.actions)}")
            if self.stop_execution_flag.is_set():
                print("--- Scenario Execution Cancelled Mid-Run ---")
                success = False
                break
            if not self._run_action(action):
                print(f"--- Scenario Execution Stopped After Step {i+1} Due to Failure or Cancellation ---")
                success = False
                break # Stop if an action returns False

        if success and not self.stop_execution_flag.is_set():
            print("\n--- Scenario Execution Finished Successfully ---")

        # Clean up the hidden root window
        try:
            # Check if root exists and is valid before destroying
            if self.root and self.root.winfo_exists():
                 self.root.quit() # Exit the hidden mainloop if it was started by wait_window
                 self.root.destroy()
        except tk.TclError as e:
             print(f"Error cleaning up Tkinter root (may already be destroyed): {e}")
        except Exception as e:
            print(f"Unexpected error during Tkinter cleanup: {e}")

        print("------------------------------------")
        return success # Return overall success/failure


# --- Clipboard Monitoring ---
def monitor_clipboard():
    """Monitors clipboard for trigger phrase and executes scenarios."""
    global last_clipboard_content
    print("Clipboard monitor started. Waiting for trigger...")

    while True:
        try:
            # Use execution lock to prevent processing while a scenario is running
            if not execution_lock.locked():
                current_clipboard_content = pyperclip.paste()

                if current_clipboard_content != last_clipboard_content and \
                   current_clipboard_content and \
                   current_clipboard_content.startswith(CLIPBOARD_TRIGGER_PREFIX):

                    print(f"\nTrigger detected in clipboard!")
                    command_json_str = current_clipboard_content[len(CLIPBOARD_TRIGGER_PREFIX):]
                    # Update last content *immediately* after detecting trigger to prevent re-triggering
                    last_clipboard_content = current_clipboard_content

                    # Acquire lock before starting execution
                    # Use a timeout to prevent waiting forever if something goes wrong
                    if execution_lock.acquire(blocking=True, timeout=1):
                        print("Execution lock acquired.")
                        # --- Execution Thread ---
                        # Define a target function for the thread
                        def execution_target(json_str):
                            try:
                                command_data = json.loads(json_str)
                                action_name = command_data.get("actionName")
                                initial_vars = command_data.get("dataForExecution")

                                if not action_name:
                                    raise ValueError("Missing 'actionName' in clipboard JSON.")
                                if initial_vars and not isinstance(initial_vars, dict):
                                     raise ValueError("'dataForExecution' must be a dictionary (JSON object).")

                                allowed_scenarios = load_allowed_scenarios() # Reload allowed list each time

                                scenario_path = get_scenario_details(action_name, allowed_scenarios)
                                scenario_actions = load_scenario(scenario_path)

                                # Create runner and run the scenario
                                runner = ScenarioRunner(scenario_actions, initial_vars)
                                runner.run() # This blocks the execution thread

                            except (PermissionError, FileNotFoundError, ValueError, IOError, RuntimeError, json.JSONDecodeError) as e:
                                print(f"Error processing command: {e}")
                                # Display error in the main thread if possible, or just log
                                display_message("Scenario Error", str(e), error=True)
                            except Exception as e:
                                error_msg = f"An unexpected error occurred during execution setup: {e}"
                                import traceback
                                print(error_msg)
                                traceback.print_exc()
                                display_message("Critical Error", error_msg, error=True)
                            finally:
                                # VERY IMPORTANT: Release the lock from the execution thread
                                if execution_lock.locked():
                                    execution_lock.release()
                                    print("Execution finished, lock released.")
                                else:
                                    # This shouldn't happen if acquired correctly, but log if it does
                                    print("Warning: Tried to release lock, but it wasn't held by this thread.")

                        # Start execution in a separate thread
                        exec_thread = threading.Thread(target=execution_target, args=(command_json_str,))
                        exec_thread.start()
                        # The monitor loop continues almost immediately

                    else:
                        # Failed to acquire lock (should be rare with blocking=True unless timeout occurs)
                        print("Failed to acquire execution lock (timeout or already locked by unexpected thread?). Skipping trigger.")
                        # Reset clipboard content to potentially allow re-triggering later if needed
                        last_clipboard_content = ""


                # Update last content if it changed but wasn't a trigger
                elif current_clipboard_content != last_clipboard_content:
                    last_clipboard_content = current_clipboard_content

            # Brief pause even if lock is held, prevents tight loop
            time.sleep(0.1)

        except pyperclip.PyperclipException as e:
             print(f"Clipboard access error: {e}. Retrying...")
             time.sleep(POLLING_INTERVAL_SECONDS * 5) # Longer wait on clipboard error
        except Exception as e:
            print(f"Unexpected error in monitoring loop: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(POLLING_INTERVAL_SECONDS * 2)

        # Wait before the next check
        time.sleep(POLLING_INTERVAL_SECONDS)


# --- Main Execution ---
if __name__ == "__main__":
    print("Starting Scenario Executor...")

    # --- Initial Setup ---
    required_dirs = [SCENARIO_DIR, ACTIONS_DIR]
    for d in required_dirs:
        if not os.path.exists(d):
            try:
                os.makedirs(d)
                print(f"Created directory: '{d}'")
            except OSError as e:
                print(f"Error creating directory '{d}': {e}. Exiting.")
                exit(1)

    # Ensure actions/__init__.py exists
    init_py_path = os.path.join(ACTIONS_DIR, "__init__.py")
    if not os.path.exists(init_py_path):
        try:
            with open(init_py_path, 'w') as f:
                pass # Create empty file
            print(f"Created '{init_py_path}'")
        except IOError as e:
             print(f"Error creating '{init_py_path}': {e}. Dynamic imports might fail.")


    # Create default config files if they don't exist
    default_files = {
        ALLOWED_SCENARIOS_FILE: [],
        ACTIONS_CONFIG_FILE: { # Add default mappings here
             "Highlight Rectangle": "highlight_rectangle",
             "Left Mouse Click": "left_mouse_click",
             "Right Mouse Click": "right_mouse_click",
             "Wait": "wait",
             "Insert Text": "insert_text",
             "Store Variable": "store_variable",
             "Copy to Clipboard": "copy_to_clipboard",
             "Paste from Clipboard": "paste_from_clipboard",
             "Select All": "select_all",
             "Press Key": "press_key",
             "Info Message": "info_message",
             "Show Form": "show_form"
         }
    }
    for filepath, default_content in default_files.items():
        if not os.path.exists(filepath):
            try:
                with open(filepath, 'w') as f:
                    json.dump(default_content, f, indent=2)
                print(f"Created default config file: '{filepath}'")
                if filepath == ALLOWED_SCENARIOS_FILE:
                     print(" -> Please edit this file to allow specific scenarios.")
                elif filepath == ACTIONS_CONFIG_FILE:
                     print(f" -> Ensure corresponding .py files exist in '{ACTIONS_DIR}'.")
            except IOError as e:
                 print(f"Error creating default file '{filepath}': {e}")

    # --- Load Initial Configs ---
    try:
        load_actions_config() # Load action mappings into global 'actions_config'
        _ = load_allowed_scenarios() # Load allowed scenarios once initially to check file
        print("Initial configuration loaded successfully.")
    except Exception as e:
        print(f"Failed during initial configuration loading: {e}. Exiting.")
        exit(1)


    # --- Start Monitoring ---
    monitor_thread = threading.Thread(target=monitor_clipboard, daemon=True)
    monitor_thread.start()

    print("\nScenario Executor is running in the background.")
    print(f"Monitoring clipboard every {POLLING_INTERVAL_SECONDS} second(s).")
    print(f"Trigger: Copy text starting with '{CLIPBOARD_TRIGGER_PREFIX}' followed by JSON.")
    print("Press Ctrl+C in the console to stop the executor.")

    # Keep the main thread alive
    try:
        while monitor_thread.is_alive(): # Keep running as long as monitor thread is up
             monitor_thread.join(timeout=1.0) # Wait for thread or timeout
    except KeyboardInterrupt:
        print("\nShutdown requested by user (Ctrl+C)...")
        # Optionally: Signal running execution threads to stop gracefully if possible
        # (Requires more complex signalling mechanism between threads)
    except Exception as e:
        print(f"Main loop exited unexpectedly: {e}")

    print("Scenario Executor stopped.")