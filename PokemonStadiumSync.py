import os
import shutil

# Set to True to keep the window open after the program finishes
stay_open = True

# Set the main save slot
RetroarchTransferPak = "gb.slot3"
DolphinPort2 = "gba.slot3"
DolphinPort3 = "gba.slot2"
DolphinPort4 = "gba.slot1"

# Base directories
base_dir = r"H:\LaunchBox\!Emulators\RetroArch\saves"
stadium_dir = os.path.join(base_dir, "stadium")

# Define slot mappings
gba_slots = {
    "gba.slot1": "Pokemon - Ruby Version (USA, Europe) (Rev 2).srm",
    "gba.slot2": "Pokemon - Sapphire Version (USA, Europe) (Rev 2).srm",
    "gba.slot3": "Pokemon - Emerald Version (USA, Europe).srm",
    "gba.slot4": "Pokemon - FireRed Version (USA, Europe).srm",
    "gba.slot5": "Pokemon - LeafGreen Version (USA, Europe) (Rev 1).srm",
}
gb_slots = {
    "gb.slot1": ("Pokemon - Green Version (Blue Version (USA, Europe) (SGB Enhanced))(patched).srm", "PkmnTransferPak1 Green.sav"),
    "gb.slot2": ("Pokemon - Red Version (USA, Europe) (SGB Enhanced).srm", "PkmnTransferPak2 Red.sav"),
    "gb.slot3": ("Pokemon - Blue Version (USA, Europe) (SGB Enhanced) (Pokemon Playable Blue)(patched).srm", "PkmnTransferPak3 Blue.sav"),
    "gb.slot4": ("Pokemon - Yellow Version - Special Pikachu Edition (Pokemon Playable Yellow) (v1.0) (alt).srm", "PkmnTransferPak4 Yellow.sav"),
    "gb.slot5": ("Pokemon - Gold Version (USA, Europe) (SGB Enhanced) (GB Compatible).srm", "PkmnTransferPak5 Gold.sav"),
    "gb.slot6": ("Pokemon - Silver Version (USA, Europe) (SGB Enhanced) (GB Compatible).srm", "PkmnTransferPak6 Silver.sav"),
    "gb.slot7": ("Pokemon - Crystal Version (USA, Europe) (Rev 1).srm", "PkmnTransferPak7 Crystal.sav"),
}

def get_last_modified_time(file_path):
    return os.path.getmtime(file_path)

def delete_and_replace(slot, srm, sav):
    try:
        # Check if the files exist
        srm_exists = os.path.exists(srm)
        sav_exists = os.path.exists(sav)

        if not srm_exists:
            print(f"{slot}: srm does not exist.")
            return
        
        if not sav_exists:
            print(f"{slot}: sav was missing, so a new copy has been created from {srm}")
            shutil.copy2(srm, sav)
        else:
            # Get last modified times if both files exist
            srm_modified_time = get_last_modified_time(srm)
            sav_modified_time = get_last_modified_time(sav)

            # Determine which file is older
            if srm_modified_time > sav_modified_time:
                print(f"{slot}: sav is older. Deleting and replacing it with {srm}")
                os.remove(sav)
                shutil.copy2(srm, sav)
            else:
                print(f"{slot}: srm is older. Deleting and replacing it with {sav}")
                os.remove(srm)
                shutil.copy2(sav, srm)

            print(f"Replacement of {slot} completed.")
    except Exception as e:
        print(f"{slot}: An error occurred with srm and sav: {e}")

# Run the function for each GB slot
for slot, (srm_filename, sav_filename) in gb_slots.items():
    srm_path = os.path.join(base_dir, srm_filename)
    
    # Adjust sav filename for the RetroarchTransferPak slot
    if slot == RetroarchTransferPak:
        sav_filename = "Pokemon Stadium (USA).n64.sav"
    
    sav_path = os.path.join(stadium_dir, sav_filename)
    delete_and_replace(slot, srm_path, sav_path)

# Run the function for each GBA slot
for gba_slot, srm_filename in gba_slots.items():
    srm_path = os.path.join(base_dir, srm_filename)
    sav_filename = srm_filename.replace(".srm", ".sav")
    
    # Check if this gba_slot is assigned to a DolphinPort
    for port, assigned_slot in {"2": DolphinPort2, "3": DolphinPort3, "4": DolphinPort4}.items():
        if gba_slot == assigned_slot:
            sav_filename = sav_filename.replace(".sav", f"-{port}.sav")
    
    sav_path = os.path.join(stadium_dir, sav_filename)
    delete_and_replace(gba_slot, srm_path, sav_path)

# Keep the window open if required
if stay_open:
    input("Press Enter to close the window...")
