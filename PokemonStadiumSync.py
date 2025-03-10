import os
import shutil
import configparser

# Load configuration
config = configparser.ConfigParser()
config.optionxform = str
config.read('PokemonStadiumSync.cfg')

stay_open = config.getboolean('General', 'stay_open')
RetroarchTransferPak1 = config.get('Ports', 'RetroarchTransferPak1')
RetroarchTransferPak2 = config.get('Ports', 'RetroarchTransferPak2')

base_dir = config.get('Directories', 'base_dir')
gb_dir = os.path.join(base_dir, config.get('Directories', 'gb_subdir'))
gba_dir = os.path.join(base_dir, config.get('Directories', 'gba_subdir'))
sav_dir = os.path.join(base_dir, config.get('Directories', 'sav_subdir'))
gbrom_dir = os.path.join(base_dir, config.get('Directories', 'gbrom_subdir'))

n64_roms = dict(config.items('StadiumROMs'))
gb_slots = dict(config.items('GBSlots'))
gba_slots = dict(config.items('GBASlots'))

slot_numbers = {"Green": 1, "Red": 2, "Blue": 3, "Yellow": 4, "Gold": 5, "Silver": 6, "Crystal": 7}

# Function Definitions
def get_last_modified_time(file_path):
    return os.path.getmtime(file_path) if os.path.exists(file_path) else None

def delete_and_replace(slot, srm, sav):
    if not srm or not sav:
        print(f"{slot}: Invalid file paths. Check your config.")
        return

    if not os.path.exists(srm):
        print(f"{slot}: .srm file does not exist.")
        return

    if not os.path.exists(sav):
        print(f"{slot}: .sav file missing. Creating from .srm...")
        shutil.copy2(srm, sav)
        return

    srm_time = get_last_modified_time(srm)
    sav_time = get_last_modified_time(sav)

    if srm_time > sav_time:
        print(f"{slot}: .sav is older. Replacing it with .srm.")
        os.remove(sav)
        shutil.copy2(srm, sav)
    else:
        print(f"{slot}: .srm is older. Replacing it with .sav.")
        os.remove(srm)
        shutil.copy2(sav, srm)

# Run synchronization for GB slots
for game_name, srm_filename in gb_slots.items():
    slot_number = slot_numbers.get(game_name, 'X')
    srm_path = os.path.join(gb_dir, srm_filename)
    sav_filename = f"PkmnTransferPak{slot_numbers[game_name]} {game_name}.sav"

    if game_name == RetroarchTransferPak1:
        sav_filename = n64_roms["Stadium 1"] + ".sav"
    elif game_name == RetroarchTransferPak2:
        sav_filename = n64_roms["Stadium 2"] + ".sav"
    else:
        sav_filename = sav_filename

    sav_path = os.path.join(sav_dir, sav_filename)
    delete_and_replace(game_name, srm=os.path.join(gb_dir, gb_slots[game_name]), sav=sav_path)

# Run synchronization for GBA slots
for gba_slot, srm_filename in gba_slots.items():
    srm_path = os.path.join(gba_dir, srm_filename)
    sav_filename = srm_filename.replace(".srm", "-2.sav")
    sav_path = os.path.join(sav_dir, sav_filename)
    delete_and_replace(gba_slot, srm_path, sav_path)
    
# Check and restore missing .gb files
def restore_gb_files():
    for key, rom in n64_roms.items():
        if not rom.strip():
            continue

        gb_file = os.path.join(sav_dir, rom + ".gb")  # Expected location
        gb_file = os.path.normpath(gb_file).replace("\\", "/")  # Normalize path

        # Determine the corresponding Game Boy ROM based on RetroarchTransferPak
        if key == "Stadium 1":
            gb_rom_name = gb_slots.get(RetroarchTransferPak1)
        elif key == "Stadium 2":
            gb_rom_name = gb_slots.get(RetroarchTransferPak2)
        else:
            gb_rom_name = None

        if gb_rom_name:
            gb_rom_name = gb_rom_name.replace(".srm", ".gb")  # Convert .srm to .gb
            gbrom_path = os.path.join(gbrom_dir, gb_rom_name)  # Locate in gbrom_dir
            gbrom_path = os.path.normpath(gbrom_path).replace("\\", "/")  # Normalize path

            if not os.path.exists(gb_file):
                print(f"Creating {rom}.gb from {gbrom_path}")

                if os.path.exists(gbrom_path):
                    try:
                        shutil.copy2(gbrom_path, gb_file)
                    except Exception as e:
                        print(f"Error fetching {rom}.gb: {e}")
                else:
                    print(f"Error: {gbrom_path} does not exist.")

# Call the function to restore missing .gb files
restore_gb_files()

if stay_open:
    input("Press Enter to close the window...")
