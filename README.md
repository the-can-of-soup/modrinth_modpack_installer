# Soup's Modrinth Modpack Installer

A Python program to convert Modrinth pack files (`*.mrpack`) into playable Minecraft instances.

## How To Use

1. Run `main.py` once to ensure all dependencies are installed and folders are created.
2. Move your `*.mrpack` file into the `modpacks` folder.
3. Run `main.py` to run the program.

## Modes

| Mode            | Description                                                                                                                                                                                                                                                                                                                                     |
|-----------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Install Modpack | Installs a Modrinth modpack file (`*.mrpack`) and creates a profile in the Minecraft Launcher. You will need to follow the instructions to install the correct loader version manually.<br/>**WARNING: Only install modpacks from sources you trust!**                                                                                          |
| Extract Modpack | Converts a Modrinth pack file (`*.mrpack`) into a `*.zip` file by downloading all necessary resources and combining them. This file can then be manually extracted and used as the game directory. After running the program, the output file can be found in either the `extracted_modpacks` folder or the `extracted_server_modpacks` folder. |
| Modpack Info    | Shows the name, version, summary, and dependencies of a Modrinth modpack file.                                                                                                                                                                                                                                                                  |
