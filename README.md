# Pokemon-Stadium-Save-Sync
A tool created to solve one simple problem: Retroarch can only save to .srm, but will only accept .sav files for its TransferPak.
It compares the srm and sav files and replace whichever is older with whichever is newer. Use the UI file for easier setup.


Step 1: Backup all your savefiles!

Step 2: Create TransferPak subfolder somewhere within your RetroArch folder (default is "RetroArch/saves/TransferPak"). This is where the .sav files will be stored.

Step 3: Place Pokemon Stadium ROM file in the newly created folder.

Step 4: Run PokemonStadiumSyncUI.py to open the setup window.
 - Select the Pokemon game you want to connect to the RetroArch TransferPak.
 - Specify the path for the RetroArch folder if not detected automaticly.
 - Click the ⭯ to automaticly locate savefiles.
 - Specify the path for anything the program was unable to find.

Step 5: Save configuration and close the UI.


Now run PokemonStadiumSync.py. This will grab any available .srm files and create a .sav copy in the TransferPak folder.
The save game you chose to use with RetroArch will be renamed something like "Pokemon Stadium (USA).n64.sav" so RetroArch loads it properly. The script will also locate the appropriate Game Boy ROM and place a copy in the TransferPak folder called "Pokemon Stadium (USA).n64.gb" so RetroArch loads it properly.

Each time you run the script now it will delete either the .srm or the .sav version of a save (whichever is older) and recreate it from the newer save. You can also minimize the script to system tray and it will monitor and sync savefiles in the background to sync after RetroArch closes. Note that this can take up to 150 seconds from when you close RetroArch, but should take less then 30 seconds.