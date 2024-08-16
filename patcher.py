import configparser
import os

# Create a ConfigParser object
config = configparser.ConfigParser()

# Read the configuration file
config.read('config.ini')

# Get the original ROM path from the config
original_rom_path = config['ROM']['path']

# Extract the file extension from the original ROM path
file_extension = os.path.splitext(original_rom_path)[1]

# Generate the new patched ROM path with the original extension
patched_rom_path = os.path.splitext(original_rom_path)[0] + '_patched' + file_extension

# Check if the patched ROM file exists, create it if not
if not os.path.exists(patched_rom_path):
    # Create a new file by copying the original ROM
    with open(original_rom_path, "rb") as original_file, open(patched_rom_path, "wb") as patched_file:
        patched_file.write(original_file.read())

# Check if truncation is enabled in the config
truncate_enabled = config.getboolean('OPTIONS', 'truncate', fallback=False)
filler_byte = bytes.fromhex(config.get('PATCH_OPTIONS', 'filler_byte', fallback='00'))

# Loop through each FILE section
for FILE_section in config.sections():
    if FILE_section.startswith('FILE'):
        # Calculate the size to read based on start and end offsets
        start_offset = int(config[FILE_section]['start_offset'], 16)
        end_offset = int(config[FILE_section]['end_offset'], 16)
        original_size = end_offset - start_offset + 1
        
        # Read the modified data from the corresponding output file
        modified_data_file = config[FILE_section]['output_file']
        with open(modified_data_file, "rb") as data_file:
            modified_data = data_file.read()
        
        # Check if the modified data is larger than the original size
        if len(modified_data) > original_size:
            if truncate_enabled:
                # Calculate the truncated size
                truncated_size = len(modified_data) - original_size
                # Truncate the modified data to fit the original size
                modified_data = modified_data[:original_size]
                print(f"Warning: Data from {modified_data_file} is larger than the original by {truncated_size} bytes. It has been truncated to fit the allowed size.")
            else:
                # Inform the user that the patch is too large
                excess_size = len(modified_data) - original_size
                print(f"Error: Data from {modified_data_file} is larger than the original by {excess_size} bytes. Truncation is disabled.")
                continue
        # Check if the modified data is smaller than the original size
        elif len(modified_data) < original_size:
            filler_size = original_size - len(modified_data)
            modified_data += filler_byte * filler_size
            print(f"Info: Data from {modified_data_file} is smaller than the original. It has been filled with {filler_byte.hex().upper()} for {filler_size} bytes.")

        # Open the patched ROM file in binary read-write mode
        with open(patched_rom_path, "r+b") as f:
            # Seek to the starting offset
            f.seek(start_offset)
            
            # Write the modified data back to the patched ROM file
            f.write(modified_data)
        
        print(f"Data from {modified_data_file} injected at offset {start_offset:X} into {patched_rom_path}")

print("All FILEs patched successfully.")
