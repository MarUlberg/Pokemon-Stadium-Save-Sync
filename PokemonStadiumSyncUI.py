import tkinter as tk
from tkinter import messagebox, filedialog
import re
import os

CONFIG_FILE = "PokemonStadiumSync.py"


def load_config():
    """Read the configuration values from PokemonStadiumSync.py"""
    config = {}
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as file:
            content = file.read()
            config["RetroarchTransferPak1"] = re.search(r'RetroarchTransferPak1 = "(.*?)"', content).group(1)
            config["RetroarchTransferPak2"] = re.search(r'RetroarchTransferPak2 = "(.*?)"', content).group(1)
            config["base_dir"] = re.search(r'base_dir = "(.*?)"', content).group(1)
            config["gb_dir"] = re.search(r'gb_dir = os.path.join\(base_dir, "(.*?)"\)', content).group(1)
            config["gba_dir"] = re.search(r'gba_dir = os.path.join\(base_dir, "(.*?)"\)', content).group(1)
            config["sav_dir"] = re.search(r'sav_dir = os.path.join\(base_dir, "(.*?)"\)', content).group(1)
            
            # Load slot mappings
            config["Stadium 1"] = re.search(r'"Stadium 1": "(.*?)"', content).group(1)
            config["Stadium 2"] = re.search(r'"Stadium 2": "(.*?)"', content).group(1)
            for slot in ["Green", "Red", "Blue", "Yellow", "Gold", "Silver", "Crystal"]:
                config[slot] = os.path.splitext(re.search(rf'"{slot}": "(.*?)"', content).group(1))[0]
            for slot in ["Ruby", "Sapphire", "Emerald", "FireRed", "LeafGreen"]:
                config[slot] = os.path.splitext(re.search(rf'"{slot}": "(.*?)"', content).group(1))[0]
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load configuration: {e}")
    return config

def browse_file(entry, filetypes, strip_extension=False):
    filename = filedialog.askopenfilename(filetypes=filetypes)
    if filename:
        filename = os.path.basename(filename)
        if strip_extension:
            filename = os.path.splitext(filename)[0]
        entry.delete(0, tk.END)
        entry.insert(0, filename)


def browse_folder(entry, key):
    folder = filedialog.askdirectory()
    if folder:
        folder = folder.replace("\\", "/")
        if key != "base_dir":
            base_dir = entries["base_dir"].get()
            if folder.startswith(base_dir):
                folder = folder[len(base_dir):].lstrip("/")
        entry.delete(0, tk.END)
        entry.insert(0, folder)

def save_config():
    """Save the modified values back to PokemonStadiumSync.py"""
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as file:
            content = file.read()
        
        for key, entry in entries.items():
            if isinstance(entry, tk.StringVar):
                value = entry.get()
            else:
                value = entry.get()
            
            if key in ["gb_dir", "gba_dir", "sav_dir"]:
                content = re.sub(rf'{key} = os.path.join\(base_dir, ".*?"\)', f'{key} = os.path.join(base_dir, "{value}")', content)
            elif key in ["Green", "Red", "Blue", "Yellow", "Gold", "Silver", "Crystal", "Ruby", "Sapphire", "Emerald", "FireRed", "LeafGreen"]:
                value += ".srm"
                content = re.sub(rf'"{key}": ".*?"', f'"{key}": "{value}"', content)
            else:
                content = re.sub(rf'{key} = ".*?"', f'{key} = "{value}"', content)

        if "Stadium 1" in entries:
            content = re.sub(r'"Stadium 1": ".*?"', f'"Stadium 1": "{entries["Stadium 1"].get()}"', content)

        if "Stadium 2" in entries:
            content = re.sub(r'"Stadium 2": ".*?"', f'"Stadium 2": "{entries["Stadium 2"].get()}"', content)
        
        with open(CONFIG_FILE, "w", encoding="utf-8") as file:
            file.write(content)
        
        messagebox.showinfo("Success", "Configuration saved successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save configuration: {e}")


# Create UI
root = tk.Tk()
root.title("Pokemon Stadium Sync Configuration")

data = load_config()
entries = {}

dropdown_options = {
    "RetroarchTransferPak1": ["", "Green", "Red", "Blue", "Yellow"],
    "RetroarchTransferPak2": ["", "Green", "Red", "Blue", "Yellow", "Gold", "Silver", "Crystal"],
}

labels = {
    "RetroarchTransferPak1": "TransferPak 1:",
    "RetroarchTransferPak2": "TransferPak 2:",
    "base_dir": "RetroArch folder:",
    "gb_dir": "GB save subfolder:",
    "gba_dir": "GBA save subfolder:",
    "sav_dir": "TransferPak subfolder:",
    "Stadium 1": "Pkmn Stadium ROM:",
    "Stadium 2": "Pkmn Stadium 2 ROM:",
}

for idx, (key, value) in enumerate(data.items()):
    tk.Label(root, text=labels.get(key, key)).grid(row=idx, column=0, padx=10, pady=5, sticky="w")
    
    if key in dropdown_options:
        var = tk.StringVar()
        var.set(value)
        dropdown = tk.OptionMenu(root, var, *dropdown_options[key])
        dropdown.config(width=12)
        dropdown.grid(row=idx, column=1, padx=10, pady=5, sticky="w")
        entries[key] = var
        
        note_text = "Select game to use with Pokemon Stadium" if key == "RetroarchTransferPak1" else "Select game to use with Pokemon Stadium 2"
        tk.Label(root, text=note_text, fg="gray").grid(row=idx, column=1, padx=5, pady=5, sticky="e")
    else:
        entry = tk.Entry(root, width=60)
        entry.insert(0, value)
        entry.grid(row=idx, column=1, padx=10, pady=5)
        entries[key] = entry
        
        browse_button = tk.Button(root, text="Browse", command=lambda e=entry, k=key: browse_folder(e, k))
        browse_button.grid(row=idx, column=2, padx=5, pady=5)

save_button = tk.Button(root, text="Save Configuration", command=save_config)
save_button.grid(row=len(data), column=0, columnspan=3, pady=10)

root.mainloop()
