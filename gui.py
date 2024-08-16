import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import configparser
import os

config = configparser.ConfigParser()
config.read('config.ini')

def save_to_config():
    config['ROM']['path'] = entry_rom.get()
    config['OPTIONS']['filler_byte'] = filler_byte_var.get()
    selected_file = file_selector.get()
    if selected_file in config.sections():
        config[selected_file]['start_offset'] = entry_start.get()
        config[selected_file]['end_offset'] = entry_end.get()
        config[selected_file]['output_file'] = entry_output.get()
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
    update_file_selector()

def on_file_select(event):
    selected_file = file_selector.get()
    if selected_file in config.sections():
        entry_start.delete(0, tk.END)
        entry_start.insert(0, config[selected_file].get('start_offset', ''))
        entry_end.delete(0, tk.END)
        entry_end.insert(0, config[selected_file].get('end_offset', ''))
        entry_output.delete(0, tk.END)
        entry_output.insert(0, config[selected_file].get('output_file', ''))

def add_new_file():
    file_sections = [section for section in config.sections() if section.startswith('FILE')]
    if file_sections:
        last_file_num = max([int(f.replace('FILE', '')) for f in file_sections])
        new_file_name = f'FILE{last_file_num + 1}'
    else:
        new_file_name = 'FILE1'
    config.add_section(new_file_name)
    config[new_file_name]['start_offset'] = ''
    config[new_file_name]['end_offset'] = ''
    config[new_file_name]['output_file'] = ''
    save_to_config()

def delete_file():
    selected_file = file_selector.get()
    if selected_file in config.sections() and messagebox.askyesno("Delete File", f"Are you sure you want to delete {selected_file}?"):
        config.remove_section(selected_file)
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
        update_file_selector()

def update_file_selector():
    current_selection = file_selector.get()  # Store the current selection
    file_list = [section for section in config.sections() if section.startswith('FILE')]
    file_selector['values'] = file_list
    if current_selection in file_list:
        file_selector.set(current_selection)  # Set back the current selection if it's still in the list
    elif file_list:
        file_selector.set(file_list[0])  # Set the first file if the current selection is no longer valid
    else:
        file_selector.set('')
    file_selector.event_generate('<<ComboboxSelected>>')

def extract_data():
    save_to_config()  # Save the current configuration before extracting
    rom_path = config['ROM']['path']
    for FILE_section in config.sections():
        if FILE_section.startswith('FILE'):
            # Get the start and end offsets from the config
            start_offset_str = config[FILE_section]['start_offset']
            end_offset_str = config[FILE_section]['end_offset']

            # Ensure the offsets are interpreted as hexadecimal
            start_offset = int('0x' + start_offset_str, 16) if not start_offset_str.startswith('0x') else int(start_offset_str, 16)
            end_offset = int('0x' + end_offset_str, 16) if not end_offset_str.startswith('0x') else int(end_offset_str, 16)

            # Validate the offsets
            if start_offset > end_offset:
                print(f"Error: The start_offset ({start_offset_str}) is greater than the end_offset ({end_offset_str}) in section {FILE_section}. Skipping this section.")
                continue

            size = end_offset - start_offset + 1

            with open(rom_path, "rb") as f:
                f.seek(start_offset)
                data = f.read(size)
                output_file = config[FILE_section]['output_file']
                with open(output_file, "wb") as out_file:
                    out_file.write(data)
                print(f"Data extracted and saved to {output_file}")
    print("All FILE data extracted successfully.")

def patch_files():
    save_to_config()  # Save the current configuration before patching

    # Get the original ROM path from the config
    original_rom_path = config['ROM']['path']

    # Extract the file extension from the original ROM path
    file_extension = os.path.splitext(original_rom_path)[1]

    # Generate the new patched ROM path with the original extension
    patched_rom_path = os.path.splitext(original_rom_path)[0] + '_patched' + file_extension

    if not os.path.exists(patched_rom_path):
        with open(original_rom_path, "rb") as original_file, open(patched_rom_path, "wb") as patched_file:
            patched_file.write(original_file.read())

    truncate_enabled = config.getboolean('OPTIONS', 'truncate', fallback=False)
    filler_byte = bytes.fromhex(config.get('OPTIONS', 'filler_byte', fallback='00'))

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
                    # Calculate the number of bytes that will be truncated
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

root = tk.Tk()
root.title('Universal Data Extractor v1.0b')

# Set a minimum width for the window
root.minsize(width=468, height=180)  # You can adjust the width (468) as needed

tk.Label(root, text='ROM Path:').grid(row=0, column=0)
entry_rom = tk.Entry(root, width=50)  # Increased the width
entry_rom.grid(row=0, column=1)
entry_rom.insert(0, config['ROM'].get('path', ''))

file_selector = ttk.Combobox(root, state='readonly', width=47)  # Increased the width
file_selector.grid(row=1, column=1, padx=10)
file_selector.bind('<<ComboboxSelected>>', on_file_select)

tk.Label(root, text='Start Offset:').grid(row=2, column=0)
entry_start = tk.Entry(root, width=35)  # Increased the width
entry_start.grid(row=2, column=1)

tk.Label(root, text='End Offset:').grid(row=3, column=0)
entry_end = tk.Entry(root, width=35)  # Increased the width
entry_end.grid(row=3, column=1)

tk.Label(root, text='Output File:').grid(row=4, column=0)
entry_output = tk.Entry(root, width=35)  # Increased the width
entry_output.grid(row=4, column=1)

filler_byte_var = tk.StringVar(value=config.get('OPTIONS', 'filler_byte', fallback='00'))
tk.Checkbutton(root, text='Enable 0xFF filling byte', variable=filler_byte_var, onvalue='FF', offvalue='00').grid(row=6, columnspan=2)

truncate = tk.IntVar(value=config.getint('OPTIONS', 'truncate'))
tk.Checkbutton(root, text='Truncate before inject', variable=truncate).grid(row=7, columnspan=2)

button_frame = tk.Frame(root)
button_frame.grid(row=8, column=1, pady=2)

tk.Button(button_frame, text='Extract Files', command=extract_data).pack(side=tk.LEFT)
tk.Button(button_frame, text='Delete Line', command=delete_file).pack(side=tk.LEFT)
tk.Button(button_frame, text='Save Config', command=save_to_config).pack(side=tk.LEFT)
tk.Button(button_frame, text='Add New', command=add_new_file).pack(side=tk.LEFT)
tk.Button(button_frame, text='Patch Files', command=patch_files).pack(side=tk.LEFT)

update_file_selector()  # Initialize the file selector with the first file section

root.mainloop()