# Palworld Dedicated Server Host Fix
## Usage

> :warning: **ALWAYS MAKE A BACKUP**: Always make a backup of any and all save fils you're modifying lest you lose all your progress. I can't guarantee that this won't mess with your saveful in some nefarious way, but from my own extensive testing, we've not run into any issues.

> ⚠️ Your character's guild doesn't currently get transferred over. If you're a guild leader, transfer the ownership to someone else before fixing the save; rejoin the guild once on the new server. If you're a guild member, just rejoin the guild.

1. Connect to your dedicated server with your host account at least once to generate the sample save file we'll be using to fix the original save file.
2. Place the following files in the folder with the `fix_host_file.py` script.
    * Newly generated player save file (PalServer/Pal/Saved/SaveGames/0/<World ID>/Players/<Your Steam ID>.sav)
    * Original player save file (PalServer/Pal/Saved/SaveGames/0/<World ID>/Players/00000000000000000000000000000001.sav)
    * Level save file (PalServer/Pal/Saved/SaveGames/0/<World ID>/Level.sav)
3. Update the SAMPLE_FILENAME variable with your newly generated player save file. (e.g. 51D4676E000000000000000000000000.sav)
4. Run `fix_host_file.py` and observe for errors
5. Copy the generated file (should be the same as SAMPLE_FILENAME) into your dedicated server saved files folder and replace the existing save
6. Profit!
