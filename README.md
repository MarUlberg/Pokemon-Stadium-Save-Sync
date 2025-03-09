# Pokemon-Stadium-Save-Sync
A tool created to solve one simple problem: Retroarch can only save to .srm, but will only accept .sav files for its TransferPak.
It compairs the srm and sav files and replace whichever is older with whichever is newer. Use the UI file for easier setup.


Step 1: Backup all your savefiles!

Step 2: Create TransferPak subfolder somewhere within your RetroArch folder (default is "RetroArch/saves/TransferPak"). This is where the .sav files will be stored.

Step 3: Place Pokemon Stadium ROM file in the newly created folder, along with the desired Game Boy ROM.

Step 4: Rename the Game Buy ROM to the same as the Stadium ROM (Pokemon Stadium (USA).n64.gb)

Step 5: Run PokemonStadiumSyncUI.py to open the setup window.
 - Select the Pokemon game you want to connect to the RetroArch TransferPak.
 - Specify the path for the RetroArch folder.
 - Specify the subfolder where Game Boy .srm savefiles are stored.
 - Specify the subfolder where Game Boy Advance .srm savefiles are stored.
 - Specify the subfolder where Pokemon Stadium ROMs are stored.
 - Specify filename of Pokemon Stadium ROMs (with extension).
 - Specify filenames of each GameBoy ROM (without extension).

Step 6: Save configuration and close the UI.


Now run PokemonStadiumSync.py. This will grab any available .srm files and create a .sav copy in the TransferPak folder.
The save game you chose to use with RetroArch will be renamed something like "Pokemon Stadium (USA).n64.sav" so RetroArch loads it properly.
Each time you run the script now it will delete either the .srm or the .sav version of a save (whichever is older) and recreate it from the newer save.
If you are using something like Launchbox, its a good idea to add the script to Pokemon Stadium as an "additional app" and check the boxes to run in before and after the game opens/close.
