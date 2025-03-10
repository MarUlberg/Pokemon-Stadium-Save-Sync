import tkinter as tk
from tkinter import messagebox, filedialog
import re
import os
import configparser
import sys
import time

start_time = time.time()

def find_retroarch_folder():
    """Dynamically locate RetroArch base directory"""
    # Check if running as a compiled executable
    if getattr(sys, 'frozen', False):
        script_dir = os.path.dirname(sys.argv[0])  # Path of the .exe file
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))  # Path of the script

    parts = script_dir.split(os.path.sep)  # Split into folder components
    parts_lower = [part.lower() for part in parts]  # Convert all parts to lowercase

    if "retroarch" in parts_lower:
        retroarch_index = parts_lower.index("retroarch")  # Find index of RetroArch (case-insensitive)
        corrected_path = os.path.sep.join(parts[:retroarch_index + 1])
        return corrected_path.replace("\\", "/")  # Ensure forward slashes
    else:
        print("Unable to locate RetroArch folder.")
        return ""

CONFIG_FILE = "PokemonStadiumSync.cfg"

def load_config():
    """Load configuration from PokemonStadiumSync.cfg"""
    config = configparser.ConfigParser()
    config_data = {}
    try:
        config.read(CONFIG_FILE, encoding="utf-8")
        config_data["RetroarchTransferPak1"] = config.get("Ports", "retroarchtransferpak1", fallback="")
        config_data["RetroarchTransferPak2"] = config.get("Ports", "retroarchtransferpak2", fallback="")
        config_base_dir = config.get("Directories", "base_dir", fallback="")
        if os.path.isdir(config_base_dir):
            config_data["base_dir"] = config_base_dir
        else:
            dynamic_base_dir = find_retroarch_folder()
            config_data["base_dir"] = dynamic_base_dir
            print(f"Config base_dir invalid or missing. Using dynamically detected: {dynamic_base_dir}")
        config_data["gb_dir"] = config.get("Directories", "gb_subdir", fallback="")
        config_data["gba_dir"] = config.get("Directories", "gba_subdir", fallback="")
        config_data["sav_dir"] = config.get("Directories", "sav_subdir", fallback="")
        config_data["gbrom_dir"] = config.get("Directories", "gbrom_subdir", fallback="")
        config_data["stay_open"] = config.getboolean("General", "stay_open", fallback=False)
        config_data["Stadium 1"] = config.get("StadiumROMs", "stadium 1", fallback="")
        config_data["Stadium 2"] = config.get("StadiumROMs", "stadium 2", fallback="")
        for game in ["Green", "Red", "Blue", "Yellow", "Gold", "Silver", "Crystal"]:
            raw_value = config.get("GBSlots", game.lower(), fallback="")
            config_data[game] = os.path.splitext(raw_value)[0]
        for game in ["Ruby", "Sapphire", "Emerald", "FireRed", "LeafGreen"]:
            raw_value = config.get("GBASlots", game.lower(), fallback="")
            config_data[game] = os.path.splitext(raw_value)[0]

    except Exception as e:
        messagebox.showerror("Error", f"Failed to load configuration: {e}")

    return config_data

def save_config():
    """Save configuration to PokemonStadiumSync.cfg"""
    try:
        # Read the existing config file to preserve structure
        with open(CONFIG_FILE, "r", encoding="utf-8") as file:
            lines = file.readlines()

        config = configparser.RawConfigParser()  # Use RawConfigParser to avoid formatting changes
        config.read(CONFIG_FILE, encoding="utf-8")

        # Preserve original sections
        if "General" in config:
            config.set("General", "_stay_open", str(stay_open_var.get()))

        if "Ports" in config:
            config.set("Ports", "RetroarchTransferPak1", entries["RetroarchTransferPak1"].get())
            config.set("Ports", "RetroarchTransferPak2", entries["RetroarchTransferPak2"].get())

        if "Directories" in config:
            config.set("Directories", "base_dir", entries["base_dir"].get())
            config.set("Directories", "gb_subdir", entries["gb_dir"].get())
            config.set("Directories", "gba_subdir", entries["gba_dir"].get())
            config.set("Directories", "sav_subdir", entries["sav_dir"].get())
            config.set("Directories", "gbrom_subdir", entries["gbrom_dir"].get())

        if "StadiumROMs" in config:
            config.set("StadiumROMs", "Stadium 1", entries["Stadium 1"].get())
            config.set("StadiumROMs", "Stadium 2", entries["Stadium 2"].get())

        if "GBSlots" in config:
            for game in ["Green", "Red", "Blue", "Yellow", "Gold", "Silver", "Crystal"]:
                game_value = entries[game].get()
                # Ensure .srm extension is added if not present
                if not game_value.endswith(".srm"):
                    game_value += ".srm"
                config.set("GBSlots", game, game_value)

        if "GBASlots" in config:
            for game in ["Ruby", "Sapphire", "Emerald", "FireRed", "LeafGreen"]:
                game_value = entries[game].get()
                # Ensure .srm extension is added if not present
                if not game_value.endswith(".srm"):
                    game_value += ".srm"
                config.set("GBASlots", game, game_value)

        # Write back using manual formatting to preserve original structure
        with open(CONFIG_FILE, "w", encoding="utf-8") as file:
            for line in lines:
                stripped = line.strip()

                # Preserve existing comments and blank lines
                if stripped.startswith(";") or stripped == "":
                    file.write(line)
                    continue

                # Write sections as-is
                if stripped.startswith("[") and stripped.endswith("]"):
                    file.write(line)
                    continue

                # Modify only the values that were updated
                key, sep, value = line.partition("=")
                key = key.strip()

                if config.has_option("General", key):
                    file.write(f"{key} = {config.get('General', key)}\n")
                elif config.has_option("Ports", key):
                    file.write(f"{key} = {config.get('Ports', key)}\n")
                elif config.has_option("Directories", key):
                    file.write(f"{key} = {config.get('Directories', key)}\n")
                elif config.has_option("StadiumROMs", key):
                    file.write(f"{key} = {config.get('StadiumROMs', key)}\n")
                elif config.has_option("GBSlots", key):
                    file.write(f"{key} = {config.get('GBSlots', key)}\n")
                elif config.has_option("GBASlots", key):
                    file.write(f"{key} = {config.get('GBASlots', key)}\n")
                else:
                    file.write(line)  # Keep unknown lines untouched
        if time.time() - start_time > 0.5:
            messagebox.showinfo("Success", "Configuration saved successfully!")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to save configuration: {e}")


# Create UI
root = tk.Tk()
root.title("Pokemon Stadium Sync Configuration")

data = load_config()
entries = {}

labels = {
    "RetroarchTransferPak1": "TransferPak 1:",
    "RetroarchTransferPak2": "TransferPak 2:",
    "base_dir": "RetroArch folder:",
    "gb_dir": "GB save subfolder:",
    "gba_dir": "GBA save subfolder:",
    "sav_dir": "TransferPak subfolder:",
    "gbrom_dir": "GB ROM subfolder:",
    "Stadium 1": "Pkmn Stadium ROM:",
    "Stadium 2": "Pkmn Stadium 2 ROM:",
    "Green": "Green Version:",
    "Red": "Red Version:",
    "Blue": "Blue Version:",
    "Yellow": "Yellow Version:",
    "Gold": "Gold Version:",
    "Silver": "Silver Version:",
    "Crystal": "Crystal Version:",
    "Ruby": "Ruby Version:",
    "Sapphire": "Sapphire Version:",
    "Emerald": "Emerald Version:",
    "FireRed": "FireRed Version:",
    "LeafGreen": "LeafGreen Version:",
}

dropdown_options = {
    "RetroarchTransferPak1": ["", "Green", "Red", "Blue", "Yellow"],
    "RetroarchTransferPak2": ["", "Green", "Red", "Blue", "Yellow", "Gold", "Silver", "Crystal"],
}

def browse_path(entry, key):
    base_dir = entries["base_dir"].get()
    subfolder = entries["base_dir"].get()
    
    # If the path is relative, join it with base_dir
    if not os.path.isabs(subfolder):
        initial_dir = os.path.join(base_dir, subfolder)
    else:
        initial_dir = subfolder

    # Ensure the initial directory exists, otherwise fall back to base_dir
    if not os.path.isdir(initial_dir):
        initial_dir = base_dir

    # Set correct browse behavior
    if key in ["gb_dir", "gba_dir", "sav_dir", "gbrom_dir"]:
        folder_selected = filedialog.askdirectory(initialdir=initial_dir)
    elif key in ["Stadium 1", "Stadium 2"]:  # Browse for Stadium ROMs (.n64 or .z64)
        stadium_dir = os.path.join(base_dir, entries["sav_dir"].get())  # Use sav_dir from textbox
        file_selected = filedialog.askopenfilename(
            initialdir=stadium_dir,
            filetypes=[("N64 ROMs", "*.n64;*.z64"), ("All Files", "*.*")]
        )
        folder_selected = os.path.basename(file_selected) if file_selected else None  # Keep only filename + extension
    elif key in ["Green", "Red", "Blue", "Yellow", "Gold", "Silver", "Crystal"]:  # Browse for GB Slots (.srm, .gb, .gbc)
        gb_slot_dir = os.path.join(base_dir, entries["gb_dir"].get())  # Use gb_dir from textbox
        file_selected = filedialog.askopenfilename(
            initialdir=gb_slot_dir,
            filetypes=[("GB/GBC Saves", "*.srm;*.gb;*.gbc"), ("All Files", "*.*")]
        )
        folder_selected = os.path.splitext(os.path.basename(file_selected))[0] if file_selected else None  # Remove path & extension
    elif key in ["Ruby", "Sapphire", "Emerald", "FireRed", "LeafGreen"]:  # Browse for GBA Slots (.srm, .gba)
        gba_slot_dir = os.path.join(base_dir, entries["gba_dir"].get())  # Use gba_dir from textbox
        file_selected = filedialog.askopenfilename(
            initialdir=gba_slot_dir,
            filetypes=[("GBA Saves", "*.srm;*.gba"), ("All Files", "*.*")]
        )
        folder_selected = os.path.splitext(os.path.basename(file_selected))[0] if file_selected else None  # Remove path & extension
    else:
        folder_selected = filedialog.askdirectory(initialdir=initial_dir)

    if folder_selected:
        # Only remove base_dir from subfolders, not full file paths
        if key in ["gb_dir", "gba_dir", "sav_dir", "gbrom_dir"] and folder_selected.startswith(base_dir):
            folder_selected = folder_selected[len(base_dir):].lstrip("\\/")

        entry.delete(0, tk.END)
        entry.insert(0, folder_selected)

for idx, (key, value) in enumerate(data.items()):
    if key == "stay_open":
        continue
    
    tk.Label(root, text=labels.get(key, key)).grid(row=idx, column=0, padx=10, pady=5, sticky="w")   
    if key in dropdown_options:
        var = tk.StringVar()
        var.set(value)
        dropdown = tk.OptionMenu(root, var, *dropdown_options[key])
        dropdown.config(width=12)
        dropdown.grid(row=idx, column=1, padx=10, pady=5, sticky="w")
        entries[key] = var
        
        note_text = "Select game to use with Pokemon Stadium          " if key == "RetroarchTransferPak1" else "Select game to use with Pokemon Stadium 2       "
        tk.Label(root, text=note_text, fg="gray").grid(row=idx, column=1, padx=10, pady=0, sticky="e")

    else:
        entry = tk.Entry(root, width=60)
        entry.insert(0, value)
        print(f"Debug: Setting UI field '{key}' with value: {value}")
        entry.grid(row=idx, column=1, padx=10, pady=5)
        entries[key] = entry
        
        browse_button = tk.Button(root, text="Browse", command=lambda e=entry, k=key: browse_path(e, k))
        browse_button.grid(row=idx, column=2, padx=5, pady=5)
stay_open_var = tk.BooleanVar(value=not data.get("stay_open", False))
stay_open_checkbox = tk.Checkbutton(root, text="Close terminal after sync", variable=stay_open_var)
stay_open_checkbox.grid(row=len(data), column=0, columnspan=2, pady=10)

save_button = tk.Button(root, text="Save Configuration", command=save_config)
save_button.grid(row=len(data) + 1, column=0, columnspan=3, pady=10)

# Apply Dark Mode Theme After UI is Created
def apply_dark_mode():
    DARK_BG = "#212121"
    LIGHT_TEXT = "#CCCCCC"
    ACCENT_COLOR = "#424242"
    ACTIVE_BG = "#6272A4"
    FONT = ("Segoe UI", 10)

    root.configure(bg=DARK_BG)

    for widget in root.winfo_children():
        if isinstance(widget, tk.Label):
            widget.configure(bg=DARK_BG, fg=LIGHT_TEXT, font=FONT)
        elif isinstance(widget, tk.Entry):
            widget.configure(bg=ACCENT_COLOR, fg=LIGHT_TEXT, insertbackground=LIGHT_TEXT, font=FONT,
                             relief="flat", highlightthickness=1, highlightbackground="#555", highlightcolor="#777")
        elif isinstance(widget, tk.Button):
            widget.configure(bg=ACCENT_COLOR, fg=LIGHT_TEXT, activebackground="#555", activeforeground=LIGHT_TEXT, font=FONT, bd=0)
            widget.bind("<Enter>", lambda e: e.widget.configure(bg="#666"))
            widget.bind("<Leave>", lambda e: e.widget.configure(bg=ACCENT_COLOR))
        elif isinstance(widget, tk.Checkbutton):
            widget.configure(bg=DARK_BG, fg=LIGHT_TEXT, selectcolor=ACCENT_COLOR, activebackground=DARK_BG, font=FONT)
        elif isinstance(widget, tk.OptionMenu):
            widget.configure(bg=ACCENT_COLOR, fg=LIGHT_TEXT, activebackground="#555", activeforeground=LIGHT_TEXT, font=FONT, bd=0)
            widget["menu"].configure(bg=ACCENT_COLOR, fg=LIGHT_TEXT, activebackground="#666", activeforeground=LIGHT_TEXT, font=FONT)


    for widget in root.winfo_children():
        if isinstance(widget, tk.OptionMenu):
            widget.configure(bg=ACCENT_COLOR, fg=LIGHT_TEXT, font=FONT)
            widget["menu"].configure(bg=ACCENT_COLOR, fg=LIGHT_TEXT, activebackground="#6272A4", activeforeground=LIGHT_TEXT, font=FONT)

apply_dark_mode()
save_config()
root.mainloop()
