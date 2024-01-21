import zlib
import binascii
import subprocess
import os
from shutil import move, rmtree

INPUT_FILENAME = "00000000000000000000000000000001.sav"
SAMPLE_FILENAME = "51D4676E000000000000000000000000.sav"  # The file created when you first join your dedicated server
LEVEL_FILENAME = "Level.sav"

INPUT_EXTRACTION_DIR = INPUT_FILENAME.split(".")[0]
SAMPLE_EXTRACTION_DIR = SAMPLE_FILENAME.split(".")[0]
# Extract existing saves
try:
    os.mkdir(INPUT_EXTRACTION_DIR)
except FileExistsError:
    pass

try:
    os.mkdir(SAMPLE_EXTRACTION_DIR)
except FileExistsError:
    pass

subprocess.run(["offzip.exe", "-s", "-a", "-o", INPUT_FILENAME, INPUT_EXTRACTION_DIR])
subprocess.run(["offzip.exe", "-s", "-a", "-o", SAMPLE_FILENAME, SAMPLE_EXTRACTION_DIR])

level_data = bytearray(open(LEVEL_FILENAME, "rb").read())
level_data = zlib.decompress(level_data[12:])
level_data = zlib.decompress(level_data)
level_bytearray = bytearray(level_data)

PLAYER_UID_GUID_OFFSET = 0x6D2
INDIVIDUAL_ID_GUID_OFFSET = 0x774
INSTANCE_ID_GUID_OFFSET = 0x7C8
INSTANCE_ID_WRITE_OFFSET = 84
ORIGINAL_ID_BYTE_OFFSET = 12

STEAM_ID_LENGTH_BYTES = 4
INSTANCE_ID_LENGTH_BYTES = 16

steam_id = bytearray.fromhex(SAMPLE_EXTRACTION_DIR)[0:4]
steam_id.reverse()

print(steam_id)
original_data = open(f"{INPUT_FILENAME.split('.')[0]}/0000000c.gva", "rb").read()
sample_data = open(f"{SAMPLE_FILENAME.split('.')[0]}/0000000c.gva", "rb").read()

original_bytearray = bytearray(original_data)
sample_bytearray = bytearray(sample_data)

# Overwrite player ID GUID
original_bytearray[
    PLAYER_UID_GUID_OFFSET : PLAYER_UID_GUID_OFFSET + STEAM_ID_LENGTH_BYTES
] = steam_id
original_bytearray[
    INDIVIDUAL_ID_GUID_OFFSET : INDIVIDUAL_ID_GUID_OFFSET + STEAM_ID_LENGTH_BYTES
] = steam_id

print(
    f"Updated Player UID GUID {hex(PLAYER_UID_GUID_OFFSET)}:{hex(PLAYER_UID_GUID_OFFSET + STEAM_ID_LENGTH_BYTES)} from {binascii.hexlify(original_data[PLAYER_UID_GUID_OFFSET:PLAYER_UID_GUID_OFFSET + STEAM_ID_LENGTH_BYTES])} to {binascii.hexlify(original_bytearray[PLAYER_UID_GUID_OFFSET:PLAYER_UID_GUID_OFFSET + STEAM_ID_LENGTH_BYTES])}"
)
print(
    f"Updated Individual ID GUID from {hex(INDIVIDUAL_ID_GUID_OFFSET)}:{hex(INDIVIDUAL_ID_GUID_OFFSET + STEAM_ID_LENGTH_BYTES)} from {binascii.hexlify(original_data[INDIVIDUAL_ID_GUID_OFFSET:INDIVIDUAL_ID_GUID_OFFSET + STEAM_ID_LENGTH_BYTES])} to {binascii.hexlify(original_bytearray[INDIVIDUAL_ID_GUID_OFFSET:INDIVIDUAL_ID_GUID_OFFSET + STEAM_ID_LENGTH_BYTES])}"
)

# Remove "01" byte from the "0000...0001.sav" ID
original_bytearray[PLAYER_UID_GUID_OFFSET + ORIGINAL_ID_BYTE_OFFSET] = 0
original_bytearray[INDIVIDUAL_ID_GUID_OFFSET + ORIGINAL_ID_BYTE_OFFSET] = 0
print(
    f"Reset 1 byte at {hex(PLAYER_UID_GUID_OFFSET + ORIGINAL_ID_BYTE_OFFSET)} from {original_data[PLAYER_UID_GUID_OFFSET + ORIGINAL_ID_BYTE_OFFSET]} to {original_bytearray[PLAYER_UID_GUID_OFFSET + ORIGINAL_ID_BYTE_OFFSET]}"
)
print(
    f"Reset 1 byte at {hex(INDIVIDUAL_ID_GUID_OFFSET + ORIGINAL_ID_BYTE_OFFSET)} from {original_data[INDIVIDUAL_ID_GUID_OFFSET + ORIGINAL_ID_BYTE_OFFSET]} to {original_bytearray[INDIVIDUAL_ID_GUID_OFFSET + ORIGINAL_ID_BYTE_OFFSET]}"
)

# Overwrite GUID in leve's instance ID for inventory
instance_id = original_bytearray[
    INSTANCE_ID_GUID_OFFSET : INSTANCE_ID_GUID_OFFSET + INSTANCE_ID_LENGTH_BYTES
]
level_data_instance_id_offset = level_data.find(instance_id)
level_bytearray[
    level_data_instance_id_offset
    - INSTANCE_ID_WRITE_OFFSET : level_data_instance_id_offset
    - INSTANCE_ID_WRITE_OFFSET
    + STEAM_ID_LENGTH_BYTES
] = steam_id
level_bytearray[
    level_data_instance_id_offset - INSTANCE_ID_WRITE_OFFSET + ORIGINAL_ID_BYTE_OFFSET
] = 0
print(
    f"Updated Instance ID GUID {hex(level_data_instance_id_offset - INSTANCE_ID_WRITE_OFFSET)}:{hex(level_data_instance_id_offset - INSTANCE_ID_WRITE_OFFSET + STEAM_ID_LENGTH_BYTES)} from {binascii.hexlify(level_data[level_data_instance_id_offset - INSTANCE_ID_WRITE_OFFSET : level_data_instance_id_offset - INSTANCE_ID_WRITE_OFFSET + STEAM_ID_LENGTH_BYTES])} to {binascii.hexlify(level_bytearray[level_data_instance_id_offset - INSTANCE_ID_WRITE_OFFSET : level_data_instance_id_offset - INSTANCE_ID_WRITE_OFFSET + STEAM_ID_LENGTH_BYTES])}"
)

compressed_level_data = zlib.compress(level_bytearray)
uncompressed_level_len = len(level_data)
compressed_level_len = len(compressed_level_data)
compressed_level_data = zlib.compress(compressed_level_data)

move(LEVEL_FILENAME, f"{LEVEL_FILENAME}.old")

f = open(LEVEL_FILENAME, "wb")
f.write(uncompressed_level_len.to_bytes(4, byteorder="little"))
f.write(compressed_level_len.to_bytes(4, byteorder="little"))
f.write(b"PlZ")
f.write(bytes([0x32]))
f.write(compressed_level_data)

compressed_data = zlib.compress(original_bytearray)
uncompressed_len = len(original_data)
compressed_len = len(compressed_data)

move(SAMPLE_FILENAME, f"{SAMPLE_FILENAME}.old")

f = open(SAMPLE_FILENAME, "wb")
f.write(uncompressed_len.to_bytes(4, byteorder="little"))
f.write(compressed_len.to_bytes(4, byteorder="little"))
f.write(b"PlZ")
f.write(bytes([0x31]))
f.write(compressed_data)

print("Cleaning up...")
rmtree(INPUT_EXTRACTION_DIR)
rmtree(SAMPLE_EXTRACTION_DIR)

print(
    f"Successfully processed {INPUT_FILENAME} and wrote to {SAMPLE_FILENAME}\n\t{SAMPLE_FILENAME}.old contains the original save file from your dedicated server"
)
