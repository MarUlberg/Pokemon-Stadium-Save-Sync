import os

import shutil

# Set to True to keep the window open after the program finishes
stay_open = False

# Save Port
RetroarchTransferPak1 = ""
RetroarchTransferPak2 = ""
DolphinPort2 = ""
DolphinPort3 = ""
DolphinPort4 = ""

# Directories
base_dir = "H:/LaunchBox/!Emulators/RetroArch"
gb_dir = os.path.join(base_dir, "saves/Nintendo - Game Boy") # Set subfolder for GameBoy .srm files
gba_dir = os.path.join(base_dir, "saves/Nintendo - Game Boy Advance") # Set subfolder for GameBoyAdvance .srm files
sav_dir = os.path.join(base_dir, "saves/stadium")  # Set subfolder with Pokemon Stadium ROM

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

def get_last_modified_time(file_path):
    return os.path.getmtime(file_path)

def delete_and_replace(slot, srm, sav):
    try:
        if not os.path.exists(srm):
            print(f"{slot}: srm does not exist.")
            return
        
        if not os.path.exists(sav):
            print(f"{slot}: sav was missing, creating a new copy from srm.")
            shutil.copy2(srm, sav)
            return

        # Get last modified times if both files exist
        srm_modified_time = get_last_modified_time(srm)
        sav_modified_time = get_last_modified_time(sav)

        # Determine which file is older
        if srm_modified_time > sav_modified_time:
            print(f"{slot}: sav is older. Deleting and replacing it with srm.")
            os.remove(sav)
            shutil.copy2(srm, sav)
        else:
            print(f"{slot}: srm is older. Deleting and replacing it with sav.")
            os.remove(srm)
            shutil.copy2(sav, srm)

        print(f"Replacement of {slot} completed.")
    except Exception as e:
        print(f"{slot}: An error occurred with srm and sav: {e}")

# Check for duplicate game assignments
assigned_games = [game for game in [RetroarchTransferPak1, RetroarchTransferPak2, DolphinPort2, DolphinPort3, DolphinPort4] if game]
if len(assigned_games) != len(set(assigned_games)):
    print("Error: Multiple ports are assigned to the same game. Please check your configuration.")
    print('Press Enter to exit...')
    input()
    exit(1)

# Ensure a valid Stadium ROM is set if a Transfer Pak is used
if RetroarchTransferPak1 and not n64_roms.get("Stadium 1"): 
    print("Error: RetroarchTransferPak1 is set, but Stadium 1 does not have a ROM assigned!")
    print('Press Enter to exit...')
    input()
    exit(1)

if RetroarchTransferPak2 and not n64_roms.get("Stadium 2"): 
    print("Error: RetroarchTransferPak2 is set, but Stadium 2 does not have a ROM assigned!")
    print('Press Enter to exit...')
    input()
    exit(1)

# Run the function for each GB slot
assigned_games = [game for game in [RetroarchTransferPak1, RetroarchTransferPak2, DolphinPort2, DolphinPort3, DolphinPort4] if game]
if len(assigned_games) != len(set(assigned_games)):
    print("Error: Multiple ports are assigned to the same game. Please check your configuration.")
    print('Press Enter to exit...')
    input()
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
    sav_filename = srm_filename.replace(".srm", ".sav")
    
    # Adjust sav filename for the DolphinPort
    for port, assigned_slot in {"2": DolphinPort2, "3": DolphinPort3, "4": DolphinPort4}.items():
        if gba_slot == assigned_slot:
            sav_filename = sav_filename.replace(".sav", f"-{port}.sav")
    
    sav_path = os.path.join(sav_dir, sav_filename)
    delete_and_replace(gba_slot, srm_path, sav_path)

# Check for ROM files 
for key, rom in n64_roms.items():
    if rom.strip():
        rom_file = os.path.join(sav_dir, rom)
        if not os.path.exists(rom_file):
            print(f"Warning: {rom} is missing!")

for key, rom in n64_roms.items():
    if rom.strip():
        gb_file = os.path.join(sav_dir, rom + ".gb")
        if not os.path.exists(gb_file):
            print(f"Warning: {rom}.gb is missing!")

# Keep the window open if required
if stay_open:
    input("Press Enter to close the window...")
