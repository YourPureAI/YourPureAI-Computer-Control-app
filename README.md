# Your Pure AI - Computer Control Application
Application which you can use together with YourPureAI (https://mypureai.pro) to control actions on your computer by your AI Assistant and Agent.

This project provides a suite of Python tools for creating and executing automated desktop workflows, referred to as "scenarios". It consists of two main parts:

1.  **Scenario Creator (`scenario_creator.py`):** A graphical user interface (GUI) application used to build step-by-step automation scenarios.
2.  **Scenario Executor (`scenario_executor.py`):** A background script that monitors the system clipboard and executes saved scenarios based on specific trigger commands.

The goal is to allow users to easily record and define sequences of actions (like mouse clicks, keyboard input, highlighting areas, showing forms, running commands) and then trigger these sequences dynamically via a clipboard command, potentially passing in data for customized execution.

## Features

*   **GUI Scenario Builder:** Visually create automation sequences with an easy-to-use interface.
*   **Modular Action System:** Actions (like "Click Mouse", "Insert Text") are implemented in separate Python files, making the system extensible.
*   **Clipboard Trigger:** Initiate scenario execution by copying a specific command and JSON payload to the clipboard.
*   **Dynamic Variables:** Pass data into scenarios during execution via the clipboard trigger and use variables within action steps (e.g., `${user_name}`).
*   **User Interaction:** Actions include highlighting screen regions, showing informational messages, and displaying custom forms for user input during scenario execution.
*   **GUI Automation:** Perform left/right mouse clicks, type text, press special keys (Enter, Tab, Arrows, etc.), select all (Ctrl+A), and interact with the clipboard (Ctrl+C, Ctrl+V).
*   **Command Execution:** Run commands or scripts via Windows Command Prompt (`cmd`) or PowerShell.
*   **Configurable Security:** Control which scenarios are allowed to run via a central configuration file (`allowed_scenarios.json`).
*   **Scenario Management:** Save and load scenarios in JSON format.

## Integration with Other Automation Tools

While this suite provides a range of built-in actions, it's also designed to integrate with your existing automation ecosystem. Use the **`Execute Command`** action to run PowerShell, `cmd`, or bash scripts. This allows you to easily trigger workflows or specific tasks managed by other automation platforms like UI.Vision, Selenium scripts, custom applications, or any tool accessible via the command line.

## Directory Structure
your_project_directory/

├── scenario_creator.py # GUI application for creating scenarios

├── scenario_executor.py # Background script for executing scenarios

├── allowed_scenarios.json # Configuration for permitted scenarios and aliases

├── actions_config.json # Maps scenario action types to Python modules

├── scenarios/ # Default directory for saved scenario (.json) files

│ └── example_scenario.json # Example scenario file

└── actions/ # Contains individual Python modules for each action type

├── init.py # Makes 'actions' a package (can be empty)

├── highlight_rectangle.py

├── left_mouse_click.py

├── right_mouse_click.py

├── wait.py

├── insert_text.py

├── store_variable.py

├── copy_to_clipboard.py

├── paste_from_clipboard.py

├── select_all.py

├── press_key.py

├── info_message.py

├── show_form.py

├── execute_command.py

└── ... (other action modules)


## Prerequisites & Installation

1.  **Python:** Ensure you have Python 3.x installed.
2.  **Required Libraries:** Install the necessary Python libraries using pip:
    ```bash
    pip install pyperclip pyautogui keyboard pyttsx3 Pillow
    ```
    *   `pyperclip`: For clipboard monitoring and interaction.
    *   `pyautogui`: For GUI automation (mouse, keyboard control).
    *   `keyboard`: For hotkey registration (in Creator) and specific key simulation/waiting (in Executor). **Note:** This library might require administrator/root privileges to function correctly, especially for global hotkeys or low-level key events.
    *   `pyttsx3`: (Optional) For text-to-speech functionality in the "Info Message" action. If initialization fails, TTS will be skipped.
    *   `Pillow`: Often needed as a dependency for `pyautogui`.
    *   `tkinter`: Used for the GUI (Creator) and dialogs/overlays (Executor). Usually included with standard Python installations on Windows, but might need separate installation on some Linux distributions (e.g., `sudo apt-get install python3-tk`).

## Usage: Scenario Creator (`scenario_creator.py`)

This GUI application allows you to build and save automation scenarios.

**Running the Creator:**

```bash
python scenario_creator.py
```

## Interface Overview

### Left Panel ("Available Actions")
Buttons for each type of action you can add to your scenario.

### Right Panel ("Scenario Actions")
A list displaying the sequence of actions currently in your scenario.

### Buttons (Below Action List)
*   **Edit**: Edit the selected action.
*   **Remove**: Remove the selected action.
*   **Move Up**: Move the selected action up in the sequence.
*   **Move Down**: Move the selected action down in the sequence.

### Menu Bar
*   **File**:
    *   *New Scenario*
    *   *Save Scenario*
    *   *Load Scenario*
    *   *Exit*
*   **Settings**:
    *   *Change Hotkey* (for coordinate selection).

## Creating a Scenario

1.  **Add Actions**: Click buttons in the **"Available Actions"** panel to add steps to your scenario. They will appear in the **"Scenario Actions"** list.

2.  **Configure Actions**: When you add an action that requires parameters (like coordinates, text, duration), a configuration dialog window will pop up.

### Coordinate Selection (for *Highlight Rectangle*, *Left/Right Click*)

1.  The dialog will prompt you to use a hotkey (default: `Ctrl+Shift`).
2.  Press the hotkey **once**. The Creator window will minimize.
3.  **For Clicks**: Move your mouse to the desired click location and press the hotkey **again**. The coordinates are recorded.
4.  **For Rectangles**:
    *   Move your mouse to the starting corner (e.g., top-left) and press the hotkey **again**.
    *   Then, move your mouse to the ending corner (e.g., bottom-right) and press the hotkey a **third time**. The start and end coordinates are recorded.
5.  The Creator window will restore automatically after coordinates are captured.
6.  The dialog will update to show the captured coordinates. Fill in any other required fields (like message, color) in the dialog.
7.  Click **"OK"** in the dialog to add the configured action.

### Other Actions
Fill in the required fields in their respective dialogs (e.g., text for *"Insert Text"*, seconds for *"Wait"*, field names for *"Show Form"*). Use `${variable_name}` syntax where variable substitution is supported.

### Manage Sequence
Select actions in the **"Scenario Actions"** list and use the **"Edit"**, **"Remove"**, **"Move Up"**, **"Move Down"** buttons to modify the scenario.

### Save Scenario
Use **File** > **Save Scenario**. Enter a filename (without extension). The scenario will be saved as a `.json` file in the `scenarios/` directory.

### Load Scenario
Use **File** > **Load Scenario** to load a previously saved `.json` file.

### Change Hotkey
Use **Settings** > **Change Hotkey** to define a different key combination for coordinate selection.


## Usage: Scenario Executor (`scenario_executor.py`)

This script runs silently in the background, waiting for specific commands on the clipboard to execute scenarios.

### Running the Executor

1.  Open your terminal or command prompt.
2.  Navigate to the directory containing the script.
3.  Run the script using Python:

    ```bash
    python scenario_executor.py
    ```

4.  The script will print status messages to the console indicating it's running and monitoring the clipboard.

*Important: The executor needs to keep running in the terminal for it to work. Do not close the terminal window while you need the executor to be active.*


## Triggering a Scenario

### 1. Construct the Command
Create a string containing the trigger prefix followed by a JSON payload.

*   **Prefix:** `Execute_Computer_Command_Your_Pure_AI-`
*   **JSON Payload:** Must contain at least `actionName`. Can optionally include `dataForExecution`.

    ```json
    {
      "actionName": "YOUR_SCENARIO_NAME",
      "dataForExecution": {
        "variable1_name": "some_value",
        "variable2_name": "another_value"
      }
    }
    ```

    *   **`actionName`**: The logical name of the scenario you want to run (must be listed and allowed in `allowed_scenarios.json`). **Do not** include the `.json` extension.
    *   **`dataForExecution`**: (Optional) A dictionary where keys are variable names and values are the initial values for those variables within the scenario run. These variables can be accessed in actions like "Insert Text" using `${variable_name}` syntax.

### 2. Copy to Clipboard
Copy the **entire string** (prefix + JSON) to your system clipboard (e.g., using `Ctrl+C`).

### Execution Process

1.  The `scenario_executor.py` script detects the change in the clipboard content.
2.  It checks if the content starts with the trigger prefix (`Execute_Computer_Command_Your_Pure_AI-`).
3.  It parses the JSON payload following the prefix.
4.  It looks up the `actionName` in `allowed_scenarios.json`.
5.  **If found and `allowed` is `true`:**
    *   It determines the actual scenario filename to use (using `alias` if provided, otherwise `name`).
    *   It checks if the corresponding `.json` file exists in the `scenarios/` directory.
    *   **If the file exists:**
        *   It loads the scenario actions.
        *   It initializes the scenario variables using the `dataForExecution` payload (if provided).
        *   It executes the actions in the scenario sequence one by one.
            *   User interactions (messages, highlights, forms) will appear on screen.
            *   Command output (from "Execute Command") will be logged to the console where the executor is running.
6.  **If not found, not allowed, or the scenario file doesn't exist:**
    *   An error message will be displayed to the user (via a message box).
    *   The error will be logged to the console.

*Note: Execution happens in a separate thread to avoid blocking the clipboard monitor during long-running scenarios.*

## Stopping the Executor

1.  Go to the terminal window where `scenario_executor.py` is running.
2.  Press `Ctrl+C`.


## Configuration Files

These JSON files control the behavior and security of the Scenario Executor.

### 1. `allowed_scenarios.json`

*   **Purpose:** Defines which scenarios can be triggered via the clipboard and maps requested names to actual scenario files (using aliases). This acts as a security layer.
*   **Format:** A JSON list `[...]` containing objects `{...}` for each scenario.
*   **Fields per Object:**
    *   `"name"` (String, Required): The logical name used in the `"actionName"` field of the clipboard trigger JSON.
    *   `"allowed"` (Boolean, Required): Set to `true` to allow this scenario to be executed, `false` to disallow it.
    *   `"alias"` (String or `null`, Required):
        *   If `null`, the executor will look for a file named `scenarios/<name>.json`.
        *   If a string (e.g., `"actual_file_v2"`), the executor will look for `scenarios/<alias>.json`. This allows you to trigger `my_process` but run `my_process_updated_version.json`.
*   **Example:**

    ```json
    [
      {
        "name": "daily_report",
        "allowed": true,
        "alias": null
      },
      {
        "name": "login_app_x",
        "allowed": true,
        "alias": "standard_login_procedure_v3"
      },
      {
        "name": "old_process",
        "allowed": false,
        "alias": null
      }
    ]
    ```

### 2. `actions_config.json`

*   **Purpose:** Maps the `"type"` string used within scenario JSON files to the corresponding Python module filename (without `.py`) located in the `actions/` directory. This allows the executor to dynamically load and run the code for each action.
*   **Format:** A JSON dictionary `{...}`.
*   **Structure:** `"Action Type String"`: `"python_module_name"`
*   **Example:**

    ```json
    {
      "Highlight Rectangle": "highlight_rectangle",
      "Left Mouse Click": "left_mouse_click",
      "Execute Command": "execute_command",
      "Insert Text": "insert_text",
      "...": "..."
    }
    ```

*   *Note: If you add a new action module (e.g., `actions/double_click.py`), you **must** add a corresponding entry here (e.g., `"Double Click": "double_click"`) for the executor to recognize it.*

## Available Actions (Core Set)

This list summarizes the actions available in the Scenario Creator and executed by the Scenario Executor. Refer to the individual files in the `actions/` directory for implementation details.

### Highlight Rectangle (`highlight_rectangle.py`)
Draws a rectangle border on the screen.
*   **Params:** `coordinates` (start, end), `message` (string, displayed near rectangle), `color` (string), `thickness` (int), `wait_for_click` (boolean), `wait_for_text` (boolean, waits for Enter key).

### Left Mouse Click (`left_mouse_click.py`)
Performs a standard left mouse click.
*   **Params:** `coordinates` (x, y).

### Right Mouse Click (`right_mouse_click.py`)
Performs a standard right mouse click.
*   **Params:** `coordinates` (x, y).

### Wait (`wait.py`)
Pauses scenario execution.
*   **Params:** `seconds` (float).

### Insert Text (`insert_text.py`)
Types text into the active window. Supports variable substitution.
*   **Params:** `text` (string, can contain `${variable_name}`).

### Store Variable (`store_variable.py`)
Saves data into a scenario variable for later use.
*   **Params:** `name` (string, variable name), `source` (string, `"value"` or `"clipboard"`), `value` (string, used if `source` is `"value"`, supports `${variable_name}`).

### Copy to Clipboard (`copy_to_clipboard.py`)
Simulates `Ctrl+C` / `Cmd+C`. Assumes content is already selected.
*   **Params:** None.

### Paste from Clipboard (`paste_from_clipboard.py`)
Simulates `Ctrl+V` / `Cmd+V`.
*   **Params:** None.

### Select All (`select_all.py`)
Simulates `Ctrl+A` / `Cmd+A`.
*   **Params:** None.

### Press Key (`press_key.py`)
Simulates pressing a single non-character key.
*   **Params:** `key` (string, e.g., `"enter"`, `"tab"`, `"up"`, `"f5"` - see `SUPPORTED_KEYS` in the module).

### Info Message (`info_message.py`)
Displays a message box to the user (waits for "OK"). Can optionally read the message aloud.
*   **Params:** `message` (string, supports `${variable_name}`), `speak` (boolean).

### Show Form (`show_form.py`)
Displays a custom form for user input. Waits for "Process" or "Cancel". Input values are stored in variables named after the fields.
*   **Params:** `fields` (list of objects, each with `name` and `description`).

### Execute Command (`execute_command.py`)
Runs commands in Windows `cmd` or `powershell`. Captures output. Supports variable substitution in commands.
*   **Params:** `command_type` (string, `"cmd"` or `"powershell"`), `commands` (string, potentially multi-line, supports `${variable_name}`).

## Contributing

Contributions, issues, and feature requests are welcome. Please feel free to fork the repository, make changes, and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
