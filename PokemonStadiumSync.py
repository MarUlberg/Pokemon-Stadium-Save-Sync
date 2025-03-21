### ==================  Import Dependencies ================== ###

# Standard Library Imports
import os
import sys
import time
import shutil
import threading
import ctypes
import configparser

# Third-Party Modules
import psutil  # Process monitoring
import pystray  # System tray management
import watchdog  # File monitoring
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pystray import MenuItem as item, Icon
from PIL import Image  # Used for tray icon handling
from colorama import init, Fore  # Colored terminal output

### ==================  Global Variables & Initialization ================== ###

# Initialize Colorama for colored terminal output
init(autoreset=True)

# Windows-Specific Console Handling
whnd = None
if sys.platform == "win32":
    whnd = ctypes.windll.kernel32.GetConsoleWindow()

# Tracking Sync Status
last_sync_time = {}      # Tracks last synchronization timestamps
file_last_checked = {}   # Tracks when files were last checked
file_last_modified = {}  # Tracks last modified timestamps
file_last_synced = {}    # Tracks when files were last successfully synced

### ==================  System Tray Functions ================== ###

def hide_terminal():
    """Hides the console window (Windows only)."""
    global whnd
    if sys.platform == "win32" and whnd:
        ctypes.windll.user32.ShowWindow(whnd, 0)

def show_terminal(icon, item):
    """Restores the console window (Windows only)."""
    global whnd
    if sys.platform == "win32" and whnd:
        ctypes.windll.user32.ShowWindow(whnd, 1)

def exit_program(icon, item):
    """Stops the system tray icon and exits the program."""
    icon.stop()
    sys.exit()

def check_minimize():
    """Continuously monitors the window state and hides it when minimized."""
    global whnd
    while True:
        time.sleep(1)
        if sys.platform == "win32" and whnd:
            if ctypes.windll.user32.IsIconic(whnd):  # If the window is minimized
                hide_terminal()

def setup_tray():
    """Creates and runs the system tray icon, allowing manual minimization."""
    try:
        image = Image.open("PokemonStadiumSync.ico")  # Ensure correct icon path
    except Exception as e:
        print(f"Error loading tray icon: {e}")
        return  # Don't exit the script if the icon fails to load

    menu = (item('Open Console', show_terminal), item('Exit', exit_program))
    tray_icon = Icon("PokemonStadiumSync", image, menu=menu)

    # Start monitoring for manual minimization
    threading.Thread(target=check_minimize, daemon=True).start()

    tray_icon.run()
    

### ==================  Configuration Handling ================== ###

# Initialize Config Parser
config = configparser.ConfigParser()
config.optionxform = str  # Preserve case sensitivity of keys

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

def load_config():
    """Loads configuration from file. Exits if file is missing or incomplete."""
    if not os.path.exists(CONFIG_FILE):
        print(f"\n{Fore.RED}[ERROR]{Fore.RESET} Config file '{CONFIG_FILE}' not found.")
        input("-> Please run the configuration tool (UI) to set it up before using this sync script.")
        sys.exit(1)

    config.read(CONFIG_FILE)

    # Warn if any section or key is missing
    for section, keys in DEFAULT_CONFIG.items():
        if not config.has_section(section):
            input(f"{Fore.RED}[ERROR]{Fore.RESET} Missing section in config: [{section}]")
            sys.exit(1)
        for key in keys:
            if key not in config[section]:
                input(f"{Fore.RED}[ERROR]{Fore.RESET} Missing config key: [{section}] {key}")
                sys.exit(1)


# Load Configuration
load_config()

# Read General Settings
stay_open = config.getboolean('General', 'stay_open', fallback=True)
run_minimized = config.getboolean('General', 'run_minimized', fallback=False)

# Hide terminal immediately if run_minimized is True
if run_minimized and sys.platform == "win32" and whnd:
    ctypes.windll.user32.ShowWindow(whnd, 0)

# Handle console minimization
if sys.platform == "win32":
    if whnd:
        try:
            tray_thread = threading.Thread(target=setup_tray, daemon=True)
            tray_thread.start()
        except Exception as e:
            print(f"Error starting system tray: {e}")

# Read Ports
retroarch_transferpak1 = config.get('Ports', 'retroarchtransferpak1', fallback='').strip()
retroarch_transferpak2 = config.get('Ports', 'retroarchtransferpak2', fallback='').strip()

# Read Directories & Normalize Paths
try:
    base_dir = os.path.normpath(config.get('Directories', 'base_dir'))
    gb_dir = os.path.join(base_dir, os.path.normpath(config.get('Directories', 'gb_dir')))
    gba_dir = os.path.join(base_dir, os.path.normpath(config.get('Directories', 'gba_dir')))
    sav_dir = os.path.join(base_dir, os.path.normpath(config.get('Directories', 'sav_dir')))
    gbrom_dir = os.path.join(base_dir, os.path.normpath(config.get('Directories', 'gbrom_dir')))
except configparser.NoOptionError as e:
    input(f"Error reading directories from config: {e}")
    sys.exit(1)


### ==================  Kill Running Instances ================== ###

def kill_previous_instances():
    """Kills older instances of PokemonStadiumSync while keeping the latest one alive."""
    current_pid = os.getpid()
    current_script = os.path.normcase(os.path.abspath(__file__))
    exe_name = "PokemonStadiumSync.exe"

    instances = []

    # Scan all running processes
    for process in psutil.process_iter(attrs=["pid", "name", "cmdline", "create_time"]):
        try:
            process_pid = process.info["pid"]
            process_name = process.info["name"]
            process_cmdline = process.info["cmdline"]
            process_start_time = process.info["create_time"]  # Get process start time

            # Skip self
            if process_pid == current_pid:
                continue

            # Check if process is another instance of this script or EXE
            if process_name.lower() == exe_name.lower():
                instances.append((process_pid, process_name, process_start_time))
            elif process_cmdline:
                for arg in process_cmdline:
                    if os.path.normcase(os.path.abspath(arg)) == current_script:
                        instances.append((process_pid, arg, process_start_time))
                        break

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    # Exit early if no instances were found
    if not instances:
        return

    # Sort instances by start time (oldest first)
    instances.sort(key=lambda x: x[2])

    # Keep the most recent instance and terminate all older ones
    for process_pid, process_name, _ in instances[:-1]:  # Keep only the last (newest) instance
        try:
            print(f"🛠️ DEBUG: Killing older instance (PID {process_pid}) - {process_name}")
            psutil.Process(process_pid).terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue


# Execute cleanup
kill_previous_instances()

### ==================  Game Slots & Save File Management ================== ###

# Read Stadium ROMs & Game Slots from Config
n64_roms = {key.lower(): value for key, value in config.items('StadiumROMs')} if config.has_section('StadiumROMs') else {}
gb_slots = {key.lower(): value for key, value in config.items('GBSlots')} if config.has_section('GBSlots') else {}
gba_slots = {key.lower(): value for key, value in config.items('GBASlots')} if config.has_section('GBASlots') else {}

# Assign Slot Numbers Dynamically
def assign_slot_numbers():
    """Dynamically assigns slot numbers to GB games."""
    return {game: i + 1 for i, game in enumerate(gb_slots.keys())}

slot_numbers = assign_slot_numbers()

# Define Game Name Formatting
def format_game_name(game_name):
    """Formats game names properly, handling special cases."""
    special_cases = {"firered": "FireRed", "leafgreen": "LeafGreen"}
    return special_cases.get(game_name.lower(), game_name.capitalize())

# Define Colors for Each Game Type
slot_colors = {
    "green": Fore.LIGHTGREEN_EX,
    "red": Fore.LIGHTRED_EX,
    "blue": Fore.LIGHTBLUE_EX,
    "yellow": Fore.YELLOW,
    "gold": Fore.LIGHTYELLOW_EX,
    "silver": Fore.LIGHTWHITE_EX,
    "crystal": Fore.LIGHTCYAN_EX,
    "ruby": Fore.RED,
    "sapphire": Fore.BLUE,
    "emerald": Fore.GREEN,
    "leafgreen": Fore.LIGHTGREEN_EX,
    "firered": Fore.LIGHTRED_EX
}


### ================== Save Synchronization ================== ###

def get_last_modified_time(file_path):
    """Get last modified time or 0 if file doesn't exist."""
    return os.path.getmtime(file_path) if os.path.exists(file_path) else 0

def get_transferpak_indicator(slot):
    slot_lower = slot.lower()
    if slot_lower == retroarch_transferpak1.lower():
        return f"{Fore.LIGHTBLACK_EX}]TransferPak{Fore.RED}1{Fore.RESET}"
    elif slot_lower == retroarch_transferpak2.lower():
        return f"{Fore.LIGHTBLACK_EX}]TransferPak{Fore.YELLOW}2{Fore.RESET}"
    return ""

def sync_files(slot, srm, sav, monitoring=False):
    color = slot_colors.get(slot.lower(), Fore.WHITE)
    formatted_slot = f"{color}{format_game_name(slot)}{Fore.RESET}"
    formatted_cart = f" {color}□{Fore.RESET}"
    transferpak_suffix = get_transferpak_indicator(slot)

    srm_exists = os.path.exists(srm)
    sav_exists = os.path.exists(sav)

    if monitoring:
        timestamp = time.strftime("[%H:%M] ")
    else:
        timestamp = ""

    if not srm_exists:
        print(f"{timestamp}{formatted_slot}: {Fore.LIGHTBLACK_EX}.srm file does not exist. Sync aborted.{Fore.RESET}")
        return

    if not sav_exists:
        print(f"{timestamp}{formatted_slot}: {Fore.LIGHTGREEN_EX}No .sav file found. Creating from .srm{Fore.LIGHTBLACK_EX} - {Fore.YELLOW}SRM → SAV{Fore.LIGHTBLACK_EX} - {Fore.RESET}{formatted_cart}{transferpak_suffix}")
        shutil.copy2(srm, sav)
        os.utime(sav, (get_last_modified_time(srm), get_last_modified_time(srm)))
        return

    srm_time, sav_time = get_last_modified_time(srm), get_last_modified_time(sav)

    if srm_time == sav_time:
        print(f"{timestamp}{formatted_slot}: Saves are already synced{Fore.LIGHTBLACK_EX} - {Fore.RESET}SRM ↔ SAV{Fore.LIGHTBLACK_EX} - {Fore.RESET}{formatted_cart}{transferpak_suffix}")
        return

    action_color = Fore.CYAN if monitoring else Fore.LIGHTGREEN_EX

    if srm_time > sav_time:
        print(f"{timestamp}{formatted_slot}: {action_color}The .sav is outdated. Replacing it with .srm{Fore.LIGHTBLACK_EX} - {Fore.YELLOW}SRM → SAV{Fore.LIGHTBLACK_EX} - {Fore.RESET}{formatted_cart}{transferpak_suffix}")
        shutil.copy2(srm, sav)
        os.utime(sav, (srm_time, srm_time))
    else:
        print(f"{timestamp}{formatted_slot}: {action_color}The .srm is outdated. Replacing it with .sav{Fore.LIGHTBLACK_EX} - {Fore.YELLOW}SRM ← SAV{Fore.LIGHTBLACK_EX} - {Fore.RESET}{formatted_cart}{transferpak_suffix}")
        shutil.copy2(sav, srm)
        os.utime(srm, (sav_time, sav_time))

# Sync GB slots
for game_name, srm_filename in gb_slots.items():
    srm_path = os.path.join(gb_dir, f"{srm_filename}.srm")
    slot_number = slot_numbers.get(game_name, 'X')
    formatted_game_name = format_game_name(game_name)

    if game_name.lower() == retroarch_transferpak1.lower():
        sav_filename = f"{n64_roms.get('stadium 1', '')}.sav"
    elif game_name.lower() == retroarch_transferpak2.lower():
        sav_filename = f"{n64_roms.get('stadium 2', '')}.sav"
    else:
        sav_filename = f"PkmnTransferPak{slot_number} {formatted_game_name}.sav"

    sav_path = os.path.join(sav_dir, sav_filename)
    sync_files(game_name, srm_path, sav_path)

# Sync GBA slots
for gba_slot, rom_filename in gba_slots.items():
    srm_path = os.path.join(gba_dir, f"{rom_filename}.srm")
    sav_path = os.path.join(sav_dir, f"{rom_filename}-2.sav")
    sync_files(gba_slot, srm_path, sav_path)

 
### ==================  File Monitoring ================== ###

# Cache for RetroArch status
_last_check_time = 0
_retroarch_status = False

# Optimized function to check if RetroArch is running
def is_retroarch_running():
    """Checks if RetroArch is running, optimized for performance with caching."""
    global _last_check_time, _retroarch_status
    now = time.time()

    # Check at most every 30 seconds
    if now - _last_check_time < 30:
        return _retroarch_status

    _last_check_time = now
    try:
        for p in psutil.process_iter(["name"]):
            if p.info["name"] and "retroarch" in p.info["name"].lower():
                _retroarch_status = True
                return True
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass

    _retroarch_status = False
    return False

# Optimized function to check if files should sync
def should_sync(srm, sav):
    """Determine if two files should be synced."""
    current_time = time.time()

    # Get file modification times only once
    srm_time, sav_time = get_last_modified_time(srm), get_last_modified_time(sav)

    # If either file does not exist, return False
    if srm_time == 0 or sav_time == 0:
        return False

    # If timestamps match, they're already synced
    if srm_time == sav_time:
        return False

    # Don't sync if RetroArch is running
    if is_retroarch_running():
        return False

    # Only sync if no changes in the last 30 seconds
    return (current_time - max(srm_time, sav_time)) >= 30

class SaveFileEventHandler(FileSystemEventHandler):
    """Handles file modifications and triggers sync when needed."""

    def on_modified(self, event):
        """Triggered when a save file (.srm or .sav) is modified."""
        if event.is_directory:
            return

        filepath = os.path.normcase(os.path.abspath(event.src_path))

        # Track whether we already handled a match to prevent duplicate processing
        handled = False

        # Check GB save files
        for game_name, srm_filename in gb_slots.items():
            srm_path = os.path.normcase(os.path.abspath(os.path.join(gb_dir, f"{srm_filename}.srm")))
            slot_number = slot_numbers.get(game_name, 'X')
            formatted_game_name = format_game_name(game_name)
            sav_filename = f"PkmnTransferPak{slot_number} {formatted_game_name}.sav"

            if game_name == retroarch_transferpak1.lower():
                sav_filename = f"{n64_roms.get('stadium 1', '')}.sav"
            elif game_name == retroarch_transferpak2.lower():
                sav_filename = f"{n64_roms.get('stadium 2', '')}.sav"

            sav_path = os.path.normcase(os.path.abspath(os.path.join(sav_dir, sav_filename)))

            if filepath in [srm_path, sav_path] and should_sync(srm_path, sav_path):
                if not handled:
                    sync_files(game_name, srm_path, sav_path, monitoring=True)
                    handled = True
                return  # Exit after first sync

        # Check GBA save files
        for gba_slot, rom_filename in gba_slots.items():
            srm_path = os.path.normcase(os.path.abspath(os.path.join(gba_dir, f"{rom_filename}.srm")))
            sav_filename = f"{rom_filename}-2.sav"
            sav_path = os.path.normcase(os.path.abspath(os.path.join(sav_dir, sav_filename)))

            if filepath in [srm_path, sav_path] and should_sync(srm_path, sav_path):
                if not handled:
                    sync_files(gba_slot, srm_path, sav_path, monitoring=True)
                    handled = True
                return  # Exit after first sync


# Initialize and start the watchdog observer
observer = Observer()
save_event_handler = SaveFileEventHandler()

# Schedule observers ONLY on directories containing save files
for name, path in [
    ("GB Save Directory", gb_dir),
    ("GBA Save Directory", gba_dir),
    ("TransferPak Save Directory", sav_dir)
]:
    try:
        if not os.path.exists(path):
            raise FileNotFoundError(f"{Fore.RED}[ERROR]{Fore.RESET} '{path}' does not exist.")
        observer.schedule(save_event_handler, path=path, recursive=False)
    except Exception as e:
        print(f"\n{Fore.RED}[ERROR]{Fore.RESET} Failed to monitor {name}: {path}")
        input("-> Please check your configuration and make sure the folder exists.")
        sys.exit(1)


observer.start()

print()
print(f"{Fore.LIGHTMAGENTA_EX}Monitoring savefiles for changes...{Fore.RESET}")

def periodic_sync_check(interval=120):
    """Periodically checks save files for syncing in case missed by watchdog."""
    last_synced = {}  # Dictionary to track last sync times for each file

    while True:
        time.sleep(interval)

        # Periodically check GB save files
        for game_name, srm_filename in gb_slots.items():
            srm_path = os.path.abspath(os.path.join(gb_dir, f"{srm_filename}.srm"))
            slot_number = slot_numbers.get(game_name, 'X')
            formatted_game_name = format_game_name(game_name)
            sav_filename = f"PkmnTransferPak{slot_number} {formatted_game_name}.sav"

            if game_name == retroarch_transferpak1.lower():
                sav_filename = f"{n64_roms.get('stadium 1', '')}.sav"
            elif game_name == retroarch_transferpak2.lower():
                sav_filename = f"{n64_roms.get('stadium 2', '')}.sav"

            sav_path = os.path.abspath(os.path.join(sav_dir, sav_filename))

            # Ensure last_sync_time is set before checking it
            last_sync_time = last_synced.get(game_name, 0)

            if should_sync(srm_path, sav_path) and (time.time() - last_sync_time > 5):
                sync_files(game_name, srm_path, sav_path, monitoring=True)
                last_synced[game_name] = time.time()  # Update last sync time

        # Periodically check GBA save files
        for gba_slot, rom_filename in gba_slots.items():
            srm_path = os.path.abspath(os.path.join(gba_dir, f"{rom_filename}.srm"))
            sav_filename = f"{rom_filename}-2.sav"
            sav_path = os.path.abspath(os.path.join(sav_dir, sav_filename))

            # Ensure last_sync_time is set before checking it
            last_sync_time = last_synced.get(gba_slot, 0)

            if should_sync(srm_path, sav_path) and (time.time() - last_sync_time > 5):
                sync_files(gba_slot, srm_path, sav_path, monitoring=True)
                last_synced[gba_slot] = time.time()  # Update last sync time



# Start periodic checker in background
periodic_thread = threading.Thread(target=periodic_sync_check, args=(30,), daemon=True)
periodic_thread.start()

### ==================  End print ================== ###
if stay_open:
    input()