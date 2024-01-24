import argparse
import zlib
import binascii
import os.path
from shutil import move, rmtree

parser = argparse.ArgumentParser(
    description="Palworld dedicated server host save fixer"
)
parser.add_argument(
    "saves_location",
    type=str,
    help="the directory your server saves are stored (e.g.: PalServer\\Pal\\Saved\\SaveGames\\0\\3DAB7FAF44A6A0E6576B0EA3C84F24A8",
)
parser.add_argument(
    "dst_filename",
    type=str,
    help="the name of the save file to overwrite (this will be the newly generated save, NOT 00000000000000000000000000000001.sav)",
)
parser.add_argument(
    "src_filename",
    type=str,
    default="00000000000000000000000000000001.sav",
    help="the name of the save file to pull from (this will default to 00000000000000000000000000000001.sav if not set)",
)
args = parser.parse_args()

if not os.path.isfile(f"{args.saves_location}/Level.sav"):
    print("Invalid server location provided")
    parser.print_help()
    exit(-1)

if not os.path.isfile(f"{args.saves_location}/Players/{args.dst_filename}"):
    print(
        "Invalid generated player save file provided. This should be the newly generated player save file with your steam ID on it."
    )
    parser.print_help()
    exit(-1)


if not os.path.isfile(
    f"{args.saves_location}/Players/{args.src_filename}"
):
    print(
        f"Unable to find source save file ({args.src_filename}). Please ensure it exists."
    )
    parser.print_help()
    exit(-1)

SRC_FILENAME = f"{args.saves_location}/Players/{args.src_filename}"
DST_FILENAME = f"{args.saves_location}/Players/{args.dst_filename}"  # The file created when you first join your dedicated server
LEVEL_FILENAME = f"{args.saves_location}/Level.sav"

original_data = bytearray(open(SRC_FILENAME, "rb").read())
original_data = zlib.decompress(original_data[12:])
original_bytearray = bytearray(original_data)

sample_data = bytearray(open(DST_FILENAME, "rb").read())
sample_data = zlib.decompress(sample_data[12:])
sample_bytearray = bytearray(sample_data)

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

steam_id = bytearray.fromhex(args.dst_filename.split(".")[0])[0:4]
steam_id.reverse()

print(f"Fixing save file for player {steam_id}")

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

# Compress and write level save file
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

# Compress and write player save file
compressed_data = zlib.compress(original_bytearray)
uncompressed_len = len(original_data)
compressed_len = len(compressed_data)

move(DST_FILENAME, f"{DST_FILENAME}.old")

f = open(DST_FILENAME, "wb")
f.write(uncompressed_len.to_bytes(4, byteorder="little"))
f.write(compressed_len.to_bytes(4, byteorder="little"))
f.write(b"PlZ")
f.write(bytes([0x31]))
f.write(compressed_data)

print(
    f"Successfully processed {SRC_FILENAME} and wrote to {DST_FILENAME}\n\t{DST_FILENAME}.old contains the original save file from your dedicated server"
)
