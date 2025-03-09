import os

import shutil

# Set to True to keep the window open after the program finishes
stay_open = True

# Save Port
RetroarchTransferPak1 = ""
RetroarchTransferPak2 = ""

# Directories
base_dir = "H:/LaunchBox/!Emulators/RetroArch"
gb_dir = os.path.join(base_dir, "saves/Nintendo - Game Boy") # Set subfolder for GameBoy .srm files
gba_dir = os.path.join(base_dir, "saves/Nintendo - Game Boy Advance") # Set subfolder for GameBoyAdvance .srm files
sav_dir = os.path.join(base_dir, "saves/TransferPak")  # Set subfolder with Pokemon Stadium ROM
gbrom_dir = os.path.join(base_dir, "games/Nintendo - Game Boy")  # Set subfolder with Game Boy ROMs

# Stadium ROMs
n64_roms = {
    "Stadium 1": "Pokemon Stadium (USA).n64",
    "Stadium 2": "Pokemon Stadium 2 (USA).n64"
}
# Save Slots
gb_slots = {
    "Green": "Pokemon - Green Version (Blue Version (USA, Europe) (SGB Enhanced))(patched).srm",
    "Red": "Pokemon - Red Version (USA, Europe) (SGB Enhanced).srm",
    "Blue": "Pokemon - Blue Version (USA, Europe) (SGB Enhanced).srm",
    "Yellow": "Pokemon - Yellow Version - Special Pikachu Edition (Pokemon Playable Yellow) (v1.0) (alt).srm",
    "Gold": "Pokemon - Gold Version (USA, Europe) (SGB Enhanced) (GB Compatible).srm",
    "Silver": "Pokemon - Silver Version (USA, Europe) (SGB Enhanced) (GB Compatible).srm",
    "Crystal": "Pokemon - Crystal Version (USA, Europe) (Rev 1).srm",
}
gba_slots = {
    "Ruby": "Pokemon - Ruby Version (USA, Europe) (Rev 2).srm",
    "Sapphire": "Pokemon - Sapphire Version (USA, Europe) (Rev 2).srm",
    "Emerald": "Pokemon - Emerald Version (USA, Europe).srm",
    "FireRed": "Pokemon - FireRed Version (USA, Europe).srm",
    "LeafGreen": "Pokemon - LeafGreen Version (USA, Europe).srm",
}

# Check if base_dir exists
if not os.path.exists(base_dir):
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Search for RetroArch folder (case-insensitive)
    parts = script_dir.split(os.path.sep)
    parts_lower = [part.lower() for part in parts]  # Convert all parts to lowercase

    if "retroarch" in parts_lower:
        retroarch_index = parts_lower.index("retroarch")  # Find index of RetroArch (case-insensitive)
        base_dir = os.path.sep.join(parts[:retroarch_index + 1])  # Reconstruct correct path
    else:
        print("Unable to locate RetroArch folder.")

def get_last_modified_time(file_path):
    """Get the last modified time of a file, or return None if the file doesn't exist."""
    if os.path.exists(file_path):
        return os.path.getmtime(file_path)
    return None

def delete_and_replace(slot, srm, sav):
    """Checks and synchronizes .srm and .sav files by replacing the older one."""
    try:
        # Validate paths
        if not srm or not sav:
            print(f"{slot}: Invalid file paths. Check your configuration.")
            return

        # Ensure .srm file exists before proceeding
        if not os.path.exists(srm):
            print(f"{slot}: .srm file does not exist.")
            return

        # If .sav file is missing, create it from .srm
        if not os.path.exists(sav):
            print(f"{slot}: .sav file is missing. Creating from .srm...")
            try:
                shutil.copy2(srm, sav)
            except PermissionError:
                print(f"Error: Permission denied while copying {srm} to {sav}. Ensure the file is not in use.")
            except shutil.SameFileError:
                print(f"Warning: Source and destination files are identical ({srm}). Skipping copy.")
            except Exception as e:
                print(f"Unexpected error while creating {sav}: {e}")
            return  # Exit function after handling the missing file

        # Get last modified times for both files
        srm_modified_time = get_last_modified_time(srm)
        sav_modified_time = get_last_modified_time(sav)

        # If timestamps could not be retrieved, abort operation
        if srm_modified_time is None or sav_modified_time is None:
            print(f"{slot}: Error retrieving file timestamps. Skipping operation.")
            return

        # Compare timestamps and replace the older file
        if srm_modified_time > sav_modified_time:
            print(f"{slot}: .sav is older. Replacing it with .srm.")
            try:
                os.remove(sav)
                shutil.copy2(srm, sav)
            except Exception as e:
                print(f"{slot}: Error replacing .sav with .srm: {e}")
        else:
            print(f"{slot}: .srm is older. Replacing it with .sav.")
            try:
                os.remove(srm)
                shutil.copy2(sav, srm)
            except Exception as e:
                print(f"{slot}: Error replacing .srm with .sav: {e}")

    except PermissionError:
        print(f"{slot}: Permission denied. Ensure the files are not in use.")
    except FileNotFoundError:
        print(f"{slot}: One of the files was deleted before the operation.")
    except Exception as e:
        print(f"{slot}: Unexpected error: {e}")


# Check for duplicate game assignments
assigned_games = [game for game in [RetroarchTransferPak1, RetroarchTransferPak2] if game]
if len(assigned_games) != len(set(assigned_games)):
    print("Error: Multiple ports are assigned to the same game. Please check your configuration.")
    input("Press Enter to exit...")
    exit(1)

# Ensure a valid Stadium ROM is set if a Transfer Pak is used
if RetroarchTransferPak1 and not n64_roms.get("Stadium 1"): 
    print("Error: RetroarchTransferPak1 is set, but Stadium 1 does not have a ROM assigned!")
    input("Press Enter to exit...")
    exit(1)

if RetroarchTransferPak2 and not n64_roms.get("Stadium 2"): 
    print("Error: RetroarchTransferPak2 is set, but Stadium 2 does not have a ROM assigned!")
    input("Press Enter to exit...")
    exit(1)

# Run the function for each GB slot
slot_numbers = {"Green": 1, "Red": 2, "Blue": 3, "Yellow": 4, "Gold": 5, "Silver": 6, "Crystal": 7}
for game_name, srm_filename in gb_slots.items():
    srm_path = os.path.join(gb_dir, srm_filename)
    
    # Generate sav filename dynamically
    slot_number = slot_numbers.get(game_name, "X")
    sav_filename = f"PkmnTransferPak{slot_number} {game_name}.sav"
    
    # Adjust sav filename for the RetroarchTransferPak Port
    if game_name == RetroarchTransferPak1:
        sav_filename = n64_roms["Stadium 1"] + ".sav"
    elif game_name == RetroarchTransferPak2:
        sav_filename = n64_roms["Stadium 2"] + ".sav"
    
    sav_path = os.path.join(sav_dir, sav_filename)
    delete_and_replace(game_name, srm_path, sav_path)

# Run the function for each GBA slot
for gba_slot, srm_filename in gba_slots.items():
    srm_path = os.path.join(gba_dir, srm_filename)
    sav_filename = srm_filename.replace(".srm", "-2.sav")
    sav_path = os.path.join(sav_dir, sav_filename)
    delete_and_replace(gba_slot, srm_path, sav_path)
    
# Check and fix missing .gb files
for key, rom in n64_roms.items():
    if rom.strip():
        gb_file = os.path.join(sav_dir, rom + ".gb")  # Where it should be stored
        gb_file = os.path.normpath(gb_file).replace("\\", "/")  # Ensure forward slashes

        # Determine the correct Game Boy ROM based on the assigned RetroarchTransferPak
        if key == "Stadium 1":
            gb_rom_name = gb_slots.get(RetroarchTransferPak1, None)  # Look up .srm file
        elif key == "Stadium 2":
            gb_rom_name = gb_slots.get(RetroarchTransferPak2, None)  # Look up .srm file
        else:
            gb_rom_name = None

        if gb_rom_name:
            # Remove .srm extension and use as .gb filename
            gb_rom_name = gb_rom_name.replace(".srm", ".gb")
            gbrom_path = os.path.join(gbrom_dir, gb_rom_name)  # Path in gbrom_dir
            gbrom_path = os.path.normpath(gbrom_path).replace("\\", "/")  # Ensure forward slashes

            if not os.path.exists(gb_file):

                try:
                    if os.path.exists(gbrom_path):
                        shutil.copy2(gbrom_path, gb_file)
                        print(f"Created {rom}.gb from {gbrom_path}.")
                    else:
                        print(f"Error: {gbrom_path} does not exist. Unable to create {rom}.gb.")
                except Exception as e:
                    print(f"Error restoring {rom}.gb: {e}")


# Check for ROM files 
for key, rom in n64_roms.items():
    if rom.strip():
        rom_file = os.path.join(sav_dir, rom)
        if not os.path.exists(rom_file):
            print(f"Warning: {rom} is missing!")

# Keep the window open if required
if stay_open:
    input("Press Enter to close the window...")
