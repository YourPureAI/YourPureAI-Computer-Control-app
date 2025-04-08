# actions/highlight_rectangle.py
import tkinter as tk
import threading
import time
import keyboard  # For waiting on 'enter'
import pyautogui

# --- Configuration for the Label ---
LABEL_PADDING_Y = 5  # Vertical padding around the label text
LABEL_FONT = ("Arial", 10, "bold")  # Font for the message label
LABEL_POSITION = "above"  # Or "below"
WINDOW_OPACITY = 0.3  # Opacity for the entire window (0.0 to 1.0)


class HighlightOverlayWindow(tk.Toplevel):
    """
    A Toplevel window for displaying the highlight rectangle and optional message.
    Handles positioning, always-on-top, transparency, and drawing.
    """

    def __init__(self, parent, x, y, width, height, color="green", thickness=3, message=""):
        super().__init__(parent)

        self.parent = parent
        self.rect_x = x
        self.rect_y = y
        self.rect_width = width
        self.rect_height = height
        self.color = color
        self.thickness = thickness
        self.message = message
        self.label_height = 0
        self.label_widget = None
        self.click_coordinates = None  # Store the click coordinates
        self.perform_automatic_click = False  # Flag to indicate if automatic click should be performed

        # --- Calculate Label Size ---
        if self.message:
            # Create a temporary label to measure its size
            temp_label = tk.Label(self, text=self.message, font=LABEL_FONT, fg=self.color,
                                  bg="white")  # Use white bg temporarily
            temp_label.pack()  # Pack temporarily to calculate size
            self.update_idletasks()  # Ensure geometry is calculated
            self.label_height = temp_label.winfo_reqheight() + (LABEL_PADDING_Y * 2)
            temp_label.destroy()  # Remove the temporary label

        # --- Calculate Overall Window Geometry ---
        self.window_width = self.rect_width
        self.window_height = self.rect_height + self.label_height

        # Adjust window position based on label position
        if LABEL_POSITION == "above" and self.message:
            self.window_x = self.rect_x
            self.window_y = self.rect_y - self.label_height
        elif LABEL_POSITION == "below" and self.message:
            self.window_x = self.rect_x
            self.window_y = self.rect_y
            # The rectangle will be drawn starting at y=0 in the canvas
        else:  # No message or unsupported position
            self.window_x = self.rect_x
            self.window_y = self.rect_y
            self.window_height = self.rect_height  # No extra space needed

        self.geometry(f"{self.window_width}x{self.window_height}+{self.window_x}+{self.window_y}")

        # --- Window Attributes ---
        self.overrideredirect(True)  # No window decorations
        self.wm_attributes("-topmost", True)  # Always on top!
        self.lift()  # Bring window to the front

        # --- Transparency Setup ---
        try:
            self.attributes("-alpha", WINDOW_OPACITY)  # Set window transparency
            print(f"Using -alpha transparency with opacity: {WINDOW_OPACITY}")
            self.config(bg="white")  # Set a background color (can be any color)
        except tk.TclError:
            print("Warning: -alpha attribute not supported. Overlay will be solid.")
            self.config(bg="white")  # Default solid background

        # --- Create Canvas for Rectangle ---
        # Canvas should fill the entire Toplevel window
        self.canvas = tk.Canvas(self, bg=self.config('bg')[-1], highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # --- Draw Rectangle ---
        # Calculate rectangle coordinates *relative to the canvas*
        canvas_rect_x0 = self.thickness / 2
        canvas_rect_y0 = self.thickness / 2
        canvas_rect_x1 = self.rect_width - self.thickness / 2
        canvas_rect_y1 = self.rect_height - self.thickness / 2

        # Adjust vertical position if label is above
        if LABEL_POSITION == "above" and self.message:
            canvas_rect_y0 += self.label_height
            canvas_rect_y1 += self.label_height

        # Draw the rectangle border
        self.canvas.create_rectangle(
            canvas_rect_x0, canvas_rect_y0, canvas_rect_x1, canvas_rect_y1,
            outline=self.color, width=self.thickness
        )

        # --- Create Label for Message ---
        if self.message:
            self.label_widget = tk.Label(
                self.canvas,  # Place label inside the canvas
                text=self.message,
                font=LABEL_FONT,
                fg="black",  # Use black for readability against transparent bg
                bg=self.config('bg')[-1]  # Match canvas background (transparent color or solid)
            )
            # Position label within the canvas
            if LABEL_POSITION == "above":
                self.canvas.create_window(self.rect_width / 2, self.label_height / 2, window=self.label_widget)
            elif LABEL_POSITION == "below":
                # Adjust y-position to be below the rectangle area within the canvas
                label_y_center = self.rect_height + self.label_height / 2
                self.canvas.create_window(self.rect_width / 2, label_y_center, window=self.label_widget)

        # --- Event Handling Setup ---
        self._clicked_event = threading.Event()
        # Bind click to the canvas, as it covers the window
        self.canvas.bind("<Button-1>", self._on_click)
        if self.label_widget:
            self.label_widget.bind("<Button-1>", self._on_click)  # Also bind to label

        self.update()  # Ensure window is drawn

    def _on_click(self, event):
        # Check if click is within the *logical rectangle bounds* on the canvas
        if LABEL_POSITION == "above" and self.message:
            rect_canvas_y_start = self.label_height
        else:
            rect_canvas_y_start = 0
        rect_canvas_y_end = rect_canvas_y_start + self.rect_height

        # Check if click is within the rectangle's bounds (including the interior)
        if (0 <= event.x <= self.rect_width and
                rect_canvas_y_start <= event.y <= rect_canvas_y_end):
            print("Highlight clicked inside logical bounds!")
            self._clicked_event.set()
            # Store the click coordinates relative to the screen
            self.click_coordinates = (self.window_x + event.x, self.window_y + event.y)
            self.perform_automatic_click = True  # Set the flag to perform the automatic click
        else:
            print("Highlight clicked outside logical bounds (e.g., on label area or padding).")

    def wait_for_click_in_bounds(self, timeout=None):
        """Waits until the user clicks within the logical highlight area."""
        print("Waiting for click inside highlight rectangle...")
        # We need to run the Tkinter main loop briefly to process events
        # This is tricky with threading. A simple wait might suffice if events get processed.
        # Alternative: use self.parent.after() to periodically check the event?
        start_time = time.time()
        while True:
            self.parent.update_idletasks()  # Process pending Tkinter events
            self.parent.update()
            if self._clicked_event.is_set():
                print("Click detected by wait loop.")
                return True
            if timeout is not None and (time.time() - start_time) > timeout:
                print("Timeout waiting for click.")
                return False
            time.sleep(0.05)  # Small sleep to prevent busy-waiting

        # return self._clicked_event.wait(timeout) # Simple wait might not process clicks reliably

    def close(self):
        """Safely destroys the overlay window and performs the automatic click if needed."""
        try:
            # Schedule the destroy operation within the Tkinter event loop
            # Needed if called from a different thread, good practice anyway.
            if self.perform_automatic_click and self.click_coordinates:
                self.parent.after(0, self._perform_click_and_destroy)
            else:
                self.parent.after(0, self.destroy)
        except tk.TclError as e:
            print(f"Error scheduling highlight overlay destruction (may already be destroyed): {e}")
        except Exception as e:
            print(f"Unexpected error during overlay close scheduling: {e}")

    def _perform_click_and_destroy(self):
        """Performs the automatic click and then destroys the window."""
        self.update()  # Process any pending events, including destroy
        time.sleep(1)  # Wait for 1 second to ensure the window is gone
        pyautogui.click(x=self.click_coordinates[0], y=self.click_coordinates[1], button='left')
        print(f"Highlight Rectangle: Automatic click performed at {self.click_coordinates}")
        self.destroy()


def execute(data, variables, runner_instance):
    """
    Displays a highlighted rectangle on the screen with an optional message.
    Can wait for a click within the rectangle or for the Enter key.

    Args:
        data (dict): Action data containing coordinates, message, color, etc.
        variables (dict): Current scenario variables.
        runner_instance (ScenarioRunner): The main runner instance.

    Returns:
        bool: True if successful, False otherwise.
    """
    if runner_instance.stop_execution_flag.is_set():
        print("Highlight Rectangle: Execution cancelled before start.")
        return False

    overlay = None  # Initialize overlay variable

    try:
        # --- Get Data ---
        coords = data.get("coordinates", {})
        start = tuple(coords.get("start", [0, 0]))
        end = tuple(coords.get("end", [100, 100]))
        color = data.get("color", "green")
        thickness = data.get("thickness", 3)
        message_template = data.get("message", "")
        wait_click = data.get("wait_for_click", False)
        wait_text = data.get("wait_for_text", False)  # Simplified to wait for 'enter'

        # --- Process Data ---
        message = runner_instance._substitute_variables(message_template)
        # Calculate rectangle geometry (top-left corner, width, height)
        x = min(start[0], end[0])
        y = min(start[1], end[1])
        width = abs(start[0] - end[0])
        height = abs(start[1] - end[1])

        if width <= 0 or height <= 0:
            print("Warning: Highlight rectangle has zero or negative dimension. Skipping.")
            return True  # Not a failure, just nothing to show

        # --- Create and Show Overlay ---
        print(
            f"Highlight Rectangle: Displaying at ({x},{y}) size {width}x{height}, Color: {color}, Msg: '{message[:30]}...'")
        overlay = HighlightOverlayWindow(
            runner_instance.root,  # Use hidden root as parent
            x, y, width, height,
            color, thickness, message
        )

        # --- Handle Waiting Logic ---
        success = True
        if wait_click:
            clicked = overlay.wait_for_click_in_bounds(timeout=None)  # No timeout for now
            if not clicked:
                print("Highlight Rectangle: Wait for click failed or timed out.")
                # Decide if this is a failure - typically yes if waiting was required
                success = False
            else:
                print("Highlight Rectangle: Click detected.")

        elif wait_text:
            # Simplified: Wait for Enter key press after highlight is shown
            print("Highlight Rectangle: Waiting for ENTER key press...")
            try:
                keyboard.wait('enter')  # This blocks this thread
                print("Highlight Rectangle: Enter key pressed.")
            except Exception as ke:
                print(f"Highlight Rectangle: Error waiting for Enter key: {ke}")
                success = False  # Indicate failure if keyboard wait failed
        else:
            # No wait required, show briefly
            print("Highlight Rectangle: Displaying briefly.")
            # We need to keep Tkinter events processed for the duration
            start_time = time.time()
            while time.time() - start_time < 1.5:  # Show for 1.5 seconds
                runner_instance.root.update_idletasks()
                runner_instance.root.update()
                time.sleep(0.05)

        # --- Final Check for Cancellation ---
        if runner_instance.stop_execution_flag.is_set():
            print("Highlight Rectangle: Execution cancelled during wait/display.")
            success = False

        return success

    except Exception as e:
        error_message = f"Error executing 'Highlight Rectangle': {e}"
        import traceback
        print(error_message)
        traceback.print_exc()
        try:
            # Try to display error using the runner's method
            runner_instance.display_message("Action Error", error_message, error=True)
        except Exception as display_e:
            print(f"Failed to display error message box: {display_e}")
        return False  # Indicate failure

    finally:
        # --- Cleanup ---
        if overlay:
            print("Highlight Rectangle: Closing overlay.")
            overlay.close()
        # Ensure Tkinter state is updated after potential blocking calls
        try:
            if runner_instance and runner_instance.root and runner_instance.root.winfo_exists():
                runner_instance.root.update_idletasks()
                runner_instance.root.update()
        except Exception:
            pass  # Ignore cleanup errors
