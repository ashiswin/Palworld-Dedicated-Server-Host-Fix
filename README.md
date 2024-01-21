# Palworld Dedicated Server Host Fix
## Usage

1. Connect to your dedicated server with your host account at least once to generate the sample save file we'll be using to fix the original save file.
2. Place the generated sample file, along with your original save file in the folder with the `fix_host_file.py` script.
3. Update the SAMPLE_FILENAME variable with your sample filename. (e.g. 51D4676E000000000000000000000000.sav)
4. Ensure `offzip.exe` is in the same directory as the script. (It should be by default)
5. Run `fix_host_file.py` and observe for errors
6. Copy the generated file (should be the same as SAMPLE_FILENAME) into your dedicated server saved files folder and replace the existing save
7. Profit!
