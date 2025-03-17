import configparser
import os
import sys
import tkinter as tk
from tkinter import filedialog

CONFIG_FILE = "PokemonStadiumSync.cfg"

DEFAULT_CONFIG = {
    "General": {"stay_open": "True", "run_minimized": "False"},
    "Ports": {
        "RetroarchTransferPak1": "",  # TransferPak Port1 - For Pokemon Stadium
        "RetroarchTransferPak2": ""   # TransferPak Port2 - For Pokemon Stadium 2
    },
    "Directories": {
        "base_dir": "C:/Program Files (x86)/RetroArch",  # Base Directory
        "gb_dir": "saves/Nintendo - Game Boy",  # Subfolder for GB saves
        "gba_dir": "saves/Nintendo - Game Boy Advance",  # Subfolder for GBA saves
        "sav_dir": "saves/TransferPak",  # Subfolder for TransferPak
        "gbrom_dir": "games/Nintendo - Game Boy"  # Subfolder for GB ROMs
    },
    "StadiumROMs": {
        "Stadium 1": "Pokemon Stadium (USA).n64",  # N64 ROM - Pokemon Stadium ROM (.n64/.z64)
        "Stadium 2": "Pokemon Stadium 2 (USA).n64"  # N64 ROM - Pokemon Stadium 2 ROM (.n64/.z64)
    },
    "GBSlots": {
        "Green": "Pokemon - Green Version",  # GB Slot1 - Pokemon - Green Version (.srm)
        "Red": "Pokemon - Red Version (USA, Europe) (SGB Enhanced)",  # GB Slot2 - Pokemon - Red Version (.srm)
        "Blue": "Pokemon - Blue Version (USA, Europe) (SGB Enhanced)",  # GB Slot3 - Pokemon - Blue Version (.srm)
        "Yellow": "Pokemon - Yellow Version - Special Pikachu Edition (Pokemon Playable Yellow) (v1.0) (alt)",  # GB Slot4 - Pokemon - Yellow Version (.srm)
        "Gold": "Pokemon - Gold Version (USA, Europe) (SGB Enhanced) (GB Compatible)",  # GB Slot5 - Pokemon - Gold Version (.srm)
        "Silver": "Pokemon - Silver Version (USA, Europe) (SGB Enhanced) (GB Compatible)",  # GB Slot6 - Pokemon - Silver Version (.srm)
        "Crystal": "Pokemon - Crystal Version (USA, Europe) (Rev 1)"  # GB Slot7 - Pokemon - Crystal Version (.srm)
    },
    "GBASlots": {
        "Ruby": "Pokemon - Ruby Version (USA, Europe) (Rev 2)",  # GBA Slot1 - Pokemon - Ruby Version (.srm)
        "Sapphire": "Pokemon - Sapphire Version (USA, Europe) (Rev 2)",  # GBA Slot2 - Pokemon - Sapphire Version (.srm)
        "Emerald": "Pokemon - Emerald Version (USA, Europe)",  # GBA Slot3 - Pokemon - Emerald Version (.srm)
        "FireRed": "Pokemon - FireRed Version (USA, Europe)",  # GBA Slot4 - Pokemon - FireRed Version (.srm)
        "LeafGreen": "Pokemon - LeafGreen Version (USA, Europe)"  # GBA Slot5 - Pokemon - LeafGreen Version (.srm)
    }
}

status_labels = {}  # Dictionary to hold status indicators

### ==================  Browse Function ================== ###
def browse_directory(initial_dir):
    """Opens a directory selection dialog."""
    return filedialog.askdirectory(initialdir=initial_dir)

def browse_file(initial_dir, filetypes):
    """Opens a file selection dialog."""
    return filedialog.askopenfilename(initialdir=initial_dir, filetypes=filetypes)

def browse_path(entry_key):
    """Opens a file/folder selection dialog based on the entry_key."""
    global last_found, last_found_type

    initial_dir = os.path.normpath(entries["base_dir"].get().strip())
    path = None

    if entry_key == "base_dir":
        path = browse_directory(initial_dir)
        last_found_type = "base_dir"
    elif entry_key in ["gb_dir", "gba_dir", "sav_dir", "gbrom_dir"]:
        subfolder = entries[entry_key].get().strip()
        initial_subdir = os.path.join(initial_dir, os.path.normpath(subfolder))
        path = browse_directory(initial_subdir)
        last_found_type = "subfolder"
    elif entry_key in ["Stadium 1", "Stadium 2"]:
        sav_dir = entries["sav_dir"].get().strip()
        initial_sav_dir = os.path.join(initial_dir, os.path.normpath(sav_dir))
        path = browse_file(initial_sav_dir, [("N64 ROMs", "*.n64 *.z64")])
        last_found_type = "stadium_rom"
    elif entry_key in ["Green", "Red", "Blue", "Yellow", "Gold", "Silver", "Crystal"]:
        gb_dir = entries["gb_dir"].get().strip()
        initial_gb_dir = os.path.join(initial_dir, os.path.normpath(gb_dir))
        path = browse_file(initial_gb_dir, [("GB Save Files", "*.srm")])
        last_found_type = "gb_slot"
    elif entry_key in ["Ruby", "Sapphire", "Emerald", "FireRed", "LeafGreen"]:
        gba_dir = entries["gba_dir"].get().strip()
        initial_gba_dir = os.path.join(initial_dir, os.path.normpath(gba_dir))
        path = browse_file(initial_gba_dir, [("GBA Save Files", "*.srm")])
        last_found_type = "gba_slot"

    if path:
        last_found = os.path.normpath(path)
        normalized_path = last_found.replace("\\", "/")

        if last_found_type in ["gb_slot", "gba_slot"]:
            normalized_path = os.path.splitext(os.path.basename(normalized_path))[0]
        elif last_found_type == "stadium_rom":
            normalized_path = os.path.basename(normalized_path)

        entries[entry_key].delete(0, tk.END)
        entries[entry_key].insert(0, normalized_path)

        update_status_icons()
        detect_and_set_base_directory(last_found)

        if last_found_type == "subfolder":
            trim_base_dir_from_subfolders(initial_dir)

        auto_populate_subfolder()

### ==================  Search Button ================== ###
def search_for_files():
    base_dir = entries["base_dir"].get().strip()
    if not os.path.exists(base_dir):
        return print("❌ Search Aborted: Base directory does not exist.")

    file_index, folder_counts = {}, {}

    # Indexing files
    for root, _, files in os.walk(base_dir):
        for file in files:
            rel_path = os.path.relpath(os.path.join(root, file), base_dir).replace("\\", "/")
            file_index[file.lower()] = (rel_path, file)
            if file.lower().endswith((".gb", ".gbc")):
                folder_counts[root] = folder_counts.get(root, 0) + 1

    if folder_counts:
        best_gbrom_dir = max(folder_counts, key=folder_counts.get)
        current_gbrom_dir = os.path.join(base_dir, entries["gbrom_dir"].get().strip())
        if not os.path.exists(current_gbrom_dir):
            entries["gbrom_dir"].delete(0, tk.END)
            entries["gbrom_dir"].insert(0, os.path.relpath(best_gbrom_dir, base_dir).replace("\\", "/"))

    # Search for missing GB/GBA saves and populate subfolder if needed
    for key in ["Green", "Red", "Blue", "Yellow", "Gold", "Silver", "Crystal"]:
        current_value = entries[key].get().strip()
        gb_subfolder = entries["gb_dir"].get().strip()
        full_path = os.path.join(base_dir, gb_subfolder, current_value + ".srm").replace("\\", "/")

        if not os.path.exists(full_path):
            potential_match = next((f for f in file_index if f.startswith(f"pokemon - {key.lower()} version") and f.endswith(".srm")), None)
            if potential_match:
                found_path = file_index[potential_match][0]
                entries[key].delete(0, tk.END)
                entries[key].insert(0, os.path.splitext(file_index[potential_match][1])[0])

                # Update GB subfolder if invalid
                detected_gb_dir = os.path.dirname(found_path)
                if not os.path.exists(os.path.join(base_dir, gb_subfolder)):
                    entries["gb_dir"].delete(0, tk.END)
                    entries["gb_dir"].insert(0, detected_gb_dir)

    for key in ["Ruby", "Sapphire", "Emerald", "FireRed", "LeafGreen"]:
        current_value = entries[key].get().strip()
        gba_subfolder = entries["gba_dir"].get().strip()
        full_path = os.path.join(base_dir, gba_subfolder, current_value + ".srm").replace("\\", "/")

        if not os.path.exists(full_path):
            potential_match = next((f for f in file_index if f.startswith(f"pokemon - {key.lower()} version") and f.endswith(".srm")), None)
            if potential_match:
                found_path = file_index[potential_match][0]
                entries[key].delete(0, tk.END)
                entries[key].insert(0, os.path.splitext(file_index[potential_match][1])[0])

                # Update GBA subfolder if invalid
                detected_gba_dir = os.path.dirname(found_path)
                if not os.path.exists(os.path.join(base_dir, gba_subfolder)):
                    entries["gba_dir"].delete(0, tk.END)
                    entries["gba_dir"].insert(0, detected_gba_dir)

    # Find N64 ROMs and set TransferPak subfolder if needed
    for stadium, stadium_prefix in [("Stadium 1", "pokemon stadium"), ("Stadium 2", "pokemon stadium 2")]:
        current_value = entries[stadium].get().strip()
        sav_subfolder = entries["sav_dir"].get().strip()
        full_path = os.path.join(base_dir, sav_subfolder, current_value).replace("\\", "/")

        if not os.path.exists(full_path):
            potential_match = next((f for f in file_index if f.startswith(stadium_prefix) and f.endswith((".n64", ".z64"))), None)
            if potential_match:
                found_path = file_index[potential_match][0]
                entries[stadium].delete(0, tk.END)
                entries[stadium].insert(0, file_index[potential_match][1])

                # Update sav subfolder if invalid
                detected_sav_dir = os.path.dirname(found_path)
                if not os.path.exists(os.path.join(base_dir, sav_subfolder)):
                    entries["sav_dir"].delete(0, tk.END)
                    entries["sav_dir"].insert(0, detected_sav_dir)

    update_status_icons()

### ==================  Check if path exist ================== ###
def check_path_existence(path):
    """Returns whether a path exists."""
    return os.path.exists(os.path.normpath(path))

### ==================  Update status icons ================== ###
def update_entry_status(key, path, exists):
    """Updates the status icon for a given entry."""
    if key in ["RetroarchTransferPak1", "RetroarchTransferPak2"]:
        # Default to yellow warning if no game is selected
        status_icon = "⚠️"
        status_color = "yellow"

        # If a game is selected, match the status of its save slot
        selected_game = entries[key].get().strip()
        if selected_game and selected_game in status_labels:
            game_status_icon = status_labels[selected_game].cget("text")
            game_status_color = status_labels[selected_game].cget("fg")
            status_icon, status_color = game_status_icon, game_status_color

        status_labels[key].config(text=status_icon, fg=status_color)

    else:
        status_labels[key].config(text="⚠️" if not exists else "✔️", fg="red" if not exists else "green")

def update_status_icons():
    """Updates status icons based on path existence and dropdown selections."""
    base_dir = entries["base_dir"].get().strip()

    for key, entry in entries.items():
        try:
            if isinstance(entry, tk.Entry):  # Handle text fields
                path = entry.get().strip()

                if not path:  # Skip empty paths
                    update_entry_status(key, None, False)
                    continue

                path = os.path.normpath(path)

                if key in ["gb_dir", "gba_dir", "sav_dir", "gbrom_dir"]:  # Subfolders
                    path = os.path.join(base_dir, path)
                elif key in ["Stadium 1", "Stadium 2"]:  # N64 ROMs
                    path = os.path.join(base_dir, entries["sav_dir"].get().strip(), path)
                elif key in ["Green", "Red", "Blue", "Yellow", "Gold", "Silver", "Crystal"]:  # GB Saves
                    path = os.path.join(base_dir, entries["gb_dir"].get().strip(), path + ".srm")
                elif key in ["Ruby", "Sapphire", "Emerald", "FireRed", "LeafGreen"]:  # GBA Saves
                    path = os.path.join(base_dir, entries["gba_dir"].get().strip(), path + ".srm")

                exists = os.path.exists(path)
                update_entry_status(key, path, exists)

            elif isinstance(entry, tk.StringVar):  # Handle dropdowns
                update_entry_status(key, None, bool(entry.get().strip()))

        except Exception as e:
            print(f"⚠️ Error updating status for {key}: {e}")
            status_labels[key].config(text="⚠️", fg="red")  # Set to error state

    # ✅ Run a second time to update TransferPak dropdowns AFTER save slots are updated
    for key in ["RetroarchTransferPak1", "RetroarchTransferPak2"]:
        selected_game = entries[key].get().strip()
        if selected_game and selected_game in status_labels:
            game_status_icon = status_labels[selected_game].cget("text")
            game_status_color = status_labels[selected_game].cget("fg")
            status_labels[key].config(text=game_status_icon, fg=game_status_color)
        else:
            status_labels[key].config(text="⚠️", fg="yellow")  # Default warning if empty





### ==================  Monitor changes in textboxes ================== ###
def on_entry_updated(*args):
    """Triggered when any textbox or dropdown is updated"""
    print("Textbox or Dropdown updated!")  # Debugging
    update_status_icons()

def handle_paste(event):
    """Handle paste events in textboxes"""
    widget = event.widget
    widget.event_generate("<<Paste>>")
    on_entry_updated()





### ==================  Save configuration ================== ###
def save_configuration():
    """Saves the current UI values into PokemonStadiumSync.cfg"""
    config = configparser.ConfigParser()

    # Ensure all sections exist
    for section in DEFAULT_CONFIG:
        config[section] = {}

    # Retrieve values from UI elements
    for key, entry in entries.items():
        section = None
        config_key = key

        # Map keys to correct sections in config
        if key in ["RetroarchTransferPak1", "RetroarchTransferPak2"]:
            section = "Ports"
        elif key in ["base_dir", "gb_dir", "gba_dir", "sav_dir", "gbrom_dir"]:
            section = "Directories"
        elif key in ["Stadium 1", "Stadium 2"]:
            section = "StadiumROMs"
        elif key in ["Green", "Red", "Blue", "Yellow", "Gold", "Silver", "Crystal"]:
            section = "GBSlots"
        elif key in ["Ruby", "Sapphire", "Emerald", "FireRed", "LeafGreen"]:
            section = "GBASlots"

        # Special case for Stay Open checkbox
        if key == "stay_open":
            section = "General"
            config_key = "stay_open"
            config[section][config_key] = str(not stay_open_var.get())  # Inverted logic
            continue
            
        # Special case for Run Minimized checkbox
        if key == "run_minimized":
            section = "General"
            config_key = "run_minimized"
            config[section][config_key] = str(run_minimized_var.get())  
            continue

        # Ensure section exists
        if section:
            if isinstance(entry, tk.Entry):
                value = entry.get().strip()
            elif isinstance(entry, tk.StringVar):
                value = entry.get().strip()
            else:
                continue  # Skip invalid entries

            config[section][config_key] = value

    # Write configuration to file
    with open(CONFIG_FILE, "w") as configfile:
        config.write(configfile)

    print("✔️ Configuration saved successfully!")

### ==================  Load configuration ================== ###
def load_or_create_config():
    """Ensures the config file exists, creates missing values, and populates the UI properly."""
    config = configparser.ConfigParser()

    # ✔️ If config file does not exist, create it first
    if not os.path.exists(CONFIG_FILE):
        print("Config file missing! Creating a default config...")
        write_default_config(config)  # Ensure a new config is written

    # ✔️ Read the config file
    config.read(CONFIG_FILE)

    # ✔️ Ensure all expected sections and keys exist
    modified = False
    for section, keys in DEFAULT_CONFIG.items():
        if section not in config:
            config[section] = {}
            modified = True
        for key, default_value in keys.items():
            if key not in config[section]:
                config[section][key] = default_value
                modified = True

    # ✔️ Save updated config if anything was missing
    if modified:
        with open(CONFIG_FILE, "w") as configfile:
            config.write(configfile)

    # === DEBUG: Print Config Contents ===
    print("\n=== DEBUG: Config Values Loaded ===")
    for section in config.sections():
        for key, value in config[section].items():
            print(f"Config: [{section}] {key} = {value}")

    # === DEBUG: Print UI Dictionary Keys ===
    print("\n=== DEBUG: UI Entries Available ===")
    for entry_key in entries.keys():
        print(f"UI Entry: {entry_key}")

    # ✔️ Mapping Config Keys to UI Keys
    key_mapping = {
        "retroarchtransferpak1": "RetroarchTransferPak1",
        "retroarchtransferpak2": "RetroarchTransferPak2",
        "gb_subdir": "gb_dir",
        "gba_subdir": "gba_dir",
        "sav_subdir": "sav_dir",
        "gbrom_subdir": "gbrom_dir",
        "firered": "FireRed",
        "leafgreen": "LeafGreen",
        "stay_open": "stay_open",
        "run_minimized": "run_minimized",
    }

    # ✔️ Populate UI elements with config values
    print("\n=== DEBUG: Populating UI Fields ===")
    for section in config.sections():
        for key, value in config[section].items():
            # Normalize and map keys properly
            if key in key_mapping:
                normalized_key = key_mapping[key]
            elif section in ["GBSlots", "GBASlots", "StadiumROMs"]:
                normalized_key = key.replace("_", " ").title()  # Convert to match UI dropdowns
            else:
                normalized_key = key  # Keep paths/subfolders unchanged

            if normalized_key in entries:
                widget = entries[normalized_key]

                if isinstance(widget, tk.Entry):  # Handle textboxes
                    print(f"Updating UI Field: {normalized_key} -> {value}")
                    widget.delete(0, tk.END)
                    widget.insert(0, value)

                elif isinstance(widget, tk.StringVar):  # Handle dropdowns
                    print(f"Updating Dropdown: {normalized_key} -> {value}")
                    widget.set(value)  # Set dropdown value

                elif normalized_key == "stay_open":
                    print(f"Updating Checkbox: stay_open -> {value}")
                    stay_open_var.set(value.lower() == "false")  # Correct inversion logic
                    
                elif normalized_key == "run_minimized":
                    print(f"Updating Checkbox: run_minimized -> {value}")
                    run_minimized_var.set(value.lower() == "true")

            else:
                print(f"⚠️ WARNING: UI Entry Not Found for Key '{normalized_key}'")

    print("=== DEBUG: UI Update Completed ===")
    return config


### ==================  Write default configuration file ================== ###
def write_default_config(config):
    """Writes the default configuration to a new file."""
    for section, keys in DEFAULT_CONFIG.items():
        config[section] = keys

    with open(CONFIG_FILE, "w") as configfile:
        config.write(configfile)

    print("✔️ Default config created successfully!")





### ==================  Fills in directories ================== ###

def detect_and_set_base_directory(full_path):
    """Detects if the selected path contains a RetroArch folder and updates the base directory if needed."""
    base_dir_entry = entries["base_dir"]

    # If base_dir is already valid, skip this process
    if os.path.exists(base_dir_entry.get().strip()):
        return

    # Normalize the full path
    full_path = os.path.normpath(full_path)

    # Split the path and check for "retroarch" (case-insensitive)
    path_parts = full_path.lower().split(os.path.sep)
    if "retroarch" in path_parts:
        retroarch_index = path_parts.index("retroarch")
        detected_base = os.path.sep.join(full_path.split(os.path.sep)[:retroarch_index + 1])

        # Normalize detected_base to ensure consistency
        detected_base = os.path.normpath(detected_base)

        # Convert to forward slashes for UI consistency
        detected_base = detected_base.replace("\\", "/")

        # Update the base directory field
        print(f"✔️ Auto-detected RetroArch base directory: {detected_base}")  # Debugging
        base_dir_entry.delete(0, tk.END)
        base_dir_entry.insert(0, detected_base)

        # ✔️ Trim paths retroactively
        trim_base_dir_from_subfolders(detected_base)
        trim_base_dir_from_files(detected_base)

        # Re-run entry validation
        update_status_icons()

def auto_populate_subfolder():
    """Automatically populates subfolder textboxes based on last_found path only if they are empty or invalid."""
    global last_found, last_found_type

    if not last_found or not last_found_type:
        print("❌ auto_populate_subfolder: No valid path found. Skipping.")
        return  # No valid path found

    base_dir = os.path.normpath(entries["base_dir"].get().strip())  # Get base directory
    relative_path = os.path.relpath(last_found, base_dir).replace("\\", "/")  # Trim base dir
    subfolder_path = os.path.dirname(relative_path)  # Remove the filename

    print(f"🔍 auto_populate_subfolder: last_found = {last_found}, last_found_type = {last_found_type}")
    print(f"📁 Base Dir: {base_dir} | Relative Path: {relative_path} | Subfolder Path: {subfolder_path}")

    # Debugging: Print existing UI fields
    print("🔎 Existing UI Entries:", entries.keys())

    # Function to safely update textboxes if they don't exist
    def update_textbox_if_invalid(entry_key, value):
        """Only update the textbox if the current path is empty or invalid."""
        if entry_key in entries:
            current_path = entries[entry_key].get().strip()
            path_exists = os.path.exists(os.path.join(base_dir, current_path))  # Check if path exists

            if not path_exists:  # Only update if path does not exist
                print(f"✔️ Auto-updating {entry_key} (previously invalid) with: {value}")
                entries[entry_key].delete(0, tk.END)
                entries[entry_key].insert(0, value)
                entries[entry_key].update()  # Force UI refresh
            else:
                print(f"⚠️ Skipping {entry_key} - Path exists: {current_path}")
        else:
            print(f"❌ Error: {entry_key} not found in entries.")

    # Determine which subfolder should be updated
    if last_found_type == "gb_slot":
        update_textbox_if_invalid("gb_dir", subfolder_path)

    elif last_found_type == "gba_slot":
        update_textbox_if_invalid("gba_dir", subfolder_path)

    elif last_found_type == "stadium_rom":
        update_textbox_if_invalid("sav_dir", subfolder_path)

    # Ensure UI reflects the updates
    update_status_icons()

### ==================  Format files and directories ================== ###
def normalize_path(path):
    """Ensures all paths use '/' for consistency"""
    return os.path.normpath(path).replace("\\", "/")
    
def normalize_config_key(key):
    """Maps config keys to UI keys."""
    key_mapping = {
        "gb_subdir": "gb_dir",
        "gba_subdir": "gba_dir",
        "sav_subdir": "sav_dir",
        "gbrom_subdir": "gbrom_dir",
        "firered": "FireRed",
        "leafgreen": "LeafGreen",
        "stay_open": "stay_open",
        "run_minimized": "run_minimized",
        "retroarchtransferpak1": "RetroarchTransferPak1",
        "retroarchtransferpak2": "RetroarchTransferPak2",
    }
    return key_mapping.get(key, key)

def trim_base_dir(base_dir, entry_keys):
    """Trims the base directory from the given entry keys."""
    base_dir = os.path.normpath(base_dir).rstrip("/\\")
    for key in entry_keys:
        current_value = entries[key].get().strip()
        if not current_value:
            continue
        normalized_value = os.path.normpath(current_value).rstrip("/\\")
        if normalized_value.lower().startswith(base_dir.lower()):
            new_relative_path = normalized_value[len(base_dir):].lstrip("/\\")
            new_relative_path = os.path.normpath(new_relative_path).replace("\\", "/")
            entries[key].delete(0, tk.END)
            entries[key].insert(0, new_relative_path)
            print(f"🔧 Trimmed {key}: {normalized_value} -> {new_relative_path}")

def trim_base_dir_from_subfolders(base_dir):
    """Trims the base directory from subfolder paths."""
    trim_base_dir(base_dir, ["gb_dir", "gba_dir", "sav_dir", "gbrom_dir"])

def trim_base_dir_from_files(base_dir):
    """Trims the base directory from save slots and Stadium ROMs."""
    trim_base_dir(base_dir, ["Stadium 1", "Stadium 2", "Green", "Red", "Blue", "Yellow", "Gold", "Silver", "Crystal",
                             "Ruby", "Sapphire", "Emerald", "FireRed", "LeafGreen"])




### ==================  Create UI ================== ###
root = tk.Tk()
root.title("Pokemon Stadium Sync Configuration")

def apply_dark_mode():
    """Apply custom dark mode styling to the UI"""
    DARK_BG = "#212121"
    LIGHT_TEXT = "#CCCCCC"
    ACCENT_COLOR = "#424242"

    root.configure(bg=DARK_BG)

    for widget in root.winfo_children():
        if isinstance(widget, tk.Label):
            widget.configure(bg=DARK_BG, fg=LIGHT_TEXT)
        elif isinstance(widget, tk.Entry):
            widget.configure(bg=ACCENT_COLOR, fg=LIGHT_TEXT, insertbackground=LIGHT_TEXT)
        elif isinstance(widget, tk.Button):
            widget.configure(bg=ACCENT_COLOR, fg=LIGHT_TEXT)
        elif isinstance(widget, tk.Checkbutton):
            widget.configure(bg=DARK_BG, fg=LIGHT_TEXT, selectcolor=ACCENT_COLOR)
        elif isinstance(widget, tk.OptionMenu):
            widget.configure(bg=ACCENT_COLOR, fg=LIGHT_TEXT)
apply_dark_mode()

# Add an empty frame at the top for padding
padding_frame = tk.Frame(root, height=8, bg="#212121")  # Reduced height for better spacing
padding_frame.grid(row=0, column=0, columnspan=3, sticky="nsew")  # "nsew" ensures proper alignment

# Dictionary for label text
labels = {
    "RetroarchTransferPak1": "TransferPak 1:", # TransferPak Port1 - For Pokemon Stadium
    "RetroarchTransferPak2": "TransferPak 2:", # TransferPak Port2 - For Pokemon Stadium 2
    "base_dir": "RetroArch folder:", # Base Directory
    "gb_dir": "GB save subfolder:", # Subfolder for GB saves
    "gba_dir": "GBA save subfolder:", # Subfolder for GBA saves
    "sav_dir": "TransferPak subfolder:", # Subfolder for TransferPak
    "gbrom_dir": "GB ROM subfolder:", # Subfolder for GB ROMs
    "Stadium 1": "Pkmn Stadium ROM:", # N64 ROM  - Pokemon Stadium ROM (.n64/.z64)
    "Stadium 2": "Pkmn Stadium 2 ROM:", # N64 ROM  - Pokemon Stadium 2 ROM (.n64/.z64)
    "Green": "Green Version:", # GB Slot1  - Pokemon - Green Version (.srm)
    "Red": "Red Version:", # GB Slot2  - Pokemon - Red Version (.srm)
    "Blue": "Blue Version:", # GB Slot3  - Pokemon - Blue Version (.srm)
    "Yellow": "Yellow Version:", # GB Slot4  - Pokemon - Yellow Version (.srm)
    "Gold": "Gold Version:", # GB Slot5  - Pokemon - Gold Version (.srm)
    "Silver": "Silver Version:", # GB Slot6  - Pokemon - Silver Version (.srm)
    "Crystal": "Crystal Version:", # GB Slot7  - Pokemon - Crystal Version (.srm)
    "Ruby": "Ruby Version:", # GBA Slot1  - Pokemon - Ruby Version (.srm)
    "Sapphire": "Sapphire Version:", # GBA Slot2  - Pokemon - Sapphire Version (.srm)
    "Emerald": "Emerald Version:", # GBA Slot3  - Pokemon - Emerald Version (.srm)
    "FireRed": "FireRed Version:", # GBA Slot4  - Pokemon - FireRed Version (.srm)
    "LeafGreen": "LeafGreen Version:", # GBA Slot5  - Pokemon - LeafGreen Version (.srm)
}

# Dropdown options
dropdown_options = {
    "RetroarchTransferPak1": ["                 ", "Green", "Red", "Blue", "Yellow"],
    "RetroarchTransferPak2": ["                 ", "Green", "Red", "Blue", "Yellow", "Gold", "Silver", "Crystal"],
}

# Define colors for GB and GBA slot labels
label_colors = {
    "Green": "#43a047",
    "Red": "#e53935",
    "Blue": "#1e88e5",
    "Yellow": "#fdd835",
    "Gold": "#d4af37",
    "Silver": "#BEC2CB",
    "Crystal": "#00e5ff",
    "Ruby": "red",
    "Sapphire": "#0047AB",
    "Emerald": "green",
    "FireRed": "#ff2a04",
    "LeafGreen": "#228B22"
}

# Dictionary to store entry fields
entries = {}


### ==================  Build UI ================== ###
for idx, (key, text) in enumerate(labels.items(), start=1):
    # Create label for the setting name
    frame = tk.Frame(root, bg="#212121")
    frame.grid(row=idx, column=0, padx=10, pady=5, sticky="w")

    tk.Label(frame, text=text, fg="#CCCCCC", bg="#212121").grid(row=0, column=0, sticky="w")

    # ✔️ ADD STATUS LABEL IN COLUMN 1
    status_label = tk.Label(root, text="⚠️", fg="red", bg="#212121", font=("Segoe UI", 12))
    status_label.grid(row=idx, column=1, padx=8, pady=5)
    status_labels[key] = status_label  # Store reference to update later

    # Handle textboxes
    if key in dropdown_options:
        var = tk.StringVar()
        var.set("")
        dropdown = tk.OptionMenu(root, var, *dropdown_options[key])
        dropdown.config(width=14, bg="#424242", fg="white", activebackground="#565656", activeforeground="white", relief="flat")
        dropdown.grid(row=idx, column=2, padx=3, pady=4, ipady=1, sticky="w")
        entries[key] = var
    else:
        entry = tk.Entry(root, width=60, font=("Segoe UI", 10), bg="#424242", fg="white", insertbackground="white", relief="flat")
        entry.grid(row=idx, column=2, padx=3, pady=4, ipady=1, sticky="w")
        entries[key] = entry

        # Add browse button
        browse_button = tk.Button(root, text="Browse", command=lambda k=key: browse_path(k),
                                  font=("Segoe UI", 10), width=9, bd=0, relief="flat", bg="#424242", fg="white",
                                  activebackground="#555", activeforeground="white")
        browse_button.grid(row=idx, column=3, padx=5, pady=5)

        # ✔️ Bind event to update status when textbox is modified
        entry.bind("<FocusOut>", lambda e, k=key: update_status_icons())
        var = tk.StringVar()
        var.trace_add("write", lambda *args, k=key: update_status_icons())
        entry.config(textvariable=var)
    frame = tk.Frame(root, bg="#212121")
    frame.grid(row=idx, column=0, padx=10, pady=5, sticky="w")

    if key in label_colors:
        # Separate "Version" for GB and GBA labels
        game_name, _, version_text = text.partition(" Version")
        game_label = tk.Label(frame, text=game_name, fg=label_colors[key], bg="#212121")
        game_label.grid(row=0, column=0, sticky="w")

        if version_text:
            version_label = tk.Label(frame, text=" Version:", fg="#CCCCCC", bg="#212121")
            version_label.grid(row=0, column=1, sticky="w")
    else:
        tk.Label(frame, text=text, fg="#CCCCCC", bg="#212121").grid(row=0, column=0, sticky="w")

    # ✔️ INSERT EMPTY COLUMN (SPACER)
    root.grid_columnconfigure(1, minsize=5)  # Adjust width for spacing

    # Create dropdown menus
    if key in dropdown_options:
        var = tk.StringVar()
        var.set("")

        frame = tk.Frame(root, bg="#212121")  # Create a frame for label + dropdown
        frame.grid(row=idx, column=2, padx=0, pady=5, sticky="w")  

        # Create the label next to the dropdown
        label = tk.Label(frame, text="Select game to use with Pokemon Stadium" if key == "RetroarchTransferPak1"
                                  else "Select game to use with Pokemon Stadium 2",
                         fg="#878787", bg="#212121", font=("Segoe UI", 9))
        label.pack(side="right", padx=8)  # Align to the right of dropdown

        # Create dropdown inside the frame
        dropdown = tk.OptionMenu(frame, var, *dropdown_options[key])
        dropdown.config(
            width=16,  
            bg="#424242",  
            fg="white",  
            activebackground="#565656",  
            activeforeground="white",  
            relief="flat", 
            highlightthickness=3,
            highlightbackground="#212121",  
            highlightcolor="#777"
        )

        # ✔️ Modify the actual dropdown menu (the list of options)
        dropdown["menu"].config(
            bg="#424242",  
            fg="white",  
            activebackground="#555",  
            activeforeground="white",
            font=("Segoe UI", 10),
            relief="flat",  
        )

        dropdown.pack(side="left")  

        entries[key] = var  

    else:
        entry = tk.Entry(root, width=60, font=("Segoe UI", 10),
                         bg="#424242", fg="white", insertbackground="white",
                         relief="flat", highlightthickness=1, 
                         highlightbackground="#555", highlightcolor="#777")
        entry.grid(row=idx, column=2, padx=3, pady=4, ipady=1)  # ✔️ Column moved to 2
        entries[key] = entry

        # Create browse buttons
        browse_button = tk.Button(
            root,
            text="Browse",
            command=lambda k=key: browse_path(k),
            font=("Segoe UI", 10),  
            width=9,  
            bd=0,  
            relief="flat",  
            bg="#424242",  
            fg="white",
            activebackground="#555",  
            activeforeground="white"
        )

        browse_button.bind("<Enter>", lambda e: e.widget.configure(bg="#666"))
        browse_button.bind("<Leave>", lambda e: e.widget.configure(bg="#424242"))

        browse_button.grid(row=idx, column=3, padx=5, pady=5)  # ✔️ Browse button in column 3

### ===  Search Button === ###
search_button = tk.Button(
    root,
    text="Search for files",
    font=("Segoe UI", 10),  # Match browse buttons
    width=18,  # Match browse button width
    bd=0,  # No border
    relief="flat",
    bg="#424242",  # Same as textboxes
    fg="white",
    activebackground="#555",  # Slightly lighter on hover
    activeforeground="white"
)
search_button.bind("<Enter>", lambda e: e.widget.configure(bg="#666"))
search_button.bind("<Leave>", lambda e: e.widget.configure(bg="#424242"))
search_button.grid(row=len(labels) + 1, column=0, columnspan=2, padx=15, pady=15, sticky="w")

# Checkbox for "Stay Open"
stay_open_var = tk.BooleanVar()
entries["stay_open"] = stay_open_var  
stay_open_checkbox = tk.Checkbutton(
    root,
    text="Close terminal after sync",
    variable=stay_open_var,
    bg="#212121", fg="white",
    selectcolor="#212121",  
    font=("Segoe UI", 10),
    activebackground="#212121",
    activeforeground="white",
    relief="flat",
    border=20,
    highlightbackground="#212121",
)
stay_open_checkbox.grid(row=len(labels) + 1, column=1, columnspan=2, padx=0, pady=0, sticky="w")

# Checkbox for "Run minimized"
run_minimized_var = tk.BooleanVar()
entries["run_minimized"] = run_minimized_var
run_minimized_checkbox = tk.Checkbutton(
    root,
    text="Run in the background",
    variable=run_minimized_var,
    bg="#212121", fg="white",
    selectcolor="#212121",  
    font=("Segoe UI", 10),
    activebackground="#212121",
    activeforeground="white",
    relief="flat",
    border=20,
    highlightbackground="#212121",
)
run_minimized_checkbox.grid(row=len(labels) + 1, column=1, columnspan=2, padx=70, pady=0, sticky="e")

### ===  Save Button === ###
save_button = tk.Button(
    root,
    text="Save Configuration",
    font=("Segoe UI", 10),  # Match browse buttons
    width=18,  # Match browse button width
    bd=0,  # No border
    relief="flat",
    bg="#424242",  # Same as textboxes
    fg="white",
    activebackground="#555",  # Slightly lighter on hover
    activeforeground="white"
)
save_button.bind("<Enter>", lambda e: e.widget.configure(bg="#666"))
save_button.bind("<Leave>", lambda e: e.widget.configure(bg="#424242"))
save_button.grid(row=len(labels) + 1, column=2, columnspan=2, padx=15, pady=15, sticky="e")

# Attach change detection to all textboxes and dropdowns
for key, entry in entries.items():
    if isinstance(entry, tk.Entry):  # Handle textboxes
        entry.bind("<KeyRelease>", lambda e, k=key: on_entry_updated())  # Detect manual typing
        entry.bind("<FocusOut>", lambda e, k=key: on_entry_updated())  # Detect when textbox loses focus
    elif isinstance(entry, tk.StringVar):  # Handle dropdown changes
        entry.trace_add("write", lambda *args, k=key: on_entry_updated())  # Detect dropdown selection changes

search_button.config(command=search_for_files)
save_button.config(command=save_configuration)   
config = load_or_create_config()
update_status_icons()


### ==================  Run UI ================== ###
root.mainloop()