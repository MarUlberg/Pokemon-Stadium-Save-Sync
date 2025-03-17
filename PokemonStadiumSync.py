import os
import shutil
import configparser
import sys
import pystray
from pystray import MenuItem as item, Icon
from PIL import Image
from colorama import init, Fore
import time
import psutil
import threading
import ctypes

# Global variables here
if sys.platform == "win32":
    whnd = ctypes.windll.kernel32.GetConsoleWindow()
else:
    whnd = None

last_sync_time = {}
file_last_checked = {}
file_last_modified = {}
file_last_synced = {}

# 🟢 System Tray Functions (Define First!)
def hide_terminal():
    global whnd
    if sys.platform == "win32":
        if whnd is None:
            whnd = ctypes.windll.kernel32.GetConsoleWindow()
        if whnd:
            ctypes.windll.user32.ShowWindow(whnd, 0)

def show_terminal(icon, item):
    global whnd
    if sys.platform == "win32":
        if whnd is None:
            whnd = ctypes.windll.kernel32.GetConsoleWindow()
        if whnd:
            ctypes.windll.user32.ShowWindow(whnd, 1)

def exit_program(icon, item):
    icon.stop()
    sys.exit()

def setup_tray():
    """ Create and run the system tray icon with window minimization support. """
    global whnd
    try:
        image = Image.open("PokemonStadiumSync.ico")  # Ensure correct icon path
    except Exception as e:
        print(f"Error loading tray icon: {e}")
        sys.exit()

    menu = (item('Open Console', show_terminal), item('Exit', exit_program))
    tray_icon = Icon("PokemonStadiumSync", image, menu=menu)

    def check_minimize():
        """ Monitor and hide window when minimized. """
        global whnd
        while True:
            time.sleep(1)
            if sys.platform == "win32":
                if whnd is None:
                    whnd = ctypes.windll.kernel32.GetConsoleWindow()
                if whnd and ctypes.windll.user32.IsIconic(whnd):
                    hide_terminal()

    threading.Thread(target=check_minimize, daemon=True).start()
    tray_icon.run()


# Initialize colorama for Windows support
init(autoreset=True)

# Load configuration
config = configparser.ConfigParser()
config.optionxform = str  # Preserve case sensitivity of keys

config_file = 'PokemonStadiumSync.cfg'
if not os.path.exists(config_file):
    print(f"Error: Configuration file '{config_file}' not found!")
    sys.exit(1)  # Exit if the config is missing

config.read(config_file)

# Read general settings
stay_open = config.getboolean('General', 'stay_open', fallback=True)
run_minimized = config.getboolean('General', 'run_minimized', fallback=False)

# Handle console minimization
if run_minimized and sys.platform == "win32":
    whnd = ctypes.windll.kernel32.GetConsoleWindow()
    if whnd:
        print("Starting in system tray mode...")
        ctypes.windll.user32.ShowWindow(whnd, 0)  # Hide console immediately

        try:
            tray_thread = threading.Thread(target=setup_tray, daemon=True)
            tray_thread.start()
        except Exception as e:
            print(f"Error starting system tray: {e}")
            print("Falling back to normal mode.")
            ctypes.windll.user32.ShowWindow(whnd, 1)  # Restore console
            run_minimized = False  # Disable minimization fallback


# Read ports
retroarch_transferpak1 = config.get('Ports', 'retroarchtransferpak1', fallback='').strip()
retroarch_transferpak2 = config.get('Ports', 'retroarchtransferpak2', fallback='').strip()

# Read directories
try:
    base_dir = os.path.normpath(config.get('Directories', 'base_dir'))
    gb_dir = os.path.join(base_dir, os.path.normpath(config.get('Directories', 'gb_dir')))
    gba_dir = os.path.join(base_dir, os.path.normpath(config.get('Directories', 'gba_dir')))
    sav_dir = os.path.join(base_dir, os.path.normpath(config.get('Directories', 'sav_dir')))
    gbrom_dir = os.path.join(base_dir, os.path.normpath(config.get('Directories', 'gbrom_dir')))
except configparser.NoOptionError as e:
    print(f"Error reading directories from config: {e}")
    sys.exit(1)

# Read Stadium ROMs & Game Slots
n64_roms = {key.lower(): value for key, value in config.items('StadiumROMs')} if config.has_section('StadiumROMs') else {}
gb_slots = {key.lower(): value for key, value in config.items('GBSlots')} if config.has_section('GBSlots') else {}
gba_slots = {key.lower(): value for key, value in config.items('GBASlots')} if config.has_section('GBASlots') else {}

# Assign slot numbers dynamically
slot_numbers = {game: i + 1 for i, game in enumerate(gb_slots.keys())}


# Function to format game names correctly
def format_game_name(game_name):
    special_cases = {"firered": "FireRed", "leafgreen": "LeafGreen"}
    return special_cases.get(game_name.lower(), game_name.capitalize())

# Define colors using colorama
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

# Function Definitions
def get_last_modified_time(file_path):
    """Get the last modified time of a file. Return 0 if file does not exist."""
    return os.path.getmtime(file_path) if os.path.exists(file_path) else 0

def delete_and_replace(slot, srm, sav, monitoring=False):
    color = slot_colors.get(slot.lower(), Fore.WHITE)
    formatted_slot = f"{color}{format_game_name(slot)}{Fore.RESET}"

    if not os.path.exists(srm):
        print(f"{formatted_slot}: {Fore.LIGHTBLACK_EX}.srm file does not exist.{Fore.RESET}")
        return

    if not os.path.exists(sav):
        print(f"{formatted_slot}: {Fore.LIGHTGREEN_EX}.sav file missing. Creating from .srm...{Fore.RESET}")
        shutil.copy2(srm, sav)
        os.utime(sav, (get_last_modified_time(srm), get_last_modified_time(srm)))
        return

    srm_time = get_last_modified_time(srm)
    sav_time = get_last_modified_time(sav)

    if srm_time == sav_time:
        print(f"{formatted_slot}: Saves are already synced.")
        return

    # Select color dynamically based on monitoring mode
    action_color = Fore.CYAN if monitoring else Fore.LIGHTGREEN_EX

    if srm_time > sav_time:
        print(f"{formatted_slot}: {action_color}.sav is older. Replacing it with .srm.{Fore.RESET}")
        os.remove(sav)
        shutil.copy2(srm, sav)
        os.utime(sav, (srm_time, srm_time))
    else:
        print(f"{formatted_slot}: {action_color}.srm is older. Replacing it with .sav.{Fore.RESET}")
        os.remove(srm)
        shutil.copy2(sav, srm)
        os.utime(srm, (sav_time, sav_time))



# Run synchronization for GB slots
for game_name, srm_filename in gb_slots.items():
    srm_path = os.path.join(gb_dir, srm_filename + ".srm")
    slot_number = slot_numbers.get(game_name, 'X')  # Get slot number dynamically
    formatted_game_name = format_game_name(game_name)
    sav_filename = f"PkmnTransferPak{slot_number} {formatted_game_name}.sav"
    
    if game_name == retroarch_transferpak1.lower():
        sav_filename = f"{n64_roms.get('stadium 1', '')}.sav"
    elif game_name == retroarch_transferpak2.lower():
        sav_filename = f"{n64_roms.get('stadium 2', '')}.sav"
    
    sav_path = os.path.join(sav_dir, sav_filename)
    delete_and_replace(game_name, srm=srm_path, sav=sav_path)

# Run synchronization for GBA slots
for gba_slot, srm_filename in gba_slots.items():
    srm_path = os.path.join(gba_dir, srm_filename + ".srm")
    
    # Use the actual ROM filename instead of just the slot name
    rom_filename = gba_slots.get(gba_slot, "")  # Get the full ROM filename
    if not rom_filename:
        print(f"{Fore.RED}Error: No ROM filename found for {gba_slot}{Fore.RESET}")
        continue
    
    sav_filename = f"{rom_filename}-2.sav"  # Ensure the correct format
    sav_path = os.path.join(sav_dir, sav_filename)
    
    delete_and_replace(gba_slot, srm_path, sav_path)

# Dictionary to track last sync time
_last_check_time = 0
_retroarch_status = False

def is_retroarch_running():
    """Check if RetroArch is currently running, with caching for performance."""
    global _last_check_time, _retroarch_status
    now = time.time()

    # Only check every 10 seconds
    if now - _last_check_time < 10:
        return _retroarch_status

    _last_check_time = now
    _retroarch_status = any('retroarch' in p.info['name'].lower() for p in psutil.process_iter(attrs=['name']))
    
    return _retroarch_status

def should_sync(srm, sav):
    """Determine if two files should be synced."""
    current_time = time.time()

    # Both files must exist
    if not os.path.exists(srm) or not os.path.exists(sav):
        return False

    srm_time = get_last_modified_time(srm)
    sav_time = get_last_modified_time(sav)
    latest_change_time = max(srm_time, sav_time)

    # Skip if timestamps are equal (already synced)
    if srm_time == sav_time:
        return False

    # Don't sync if RetroArch is running
    if is_retroarch_running():
        return False

    # Only sync if no changes in the last 60 seconds
    if (current_time - max(srm_time, sav_time)) < 60:
        return False

    return True


def files_need_sync(srm, sav):
    """Return True only if both files exist and timestamps differ."""
    if not (os.path.exists(srm) and os.path.exists(sav)):
        return False  # Can't sync if one doesn't exist
    
    return get_last_modified_time(srm) != get_last_modified_time(sav)



def monitor_files():
    """Monitor save files for changes and re-sync when appropriate."""
    while True:
        try:
            time.sleep(5)  # Avoid excessive CPU usage
            current_time = time.time()

            # Monitor GB files
            for game_name, srm_filename in gb_slots.items():
                srm_path = os.path.join(gb_dir, srm_filename + ".srm")
                slot_number = slot_numbers.get(game_name, 'X')
                formatted_game_name = format_game_name(game_name)
                sav_filename = f"PkmnTransferPak{slot_number} {formatted_game_name}.sav"

                if game_name == retroarch_transferpak1.lower():
                    sav_filename = f"{n64_roms.get('stadium 1', '')}.sav"
                elif game_name == retroarch_transferpak2.lower():
                    sav_filename = f"{n64_roms.get('stadium 2', '')}.sav"

                sav_path = os.path.join(sav_dir, sav_filename)

                # Check both files exist and are different
                if files_need_sync(srm_path, sav_path):
                    # Only sync if stable and RetroArch not running
                    if (current_time - max(get_last_modified_time(srm_path), get_last_modified_time(sav_path)) >= 60
                        and not is_retroarch_running()):
                        delete_and_replace(game_name, srm_path, sav_path, monitoring=True)

            # Monitor GBA files
            for gba_slot, srm_filename in gba_slots.items():
                srm_path = os.path.join(gba_dir, srm_filename + ".srm")
                rom_filename = gba_slots.get(gba_slot, "")

                if not rom_filename:
                    continue

                sav_filename = f"{rom_filename}-2.sav"
                sav_path = os.path.join(sav_dir, sav_filename)

                if files_need_sync(srm_path, sav_path):
                    print(f"{Fore.CYAN}Syncing: {game_name}{Fore.RESET}")
                    delete_and_replace(game_name, srm_path, sav_path, monitoring=True)


        except Exception as e:
            print(f"{Fore.RED}Error in monitor_files(): {e}{Fore.RESET}")






# Start file monitoring in a separate thread
monitor_thread = threading.Thread(target=monitor_files, daemon=True)
monitor_thread.start()

print()
print(f"{Fore.MAGENTA}Monitoring savefiles for changes...{Fore.RESET}")
if stay_open:
    input()
