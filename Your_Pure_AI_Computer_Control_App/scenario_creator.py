import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
import keyboard
import pyautogui
import threading
import time

class ScenarioCreator:
    def __init__(self, master):
        self.master = master
        self.master.title("Scenario Creator")
        self.master.geometry("900x700")
        
        self.actions = []
        self.current_hotkey = "ctrl+shift"
        self.recording_coordinates = False
        self.coordinate_start = None
        
        # Set up main frames
        self.setup_frames()
        self.setup_action_buttons()
        self.setup_action_list()
        self.setup_menu()
        
        # Register hotkey for coordinate selection
        keyboard.add_hotkey(self.current_hotkey, self.start_coordinate_recording)
        
    def setup_frames(self):
        # Left panel for action buttons
        self.left_frame = ttk.Frame(self.master, padding=10)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        # Right panel for action list
        self.right_frame = ttk.Frame(self.master, padding=10)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Label for action buttons
        ttk.Label(self.left_frame, text="Available Actions").pack(pady=(0, 10))
        
        # Label for action list
        ttk.Label(self.right_frame, text="Scenario Actions").pack(pady=(0, 10))
    
    def setup_menu(self):
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Scenario", command=self.new_scenario)
        file_menu.add_command(label="Save Scenario", command=self.save_scenario)
        file_menu.add_command(label="Load Scenario", command=self.load_scenario)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.master.quit)
        
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Change Hotkey", command=self.change_hotkey)
    
    def setup_action_buttons(self):
        # Create a frame with scrollbar for buttons
        button_canvas = tk.Canvas(self.left_frame)
        button_scrollbar = ttk.Scrollbar(self.left_frame, orient="vertical", command=button_canvas.yview)
        button_scrollable_frame = ttk.Frame(button_canvas)
        
        button_scrollable_frame.bind(
            "<Configure>",
            lambda e: button_canvas.configure(scrollregion=button_canvas.bbox("all"))
        )
        
        button_canvas.create_window((0, 0), window=button_scrollable_frame, anchor="nw")
        button_canvas.configure(yscrollcommand=button_scrollbar.set)
        
        button_canvas.pack(side="left", fill="both", expand=True)
        button_scrollbar.pack(side="right", fill="y")
        
        # Add action buttons
        actions = [
            ("Highlight Rectangle", self.add_highlight_rectangle),
            ("Left Mouse Click", self.add_left_click),
            ("Right Mouse Click", self.add_right_click),
            ("Wait", self.add_wait),
            ("Insert Text", self.add_insert_text),
            ("Store Variable", self.add_store_variable),
            ("Copy to Clipboard", self.add_copy_to_clipboard),
            ("Paste from Clipboard", self.add_paste_from_clipboard),
            ("Select All", self.add_select_all),
            ("Press Key", self.add_press_key),
            ("Show Info Message", self.add_info_message),
            ("Show Form", self.add_show_form),
            ("Execute Command", self.add_execute_command)
        ]
        
        for text, command in actions:
            ttk.Button(button_scrollable_frame, text=text, command=command, width=20).pack(pady=5)
    
    def setup_action_list(self):
        # Create a frame with scrollbar for action list
        self.action_frame = ttk.Frame(self.right_frame)
        self.action_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar and Treeview for actions
        self.action_scrollbar = ttk.Scrollbar(self.action_frame)
        self.action_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.action_tree = ttk.Treeview(
            self.action_frame, 
            columns=("Type", "Details"),
            show="headings",
            yscrollcommand=self.action_scrollbar.set
        )
        
        self.action_tree.heading("Type", text="Action Type")
        self.action_tree.heading("Details", text="Details")
        
        self.action_tree.column("Type", width=150, stretch=False)
        self.action_tree.column("Details", width=350)
        
        self.action_scrollbar.config(command=self.action_tree.yview)
        self.action_tree.pack(fill=tk.BOTH, expand=True)
        
        # Buttons for manipulating actions
        button_frame = ttk.Frame(self.right_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Edit", command=self.edit_action).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Remove", command=self.remove_action).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Move Up", command=self.move_action_up).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Move Down", command=self.move_action_down).pack(side=tk.LEFT, padx=5)
    
    # Action management methods
    def add_action(self, action_type, details, data):
        action = {
            "type": action_type,
            "details": details,
            "data": data
        }
        self.actions.append(action)
        self.update_action_list()
    
    def update_action_list(self):
        # Clear the treeview
        for item in self.action_tree.get_children():
            self.action_tree.delete(item)
        
        # Add actions to the treeview
        for i, action in enumerate(self.actions):
            self.action_tree.insert("", "end", values=(action["type"], action["details"]))
    
    def edit_action(self):
        selected = self.action_tree.selection()
        if not selected:
            messagebox.showinfo("Edit Action", "Please select an action to edit")
            return
        
        index = self.action_tree.index(selected[0])
        action = self.actions[index]
        
        if action["type"] == "Highlight Rectangle":
            self.edit_highlight_rectangle(index)
        elif action["type"] == "Left Mouse Click":
            self.edit_left_click(index)
        elif action["type"] == "Right Mouse Click":
            self.edit_right_click(index)
        elif action["type"] == "Wait":
            self.edit_wait(index)
        elif action["type"] == "Insert Text":
            self.edit_insert_text(index)
        elif action["type"] == "Store Variable":
            self.edit_store_variable(index)
        elif action["type"] == "Info Message":
            self.edit_info_message(index)
        elif action["type"] == "Show Form":
            self.edit_show_form(index)
        elif action["type"] == "Press Key":
            self.edit_press_key(index)
        elif action["type"] == "Execute Command":
            self.edit_execute_command(index)            
        
        self.update_action_list()
    
    def remove_action(self):
        selected = self.action_tree.selection()
        if not selected:
            messagebox.showinfo("Remove Action", "Please select an action to remove")
            return
        
        index = self.action_tree.index(selected[0])
        del self.actions[index]
        self.update_action_list()
    
    def move_action_up(self):
        selected = self.action_tree.selection()
        if not selected:
            messagebox.showinfo("Move Action", "Please select an action to move")
            return
        
        index = self.action_tree.index(selected[0])
        if index > 0:
            self.actions[index], self.actions[index-1] = self.actions[index-1], self.actions[index]
            self.update_action_list()
            self.action_tree.selection_set(self.action_tree.get_children()[index-1])
    
    def move_action_down(self):
        selected = self.action_tree.selection()
        if not selected:
            messagebox.showinfo("Move Action", "Please select an action to move")
            return
        
        index = self.action_tree.index(selected[0])
        if index < len(self.actions) - 1:
            self.actions[index], self.actions[index+1] = self.actions[index+1], self.actions[index]
            self.update_action_list()
            self.action_tree.selection_set(self.action_tree.get_children()[index+1])
    
    # Coordinate recording methods
    def start_coordinate_recording(self):
        # If we're already recording, then this is the second hotkey press - record the position
        if self.recording_coordinates:
            current_pos = pyautogui.position()
            
            # For single-click actions (left click, right click)
            if hasattr(self, 'temp_coordinates') and isinstance(self.temp_coordinates, dict) and 'x' in self.temp_coordinates:
                self.temp_coordinates['x'] = current_pos[0]
                self.temp_coordinates['y'] = current_pos[1]
                print(f"Recorded position: {current_pos}")
                
                self.recording_coordinates = False
                self.master.deiconify()  # Restore window
                
            # For rectangle selection (highlight rectangle) - handle first and second point
            elif hasattr(self, 'temp_coordinates') and isinstance(self.temp_coordinates, dict) and 'start' in self.temp_coordinates:
                if self.coordinate_start is None:
                    # First point
                    self.coordinate_start = current_pos
                    print(f"Recorded start position: {current_pos}")
                    #pass
                    #messagebox.showinfo("Coordinate Selection", 
                    #                    "Start point recorded. Press Ctrl+Shift again to record the end point.")
                else:
                    # Second point - complete the rectangle
                    self.temp_coordinates['start'] = self.coordinate_start
                    self.temp_coordinates['end'] = current_pos
                    print(f"Recorded end position: {current_pos}")
                    
                    self.recording_coordinates = False
                    self.coordinate_start = None
                    self.master.deiconify()  # Restore window
        else:
            # First time pressing the hotkey - start recording
            self.recording_coordinates = True
            self.coordinate_start = None
            self.master.iconify()  # Minimize window
            
            # Show a message indicating what to do next
            root = tk.Tk()
            root.withdraw()
            if hasattr(self, 'temp_coordinates') and isinstance(self.temp_coordinates, dict) and 'x' in self.temp_coordinates:
                pass
                #messagebox.showinfo("Coordinate Selection", 
                #                   "Position your mouse where you want to click, then press Ctrl+Shift again to record.")
            else:
                pass
                # messagebox.showinfo("Coordinate Selection", 
                #                   "Position your mouse at the starting point, then press Ctrl+Shift to record. Then position at the end point and press Ctrl+Shift again.")
            root.destroy()
    
    # Menu action methods
    def new_scenario(self):
        if messagebox.askyesno("New Scenario", "Are you sure you want to create a new scenario? All unsaved changes will be lost."):
            self.actions = []
            self.update_action_list()
    
    def save_scenario(self):
        filename = simpledialog.askstring("Save Scenario", "Enter a name for the scenario file (without extension):")
        if not filename:
            return
            
        # Make sure filename ends with .json
        if not filename.endswith('.json'):
            filename += '.json'
            
        data = {
            "name": filename.replace('.json', ''),
            "actions": self.actions
        }
        
        try:
            os.makedirs('scenarios', exist_ok=True)
            with open(f"scenarios/{filename}", 'w') as file:
                json.dump(data, file, indent=4)
            messagebox.showinfo("Save Scenario", f"Scenario saved as scenarios/{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save scenario: {str(e)}")
    
    def load_scenario(self):
        filename = simpledialog.askstring("Load Scenario", "Enter the name of the scenario file to load (without extension):")
        if not filename:
            return
            
        # Make sure filename ends with .json
        if not filename.endswith('.json'):
            filename += '.json'
            
        try:
            with open(f"scenarios/{filename}", 'r') as file:
                data = json.load(file)
                self.actions = data["actions"]
                self.update_action_list()
            messagebox.showinfo("Load Scenario", f"Scenario loaded from scenarios/{filename}")
        except FileNotFoundError:
            messagebox.showerror("Error", f"Scenario file not found: scenarios/{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load scenario: {str(e)}")
    
    def change_hotkey(self):
        new_hotkey = simpledialog.askstring("Change Hotkey", "Enter the new hotkey for coordinate selection (e.g., ctrl+shift):")
        if not new_hotkey:
            return
            
        try:
            # Remove old hotkey
            keyboard.remove_hotkey(self.current_hotkey)
            # Add new hotkey
            keyboard.add_hotkey(new_hotkey, self.start_coordinate_recording)
            self.current_hotkey = new_hotkey
            messagebox.showinfo("Change Hotkey", f"Hotkey changed to {new_hotkey}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to change hotkey: {str(e)}")
            # Re-add the old hotkey
            keyboard.add_hotkey(self.current_hotkey, self.start_coordinate_recording)
    
    # Action implementation methods
    def add_highlight_rectangle(self):
        # Show dialog to configure highlight rectangle
        dialog = tk.Toplevel(self.master)
        dialog.title("Highlight Rectangle")
        dialog.geometry("400x400")  # Make it taller to fit buttons
        dialog.transient(self.master)
        dialog.grab_set()
        
        content_frame = ttk.Frame(dialog)
        content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(content_frame, text="Use Ctrl+Shift to select start and end points of the rectangle").pack(pady=10)
        
        ttk.Label(content_frame, text="Message to display:").pack(pady=5)
        message_entry = ttk.Entry(content_frame, width=40)
        message_entry.pack(pady=5)
        
        ttk.Label(content_frame, text="Rectangle color:").pack(pady=5)
        color_var = tk.StringVar(value="green")
        ttk.Combobox(content_frame, textvariable=color_var, values=["green", "red", "blue", "yellow"]).pack(pady=5)
        
        ttk.Label(content_frame, text="Line thickness (pixels):").pack(pady=5)
        thickness_var = tk.IntVar(value=3)
        ttk.Spinbox(content_frame, from_=1, to=10, textvariable=thickness_var).pack(pady=5)
        
        wait_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(content_frame, text="Wait for click in rectangle", variable=wait_var).pack(pady=5)
        
        text_input_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(content_frame, text="Wait for text input in rectangle", variable=text_input_var).pack(pady=5)
        
        # Start with dummy coordinates - will be updated by the hotkey function
        self.temp_coordinates = {"start": (0, 0), "end": (0, 0)}
        
        ttk.Label(content_frame, text="Current coordinates:").pack(pady=5)
        coords_label = ttk.Label(content_frame, text="Not set yet - use hotkey to select")
        coords_label.pack(pady=5)
        
        def update_coords():
            if hasattr(self, 'temp_coordinates') and self.temp_coordinates["start"] != (0, 0):
                coords_label.config(text=f"Start: {self.temp_coordinates['start']}, End: {self.temp_coordinates['end']}")
            dialog.after(500, update_coords)
        
        update_coords()
        
        def on_ok():
            data = {
                "coordinates": self.temp_coordinates,
                "message": message_entry.get(),
                "color": color_var.get(),
                "thickness": thickness_var.get(),
                "wait_for_click": wait_var.get(),
                "wait_for_text": text_input_var.get()
            }
            
            details = f"Coords: {self.temp_coordinates['start']} to {self.temp_coordinates['end']}, Color: {color_var.get()}"
            if wait_var.get():
                details += ", Wait for click"
            if text_input_var.get():
                details += ", Wait for text input"
                
            self.add_action("Highlight Rectangle", details, data)
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        # Make sure the button frame is at the bottom
        buttons_frame = ttk.Frame(dialog)
        buttons_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=15)
        ttk.Button(buttons_frame, text="OK", command=on_ok, width=15).pack(side=tk.LEFT, padx=10)
        ttk.Button(buttons_frame, text="Cancel", command=on_cancel, width=15).pack(side=tk.RIGHT, padx=10)
    
    def edit_highlight_rectangle(self, index):
        action = self.actions[index]
        dialog = tk.Toplevel(self.master)
        dialog.title("Edit Highlight Rectangle")
        dialog.geometry("400x400")  # Make it taller to fit buttons
        dialog.transient(self.master)
        dialog.grab_set()
        
        content_frame = ttk.Frame(dialog)
        content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(content_frame, text="Use Ctrl+Shift to select start and end points of the rectangle").pack(pady=10)
        
        ttk.Label(content_frame, text="Message to display:").pack(pady=5)
        message_entry = ttk.Entry(content_frame, width=40)
        message_entry.insert(0, action["data"].get("message", ""))
        message_entry.pack(pady=5)
        
        ttk.Label(content_frame, text="Rectangle color:").pack(pady=5)
        color_var = tk.StringVar(value=action["data"].get("color", "green"))
        ttk.Combobox(content_frame, textvariable=color_var, values=["green", "red", "blue", "yellow"]).pack(pady=5)
        
        ttk.Label(content_frame, text="Line thickness (pixels):").pack(pady=5)
        thickness_var = tk.IntVar(value=action["data"].get("thickness", 3))
        ttk.Spinbox(content_frame, from_=1, to=10, textvariable=thickness_var).pack(pady=5)
        
        wait_var = tk.BooleanVar(value=action["data"].get("wait_for_click", False))
        ttk.Checkbutton(content_frame, text="Wait for click in rectangle", variable=wait_var).pack(pady=5)
        
        text_input_var = tk.BooleanVar(value=action["data"].get("wait_for_text", False))
        ttk.Checkbutton(content_frame, text="Wait for text input in rectangle", variable=text_input_var).pack(pady=5)
        
        # Use existing coordinates
        self.temp_coordinates = action["data"]["coordinates"]
        
        ttk.Label(content_frame, text="Current coordinates:").pack(pady=5)
        coords_text = f"Start: {self.temp_coordinates['start']}, End: {self.temp_coordinates['end']}"
        coords_label = ttk.Label(content_frame, text=coords_text)
        coords_label.pack(pady=5)
        
        def update_coords():
            if hasattr(self, 'temp_coordinates'):
                coords_label.config(text=f"Start: {self.temp_coordinates['start']}, End: {self.temp_coordinates['end']}")
            dialog.after(500, update_coords)
        
        update_coords()
        
        def on_ok():
            data = {
                "coordinates": self.temp_coordinates,
                "message": message_entry.get(),
                "color": color_var.get(),
                "thickness": thickness_var.get(),
                "wait_for_click": wait_var.get(),
                "wait_for_text": text_input_var.get()
            }
            
            details = f"Coords: {self.temp_coordinates['start']} to {self.temp_coordinates['end']}, Color: {color_var.get()}"
            if wait_var.get():
                details += ", Wait for click"
            if text_input_var.get():
                details += ", Wait for text input"
                
            self.actions[index] = {
                "type": "Highlight Rectangle",
                "details": details,
                "data": data
            }
            self.update_action_list()
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        # Make sure the button frame is at the bottom
        buttons_frame = ttk.Frame(dialog)
        buttons_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=15)
        ttk.Button(buttons_frame, text="OK", command=on_ok, width=15).pack(side=tk.LEFT, padx=10)
        ttk.Button(buttons_frame, text="Cancel", command=on_cancel, width=15).pack(side=tk.RIGHT, padx=10)
    
    def add_left_click(self):
        dialog = tk.Toplevel(self.master)
        dialog.title("Left Mouse Click")
        dialog.geometry("300x200")
        dialog.transient(self.master)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Press the hotkey, then click where you want\nthe left mouse click to be performed").pack(pady=10)
        
        # Start with dummy coordinates - will be updated by the hotkey function
        self.temp_coordinates = {"x": 0, "y": 0}
        
        ttk.Label(dialog, text="Current coordinates:").pack(pady=5)
        coords_label = ttk.Label(dialog, text="Not set yet - use hotkey to select")
        coords_label.pack(pady=5)
        
        def update_coords():
            if hasattr(self, 'temp_coordinates') and self.temp_coordinates["x"] != 0:
                coords_label.config(text=f"X: {self.temp_coordinates['x']}, Y: {self.temp_coordinates['y']}")
            dialog.after(500, update_coords)
        
        update_coords()
        
        def on_ok():
            data = {
                "coordinates": self.temp_coordinates
            }
            
            details = f"At position: ({self.temp_coordinates['x']}, {self.temp_coordinates['y']})"
            self.add_action("Left Mouse Click", details, data)
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        buttons_frame = ttk.Frame(dialog)
        buttons_frame.pack(side=tk.BOTTOM, pady=15)
        ttk.Button(buttons_frame, text="OK", command=on_ok, width=10).pack(side=tk.LEFT, padx=10)
        ttk.Button(buttons_frame, text="Cancel", command=on_cancel, width=10).pack(side=tk.LEFT, padx=10)
    
    def edit_left_click(self, index):
        action = self.actions[index]
        dialog = tk.Toplevel(self.master)
        dialog.title("Edit Left Mouse Click")
        dialog.geometry("300x200")
        dialog.transient(self.master)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Press the hotkey, then click where you want\nthe left mouse click to be performed").pack(pady=10)
        
        # Use existing coordinates
        self.temp_coordinates = action["data"]["coordinates"]
        
        ttk.Label(dialog, text="Current coordinates:").pack(pady=5)
        coords_text = f"X: {self.temp_coordinates['x']}, Y: {self.temp_coordinates['y']}"
        coords_label = ttk.Label(dialog, text=coords_text)
        coords_label.pack(pady=5)
        
        def update_coords():
            if hasattr(self, 'temp_coordinates'):
                coords_label.config(text=f"X: {self.temp_coordinates['x']}, Y: {self.temp_coordinates['y']}")
            dialog.after(500, update_coords)
        
        update_coords()
        
        def on_ok():
            data = {
                "coordinates": self.temp_coordinates
            }
            
            details = f"At position: ({self.temp_coordinates['x']}, {self.temp_coordinates['y']})"
            self.actions[index] = {
                "type": "Left Mouse Click",
                "details": details,
                "data": data
            }
            self.update_action_list()
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        buttons_frame = ttk.Frame(dialog)
        buttons_frame.pack(side=tk.BOTTOM, pady=15)
        ttk.Button(buttons_frame, text="OK", command=on_ok, width=10).pack(side=tk.LEFT, padx=10)
        ttk.Button(buttons_frame, text="Cancel", command=on_cancel, width=10).pack(side=tk.LEFT, padx=10)
    
    def add_right_click(self):
        dialog = tk.Toplevel(self.master)
        dialog.title("Right Mouse Click")
        dialog.geometry("300x200")
        dialog.transient(self.master)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Press the hotkey, then click where you want\nthe right mouse click to be performed").pack(pady=10)
        
        # Start with dummy coordinates - will be updated by the hotkey function
        self.temp_coordinates = {"x": 0, "y": 0}
        
        ttk.Label(dialog, text="Current coordinates:").pack(pady=5)
        coords_label = ttk.Label(dialog, text="Not set yet - use hotkey to select")
        coords_label.pack(pady=5)
        
        def update_coords():
            if hasattr(self, 'temp_coordinates') and self.temp_coordinates["x"] != 0:
                coords_label.config(text=f"X: {self.temp_coordinates['x']}, Y: {self.temp_coordinates['y']}")
            dialog.after(500, update_coords)
        
        update_coords()
        
        def on_ok():
            data = {
                "coordinates": self.temp_coordinates
            }
            
            details = f"At position: ({self.temp_coordinates['x']}, {self.temp_coordinates['y']})"
            self.add_action("Right Mouse Click", details, data)
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        buttons_frame = ttk.Frame(dialog)
        buttons_frame.pack(side=tk.BOTTOM, pady=15)
        ttk.Button(buttons_frame, text="OK", command=on_ok, width=10).pack(side=tk.LEFT, padx=10)
        ttk.Button(buttons_frame, text="Cancel", command=on_cancel, width=10).pack(side=tk.LEFT, padx=10)
    
    def edit_right_click(self, index):
        action = self.actions[index]
        dialog = tk.Toplevel(self.master)
        dialog.title("Edit Right Mouse Click")
        dialog.geometry("300x200")
        dialog.transient(self.master)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Press the hotkey, then click where you want\nthe right mouse click to be performed").pack(pady=10)
        
        # Use existing coordinates
        self.temp_coordinates = action["data"]["coordinates"]
        
        ttk.Label(dialog, text="Current coordinates:").pack(pady=5)
        coords_text = f"X: {self.temp_coordinates['x']}, Y: {self.temp_coordinates['y']}"
        coords_label = ttk.Label(dialog, text=coords_text)
        coords_label.pack(pady=5)
        
        def update_coords():
            if hasattr(self, 'temp_coordinates'):
                coords_label.config(text=f"X: {self.temp_coordinates['x']}, Y: {self.temp_coordinates['y']}")
            dialog.after(500, update_coords)
        
        update_coords()
        
        def on_ok():
            data = {
                "coordinates": self.temp_coordinates
            }
            
            details = f"At position: ({self.temp_coordinates['x']}, {self.temp_coordinates['y']})"
            self.actions[index] = {
                "type": "Right Mouse Click",
                "details": details,
                "data": data
            }
            self.update_action_list()
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        buttons_frame = ttk.Frame(dialog)
        buttons_frame.pack(side=tk.BOTTOM, pady=15)
        ttk.Button(buttons_frame, text="OK", command=on_ok, width=10).pack(side=tk.LEFT, padx=10)
        ttk.Button(buttons_frame, text="Cancel", command=on_cancel, width=10).pack(side=tk.LEFT, padx=10)
    
    def add_wait(self):
        seconds = simpledialog.askfloat("Wait", "Enter the number of seconds to wait:", minvalue=0.1, maxvalue=300)
        if seconds is not None:
            data = {"seconds": seconds}
            details = f"Wait for {seconds} seconds"
            self.add_action("Wait", details, data)
    
    def edit_wait(self, index):
        action = self.actions[index]
        seconds = simpledialog.askfloat("Edit Wait", "Enter the number of seconds to wait:", 
                                      initialvalue=action["data"]["seconds"], minvalue=0.1, maxvalue=300)
        if seconds is not None:
            data = {"seconds": seconds}
            details = f"Wait for {seconds} seconds"
            self.actions[index] = {
                "type": "Wait",
                "details": details,
                "data": data
            }
    
    def add_insert_text(self):
        dialog = tk.Toplevel(self.master)
        dialog.title("Insert Text")
        dialog.geometry("400x200")
        dialog.transient(self.master)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Enter the text to insert:").pack(pady=10)
        
        text_entry = ttk.Entry(dialog, width=40)
        text_entry.pack(pady=5)
        
        ttk.Label(dialog, text="Use ${variable_name} to insert variable values").pack(pady=5)
        
        def on_ok():
            text = text_entry.get()
            if not text:
                messagebox.showwarning("Warning", "Text cannot be empty")
                return
                
            data = {"text": text}
            details = f"Text: {text}"
            self.add_action("Insert Text", details, data)
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        buttons_frame = ttk.Frame(dialog)
        buttons_frame.pack(side=tk.BOTTOM, pady=15)
        ttk.Button(buttons_frame, text="OK", command=on_ok, width=10).pack(side=tk.LEFT, padx=10)
        ttk.Button(buttons_frame, text="Cancel", command=on_cancel, width=10).pack(side=tk.LEFT, padx=10)
    
    def edit_insert_text(self, index):
        action = self.actions[index]
        dialog = tk.Toplevel(self.master)
        dialog.title("Edit Insert Text")
        dialog.geometry("400x200")
        dialog.transient(self.master)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Enter the text to insert:").pack(pady=10)
        
        text_entry = ttk.Entry(dialog, width=40)
        text_entry.insert(0, action["data"]["text"])
        text_entry.pack(pady=5)
        
        ttk.Label(dialog, text="Use ${variable_name} to insert variable values").pack(pady=5)
        
        def on_ok():
            text = text_entry.get()
            if not text:
                messagebox.showwarning("Warning", "Text cannot be empty")
                return
                
            data = {"text": text}
            details = f"Text: {text}"
            self.actions[index] = {
                "type": "Insert Text",
                "details": details,
                "data": data
            }
            self.update_action_list()
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        buttons_frame = ttk.Frame(dialog)
        buttons_frame.pack(side=tk.BOTTOM, pady=15)
        ttk.Button(buttons_frame, text="OK", command=on_ok, width=10).pack(side=tk.LEFT, padx=10)
        ttk.Button(buttons_frame, text="Cancel", command=on_cancel, width=10).pack(side=tk.LEFT, padx=10)
    
    def add_store_variable(self):
        dialog = tk.Toplevel(self.master)
        dialog.title("Store Variable")
        dialog.geometry("400x300")
        dialog.transient(self.master)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Variable name:").pack(pady=10)
        
        var_name_entry = ttk.Entry(dialog, width=30)
        var_name_entry.pack(pady=5)
        
        source_var = tk.StringVar(value="value")
        
        ttk.Radiobutton(dialog, text="Specific value", variable=source_var, value="value").pack(anchor=tk.W, padx=20, pady=5)
        ttk.Radiobutton(dialog, text="Current clipboard content", variable=source_var, value="clipboard").pack(anchor=tk.W, padx=20, pady=5)
        
        ttk.Label(dialog, text="Value (if 'Specific value' is selected):").pack(pady=5)
        
        value_entry = ttk.Entry(dialog, width=30)
        value_entry.pack(pady=5)
        
        def on_ok():
            var_name = var_name_entry.get()
            if not var_name:
                messagebox.showwarning("Warning", "Variable name cannot be empty")
                return
                
            source = source_var.get()
            value = value_entry.get() if source == "value" else ""
            
            data = {
                "name": var_name,
                "source": source,
                "value": value
            }
            
            details = f"Name: {var_name}, Source: {source}"
            if source == "value":
                details += f", Value: {value}"
                
            self.add_action("Store Variable", details, data)
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        buttons_frame = ttk.Frame(dialog)
        buttons_frame.pack(side=tk.BOTTOM, pady=15)
        ttk.Button(buttons_frame, text="OK", command=on_ok, width=10).pack(side=tk.LEFT, padx=10)
        ttk.Button(buttons_frame, text="Cancel", command=on_cancel, width=10).pack(side=tk.LEFT, padx=10)
    
    def edit_store_variable(self, index):
        action = self.actions[index]
        dialog = tk.Toplevel(self.master)
        dialog.title("Edit Store Variable")
        dialog.geometry("400x300")
        dialog.transient(self.master)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Variable name:").pack(pady=10)
        
        var_name_entry = ttk.Entry(dialog, width=30)
        var_name_entry.insert(0, action["data"]["name"])
        var_name_entry.pack(pady=5)
        
        source_var = tk.StringVar(value=action["data"]["source"])
        
        ttk.Radiobutton(dialog, text="Specific value", variable=source_var, value="value").pack(anchor=tk.W, padx=20, pady=5)
        ttk.Radiobutton(dialog, text="Current clipboard content", variable=source_var, value="clipboard").pack(anchor=tk.W, padx=20, pady=5)
        
        ttk.Label(dialog, text="Value (if 'Specific value' is selected):").pack(pady=5)
        
        value_entry = ttk.Entry(dialog, width=30)
        if action["data"]["source"] == "value":
            value_entry.insert(0, action["data"]["value"])
        value_entry.pack(pady=5)
        
        def on_ok():
            var_name = var_name_entry.get()
            if not var_name:
                messagebox.showwarning("Warning", "Variable name cannot be empty")
                return
                
            source = source_var.get()
            value = value_entry.get() if source == "value" else ""
            
            data = {
                "name": var_name,
                "source": source,
                "value": value
            }
            
            details = f"Name: {var_name}, Source: {source}"
            if source == "value":
                details += f", Value: {value}"
                
            self.actions[index] = {
                "type": "Store Variable",
                "details": details,
                "data": data
            }
            self.update_action_list()
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        buttons_frame = ttk.Frame(dialog)
        buttons_frame.pack(side=tk.BOTTOM, pady=15)
        ttk.Button(buttons_frame, text="OK", command=on_ok, width=10).pack(side=tk.LEFT, padx=10)
        ttk.Button(buttons_frame, text="Cancel", command=on_cancel, width=10).pack(side=tk.LEFT, padx=10)
    
    def add_copy_to_clipboard(self):
        details = "Copy selected text to clipboard (Ctrl+C)"
        data = {}
        self.add_action("Copy to Clipboard", details, data)
    
    def add_paste_from_clipboard(self):
        details = "Paste from clipboard (Ctrl+V)"
        data = {}
        self.add_action("Paste from Clipboard", details, data)
    
    def add_select_all(self):
        details = "Select all (Ctrl+A)"
        data = {}
        self.add_action("Select All", details, data)
    
    def add_press_key(self):
        dialog = tk.Toplevel(self.master)
        dialog.title("Press Key")
        dialog.geometry("300x350")  # Make it taller to fit buttons
        dialog.transient(self.master)
        dialog.grab_set()
        
        content_frame = ttk.Frame(dialog)
        content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(content_frame, text="Select key to press:").pack(pady=10)
        ttk.Label(content_frame, text="(Select a key below, then click OK to confirm)").pack(pady=5)
        
        # Create a frame for the radio buttons
        radio_frame = ttk.Frame(content_frame)
        radio_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        key_var = tk.StringVar(value="enter")
        keys = ["enter", "up", "down", "left", "right", "tab", "escape", "backspace"]
        
        for key in keys:
            ttk.Radiobutton(radio_frame, text=key.capitalize(), variable=key_var, value=key).pack(anchor=tk.W, padx=20, pady=2)
        
        def on_ok():
            key = key_var.get()
            data = {"key": key}
            details = f"Press key: {key}"
            self.add_action("Press Key", details, data)
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        # Make sure the button frame is at the bottom
        buttons_frame = ttk.Frame(dialog)
        buttons_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=15)
        ttk.Button(buttons_frame, text="OK", command=on_ok, width=15).pack(side=tk.LEFT, padx=10)
        ttk.Button(buttons_frame, text="Cancel", command=on_cancel, width=15).pack(side=tk.RIGHT, padx=10)
    
    def edit_press_key(self, index):
        action = self.actions[index]
        dialog = tk.Toplevel(self.master)
        dialog.title("Edit Press Key")
        dialog.geometry("300x350")  # Make it taller to fit buttons
        dialog.transient(self.master)
        dialog.grab_set()
        
        content_frame = ttk.Frame(dialog)
        content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(content_frame, text="Select key to press:").pack(pady=10)
        ttk.Label(content_frame, text="(Select a key below, then click OK to confirm)").pack(pady=5)
        
        # Create a frame for the radio buttons
        radio_frame = ttk.Frame(content_frame)
        radio_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        key_var = tk.StringVar(value=action["data"]["key"])
        keys = ["enter", "up", "down", "left", "right", "tab", "escape", "backspace"]
        
        for key in keys:
            ttk.Radiobutton(radio_frame, text=key.capitalize(), variable=key_var, value=key).pack(anchor=tk.W, padx=20, pady=2)
        
        def on_ok():
            key = key_var.get()
            data = {"key": key}
            details = f"Press key: {key}"
            self.actions[index] = {
                "type": "Press Key",
                "details": details,
                "data": data
            }
            self.update_action_list()
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        # Make sure the button frame is at the bottom
        buttons_frame = ttk.Frame(dialog)
        buttons_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=15)
        ttk.Button(buttons_frame, text="OK", command=on_ok, width=15).pack(side=tk.LEFT, padx=10)
        ttk.Button(buttons_frame, text="Cancel", command=on_cancel, width=15).pack(side=tk.RIGHT, padx=10)
    
    def add_info_message(self):
        dialog = tk.Toplevel(self.master)
        dialog.title("Info Message")
        dialog.geometry("400x200")
        dialog.transient(self.master)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Message to display:").pack(pady=10)
        
        message_entry = ttk.Entry(dialog, width=40)
        message_entry.pack(pady=5)
        
        speak_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(dialog, text="Read message aloud", variable=speak_var).pack(pady=5)
        
        def on_ok():
            message = message_entry.get()
            if not message:
                messagebox.showwarning("Warning", "Message cannot be empty")
                return
                
            data = {
                "message": message,
                "speak": speak_var.get()
            }
            
            details = f"Message: {message}"
            if speak_var.get():
                details += " (will be read aloud)"
                
            self.add_action("Info Message", details, data)
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        buttons_frame = ttk.Frame(dialog)
        buttons_frame.pack(side=tk.BOTTOM, pady=15)
        ttk.Button(buttons_frame, text="OK", command=on_ok, width=10).pack(side=tk.LEFT, padx=10)
        ttk.Button(buttons_frame, text="Cancel", command=on_cancel, width=10).pack(side=tk.LEFT, padx=10)
    
    def edit_info_message(self, index):
        action = self.actions[index]
        dialog = tk.Toplevel(self.master)
        dialog.title("Edit Info Message")
        dialog.geometry("400x200")
        dialog.transient(self.master)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Message to display:").pack(pady=10)
        
        message_entry = ttk.Entry(dialog, width=40)
        message_entry.insert(0, action["data"]["message"])
        message_entry.pack(pady=5)
        
        speak_var = tk.BooleanVar(value=action["data"].get("speak", False))
        ttk.Checkbutton(dialog, text="Read message aloud", variable=speak_var).pack(pady=5)
        
        def on_ok():
            message = message_entry.get()
            if not message:
                messagebox.showwarning("Warning", "Message cannot be empty")
                return
                
            data = {
                "message": message,
                "speak": speak_var.get()
            }
            
            details = f"Message: {message}"
            if speak_var.get():
                details += " (will be read aloud)"
                
            self.actions[index] = {
                "type": "Info Message",
                "details": details,
                "data": data
            }
            self.update_action_list()
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        buttons_frame = ttk.Frame(dialog)
        buttons_frame.pack(side=tk.BOTTOM, pady=15)
        ttk.Button(buttons_frame, text="OK", command=on_ok, width=10).pack(side=tk.LEFT, padx=10)
        ttk.Button(buttons_frame, text="Cancel", command=on_cancel, width=10).pack(side=tk.LEFT, padx=10)
    
    def add_show_form(self):
        dialog = tk.Toplevel(self.master)
        dialog.title("Show Form")
        dialog.geometry("500x400")
        dialog.transient(self.master)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Form Fields:").pack(pady=10)
        
        # Frame for the fields with scrollbar
        fields_frame = ttk.Frame(dialog)
        fields_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        canvas = tk.Canvas(fields_frame)
        scrollbar = ttk.Scrollbar(fields_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Store field entries for later use
        field_entries = []
        
        def add_field():
            field_frame = ttk.Frame(scrollable_frame)
            field_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(field_frame, text="Field Name:", width=10).pack(side=tk.LEFT, padx=5)
            name_entry = ttk.Entry(field_frame, width=15)
            name_entry.pack(side=tk.LEFT, padx=5)
            
            ttk.Label(field_frame, text="Description:", width=10).pack(side=tk.LEFT, padx=5)
            desc_entry = ttk.Entry(field_frame, width=15)
            desc_entry.pack(side=tk.LEFT, padx=5)
            
            def remove_field():
                field_frame.destroy()
                field_entries.remove((name_entry, desc_entry))
            
            ttk.Button(field_frame, text="X", width=2, command=remove_field).pack(side=tk.LEFT, padx=5)
            
            field_entries.append((name_entry, desc_entry))
        
        # Add a couple of default fields
        add_field()
        add_field()
        
        ttk.Button(dialog, text="Add Field", command=add_field).pack(pady=5)
        
        def on_ok():
            fields = []
            for name_entry, desc_entry in field_entries:
                name = name_entry.get().strip()
                desc = desc_entry.get().strip()
                
                if name:  # Only add if name is not empty
                    fields.append({
                        "name": name,
                        "description": desc
                    })
            
            if not fields:
                messagebox.showwarning("Warning", "Form must have at least one field")
                return
                
            data = {"fields": fields}
            
            field_names = [field["name"] for field in fields]
            details = f"Form with fields: {', '.join(field_names)}"
            
            self.add_action("Show Form", details, data)
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        buttons_frame = ttk.Frame(dialog)
        buttons_frame.pack(side=tk.BOTTOM, pady=15)
        ttk.Button(buttons_frame, text="OK", command=on_ok, width=10).pack(side=tk.LEFT, padx=10)
        ttk.Button(buttons_frame, text="Cancel", command=on_cancel, width=10).pack(side=tk.LEFT, padx=10)
    
    def edit_show_form(self, index):
        action = self.actions[index]
        dialog = tk.Toplevel(self.master)
        dialog.title("Edit Show Form")
        dialog.geometry("500x400")
        dialog.transient(self.master)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Form Fields:").pack(pady=10)
        
        # Frame for the fields with scrollbar
        fields_frame = ttk.Frame(dialog)
        fields_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        canvas = tk.Canvas(fields_frame)
        scrollbar = ttk.Scrollbar(fields_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Store field entries for later use
        field_entries = []
        
        def add_field(name="", desc=""):
            field_frame = ttk.Frame(scrollable_frame)
            field_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(field_frame, text="Field Name:", width=10).pack(side=tk.LEFT, padx=5)
            name_entry = ttk.Entry(field_frame, width=15)
            name_entry.insert(0, name)
            name_entry.pack(side=tk.LEFT, padx=5)
            
            ttk.Label(field_frame, text="Description:", width=10).pack(side=tk.LEFT, padx=5)
            desc_entry = ttk.Entry(field_frame, width=15)
            desc_entry.insert(0, desc)
            desc_entry.pack(side=tk.LEFT, padx=5)
            
            def remove_field():
                field_frame.destroy()
                field_entries.remove((name_entry, desc_entry))
            
            ttk.Button(field_frame, text="X", width=2, command=remove_field).pack(side=tk.LEFT, padx=5)
            
            field_entries.append((name_entry, desc_entry))
        
        # Add existing fields
        for field in action["data"]["fields"]:
            add_field(field["name"], field["description"])
        
        # If no fields, add one empty field
        if not action["data"]["fields"]:
            add_field()
        
        ttk.Button(dialog, text="Add Field", command=lambda: add_field()).pack(pady=5)
        
        def on_ok():
            fields = []
            for name_entry, desc_entry in field_entries:
                name = name_entry.get().strip()
                desc = desc_entry.get().strip()
                
                if name:  # Only add if name is not empty
                    fields.append({
                        "name": name,
                        "description": desc
                    })
            
            if not fields:
                messagebox.showwarning("Warning", "Form must have at least one field")
                return
                
            data = {"fields": fields}
            
            field_names = [field["name"] for field in fields]
            details = f"Form with fields: {', '.join(field_names)}"
            
            self.actions[index] = {
                "type": "Show Form",
                "details": details,
                "data": data
            }
            self.update_action_list()
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        buttons_frame = ttk.Frame(dialog)
        buttons_frame.pack(side=tk.BOTTOM, pady=15)
        ttk.Button(buttons_frame, text="OK", command=on_ok, width=10).pack(side=tk.LEFT, padx=10)
        ttk.Button(buttons_frame, text="Cancel", command=on_cancel, width=10).pack(side=tk.LEFT, padx=10)


    def add_execute_command(self):
        dialog = tk.Toplevel(self.master)
        dialog.title("Execute Command")
        dialog.geometry("500x300")
        dialog.transient(self.master)
        dialog.grab_set()

        ttk.Label(dialog, text="Select command type:").pack(pady=10)

        command_type_var = tk.StringVar(value="cmd")
        ttk.Radiobutton(dialog, text="Command Prompt (cmd)", variable=command_type_var, value="cmd").pack(anchor=tk.W, padx=20, pady=5)
        ttk.Radiobutton(dialog, text="PowerShell", variable=command_type_var, value="powershell").pack(anchor=tk.W, padx=20, pady=5)

        ttk.Label(dialog, text="Enter command(s) to execute (one per line):").pack(pady=10)

        command_text = tk.Text(dialog, width=50, height=8)
        command_text.pack(pady=5)

        def on_ok():
            command_type = command_type_var.get()
            commands = command_text.get("1.0", tk.END).strip()
            if not commands:
                messagebox.showwarning("Warning", "Commands cannot be empty")
                return

            data = {
                "command_type": command_type,
                "commands": commands
            }
            replaced_commands = commands.replace('\n', '; ')
            details = f"Execute {command_type}: {replaced_commands}"

            self.add_action("Execute Command", details, data)
            dialog.destroy()

        def on_cancel():
            dialog.destroy()

        buttons_frame = ttk.Frame(dialog)
        buttons_frame.pack(side=tk.BOTTOM, pady=15)
        ttk.Button(buttons_frame, text="OK", command=on_ok, width=10).pack(side=tk.LEFT, padx=10)
        ttk.Button(buttons_frame, text="Cancel", command=on_cancel, width=10).pack(side=tk.LEFT, padx=10)        

    def edit_execute_command(self, index):
        action = self.actions[index]
        dialog = tk.Toplevel(self.master)
        dialog.title("Edit Execute Command")
        dialog.geometry("500x300")
        dialog.transient(self.master)
        dialog.grab_set()

        ttk.Label(dialog, text="Select command type:").pack(pady=10)

        command_type_var = tk.StringVar(value=action["data"]["command_type"])
        ttk.Radiobutton(dialog, text="Command Prompt (cmd)", variable=command_type_var, value="cmd").pack(anchor=tk.W, padx=20, pady=5)
        ttk.Radiobutton(dialog, text="PowerShell", variable=command_type_var, value="powershell").pack(anchor=tk.W, padx=20, pady=5)

        ttk.Label(dialog, text="Enter command(s) to execute (one per line):").pack(pady=10)

        command_text = tk.Text(dialog, width=50, height=8)
        command_text.insert("1.0", action["data"]["commands"])
        command_text.pack(pady=5)

        def on_ok():
            command_type = command_type_var.get()
            commands = command_text.get("1.0", tk.END).strip()
            if not commands:
                messagebox.showwarning("Warning", "Commands cannot be empty")
                return

            data = {
                "command_type": command_type,
                "commands": commands
            }

            replaced_commands = commands.replace('\n', '; ')
            details = f"Execute {command_type}: {replaced_commands}"

            self.actions[index] = {
                "type": "Execute Command",
                "details": details,
                "data": data
            }
            self.update_action_list()
            dialog.destroy()

        def on_cancel():
            dialog.destroy()

        buttons_frame = ttk.Frame(dialog)
        buttons_frame.pack(side=tk.BOTTOM, pady=15)
        ttk.Button(buttons_frame, text="OK", command=on_ok, width=10).pack(side=tk.LEFT, padx=10)
        ttk.Button(buttons_frame, text="Cancel", command=on_cancel, width=10).pack(side=tk.LEFT, padx=10)        

def main():
    root = tk.Tk()
    app = ScenarioCreator(root)
    root.mainloop()

if __name__ == "__main__":
    main()