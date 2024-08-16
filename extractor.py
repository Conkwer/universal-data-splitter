import configparser

# Create a ConfigParser object
config = configparser.ConfigParser()

# Read the configuration file
config.read('config.ini')

# Get the ROM path from the config
rom_path = config['ROM']['path']

# Loop through each FILE section
for FILE_section in config.sections():
    if FILE_section.startswith('FILE'):
        # Calculate the size to read based on start and end offsets
        start_offset = int(config[FILE_section]['start_offset'], 16)
        end_offset = int(config[FILE_section]['end_offset'], 16)
        size = end_offset - start_offset + 1
        
        # Open the ROM file in binary read mode
        with open(rom_path, "rb") as f:
            # Seek to the starting offset
            f.seek(start_offset)
            
            # Read the data from the starting offset to the ending offset
            data = f.read(size)
            
            # Write the data to the output file
            output_file = config[FILE_section]['output_file']
            with open(output_file, "wb") as out_file:
                out_file.write(data)
        
        print(f"Data extracted and saved to {output_file}")

# Inform the user that all FILEs have been extracted
print("All FILE data extracted successfully.")