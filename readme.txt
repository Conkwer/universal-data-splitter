The program extracts data at a specified offset.

Note: info.txt is written for an older version.

Optionally, there is an interface (gui.exe). You can write the desired offsets for multiple files in config.ini.

For example, in the file: "1ST_READ.BIN" the font at the address: from c040 to c3b0 (just for example, there is no font and the data is random).

In config.ini we write:

[FILE1]
start_offset = 0xc040
end_offset = 0xc3b0
output_file = extracted-area-01.bin

The start offset, end offset, and the name of the file where it will be saved.
For example, this can also be used to extract music from Dreamcast in individual cases. Write the start of the yadpcm file, skip the header, specify the end of the file and the extension.

You can do this for several files. For example, if there are multiple fonts, then write:

[FILE1]
start_offset = c040
end_offset = c3b0
output_file = extracted-area-01.bin

[FILE2]
start_offset = c051
end_offset = c3bf
output_file = extracted-area-02.bin

Something like that.

The Truncated option for patcher.exe, prevents going beyond the specified range. The program checks the size of the new file and when we insert and accidentally made it larger, it will cut the tail.

For PCM or ADPCM sound, it is not critical if it cuts off extra.

The filler_byte = 00 option is like truncate in reverse, if the file is smaller, it fills the rest with zeros or FF (your choice). By default, the fill byte is '00', but if a specific game bugs out because of this, we use FF.

------------------------
Using gui.exe:

The same as in the config. This program simply edits the config.
However, it immediately has a "extract files" button, so it replaces both extractor.exe and patcher.exe.

Run the program, specify the offsets. You can add new files, you can delete old ones. Save the config and press the extract button, it will extract the specified files.

You can also use extractor.exe, the same thing. The main thing is to save the desired offsets and file names in the config.

Reinsert using patcher.exe.

------------------------

Conkwer, 2024