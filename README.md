# Palworld Dedicated Server Host Fix
## Usage

> :warning: **ALWAYS MAKE A BACKUP**: Always make a backup of any and all save fils you're modifying lest you lose all your progress. I can't guarantee that this won't mess with your saveful in some nefarious way, but from my own extensive testing, we've not run into any issues.

> ⚠️ Your character's guild doesn't currently get transferred over. If you're a guild leader, transfer the ownership to someone else before fixing the save; rejoin the guild once on the new server. If you're a guild member, just rejoin the guild.

1. Copy your local save files over to your dedicated server
    * Local save files should be stored in `C:\Users\<Your Windows User>\AppData\Local\Pal\Saved\SaveGames\<Your Steam ID>\<World ID>`. Copy the ENTIRE <World ID> folder over to your dedicated server.
    * Paste it in `<PalServer Install Directory>/PalServer/Pal/Saved/SaveGames/0/`
2. Launch your dedicated server and connect to it with your local client
    * You should be presented with a character creation screen. Go ahead and create a new character, we need it to patch the host file later.
    * Check that there's a new player save file generated in `<PalServer Install Directory>/PalServer/Pal/Saved/SaveGames/0/<World ID>/Players`. That's the file you need for step 5.
3. Shut down the dedicated server
4. Clone this repository anywhere in your dedicated server, or just download `fix_host_file.py`
5. Run `fix_host_file.py` in the following manner: `python fix_host_file.py "<PalServer Install Directory>/PalServer/Pal/Saved/SaveGames/0/<World ID>" <Newly generated filename from step 2>`
    * Example usage (Windows): `py fix_host_file.py "C:\Program Files (x86)\Steam\steamapps\common\PalServer\Pal\Saved\SaveGames\0\3DAB7FAF44A6A0E6576B0EA3C84F24A8" 51D4676E000000000000000000000000.sav`
    * Example usage (Linux): `python fix_host_file.py "~/Steam/steamapps/common/PalServer/Pal/Saved/SaveGames/0/3DAB7FAF44A6A0E6576B0EA3C84F24A8" 51D4676E000000000000000000000000.sav`
    * You can run `python fix_host_file.py -h` for a list of explanations for the parmeters
6. Launch your dedicated server again and try connecting. You should be connected as your character, with all information transferred except your guild affiliation.

## Troubleshooting

### I'm getting an infinite loading screen
This usually happens when you're not using the right Level.sav or save files. Try re-copying your local save files to the dedicated server and following the steps above again.
