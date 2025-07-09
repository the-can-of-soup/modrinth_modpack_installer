# IMPORTS

from typing import Optional, Callable
import subprocess
import traceback
import sys
import os

try:
    import modpack_installer
except OSError as error:
    print(error)
    print('')
    input('Press ENTER to close.')
except ModuleNotFoundError:
    print('Either PIL or requests is not installed!')
    input('Press ENTER to install them automatically.')
    print('')
    result: subprocess.CompletedProcess = subprocess.run([sys.executable, '-m', 'pip', 'install', 'pillow', 'requests'])
    print('')
    if result.returncode == 0:
        input('Success! Press ENTER to start the program.')
        try:
            import modpack_installer
        except ModuleNotFoundError:
            print('Something went wrong.')
            input('Press ENTER to close.')
            exit()
    else:
        print('Something went wrong.')
        input('Press ENTER to close.')
        exit()



# CONSTANTS

MODPACKS_DIR: str = 'modpacks'
EXTRACTED_MODPACKS_DIR: str = 'extracted_modpacks'
EXTRACTED_SERVER_PACKS_DIR: str = 'extracted_server_modpacks'



# DEFINITIONS

def print_title() -> None:
    os.system('cls')
    print('SOUP\'S MODRINTH MODPACK INSTALLER')
    print('----------------------------------')
    print('')

def select_file(directory: str, file_extension: Optional[str] = None) -> Optional[str]:
    """
    Asks the user to choose a file from a directory.

    :param directory: The directory to choose a file from.
    :type directory: str
    :param file_extension: The extension the selected file should have, or None.
    :type file_extension: Optional[str]
    :return: The path to the selected file, or None if no file was chosen.
    :rtype: Optional[str]
    """

    # Get options to choose from
    filenames: list[str] = os.listdir(directory)
    options: list[str] = []
    for filename in filenames:
        path: str = os.path.join(directory, filename)
        if os.path.isfile(path):
            if file_extension is None:
                options.append(filename)
                continue
            if filename.lower().endswith(f'.{file_extension.lower()}'):
                options.append(filename)

    # Print options
    if len(options) == 0:
        print('No files available!')
        if file_extension is not None:
            print(f'Please add a .{file_extension} file to the "{directory}" folder.')
        else:
            print(f'Please add a file to the "{directory}" folder.')
        print('')
        input('Press ENTER to continue.')
        return None
    print('Available files:')
    for i, option in enumerate(options):
        print(f'    [{i}] {option}')
    print('')

    # Ask for user's choice
    choice_str: str = input('Choose a file: ').strip()

    # Validate choice
    choice_valid: bool = True
    try:
        choice_index: int = int(choice_str)
    except ValueError:
        choice_valid = False
    else:
        if not (0 <= choice_index < len(options)):
            choice_valid = False
    if not choice_valid:
        print('Invalid input!')
        print('')
        input('Press ENTER to continue.')
        return None

    # Return choice
    # noinspection PyUnboundLocalVariable
    filename: str = options[choice_index]
    path: str = os.path.join(directory, filename)
    return path

def catch_errors(function: Callable, *args) -> bool:
    # noinspection PyBroadException,PyShadowingNames
    try:
        function(*args)
    except modpack_installer.ModpackExtractorError as error:
        print('')
        print(f'MODPACK EXTRACTOR ERROR: {error}')
    except modpack_installer.ModpackInstallerError as error:
        print('')
        print(f'MODPACK INSTALLER ERROR: {error}')
    except:
        print('')
        print('AN ERROR OCCURRED')
        print('=' * 40)
        traceback.print_exc()
        print('=' * 40)
    else:
        return True # Success
    return False # Error

def install(filename: str, do_optional: bool) -> None:
    extracted_filename: str
    modpack_data: dict
    extracted_filename, modpack_data = modpack_installer.extract_modpack(filename, EXTRACTED_MODPACKS_DIR, is_server=False, download_optional_files=do_optional)
    modpack_installer.install_modpack(extracted_filename, modpack_data)

def extract(filename: str, is_server: bool, do_optional: bool) -> None:
    directory: str = EXTRACTED_MODPACKS_DIR
    if is_server:
        directory = EXTRACTED_SERVER_PACKS_DIR
    modpack_installer.extract_modpack(filename, directory, is_server=is_server, download_optional_files=do_optional)



# MAIN

def main() -> None:
    # Create folders
    if not os.path.isdir(MODPACKS_DIR):
        os.mkdir(MODPACKS_DIR)
    if not os.path.isdir(EXTRACTED_MODPACKS_DIR):
        os.mkdir(EXTRACTED_MODPACKS_DIR)
    if not os.path.isdir(EXTRACTED_SERVER_PACKS_DIR):
        os.mkdir(EXTRACTED_SERVER_PACKS_DIR)

    # Mainloop
    while True:
        print_title()
        print('Available actions:')
        print('    [I] Install Modpack')
        print('    [E] Extract Modpack (Convert to ZIP)')
        print('    [M] Modpack Info')
        print('    [Q] Quit')
        print('')
        action: str = input('Choose an action: ').strip().lower()

        print_title()

        # Install Modpack
        if action == 'i':
            # Select modpack file
            filename: Optional[str] = select_file(MODPACKS_DIR, 'mrpack')
            if filename is None:
                continue
            print_title()

            # Ask about optional files
            do_optional: bool = input('Should optional files be downloaded? Default: yes. [y/n] ').strip().lower() not in ('n', 'no')

            # Extract and install modpack
            catch_errors(install, filename, do_optional)

            # Finish
            print('')
            input('Press ENTER to finish.')

        # Extract Modpack (Convert to ZIP)
        elif action == 'e':
            # Select modpack file
            filename: Optional[str] = select_file(MODPACKS_DIR, 'mrpack')
            if filename is None:
                continue
            print_title()

            # Ask for settings
            is_server: bool = input('Is this modpack being extracted for a server? Default: no. [y/n] ').strip().lower() in ('y', 'yes')
            do_optional: bool = input('Should optional files be downloaded? Default: yes. [y/n] ').strip().lower() not in ('n', 'no')

            # Extract modpack
            catch_errors(extract, filename, is_server, do_optional)

            # Finish
            print('')
            input('Press ENTER to finish.')

        # Modpack Info
        elif action == 'm':
            # Select modpack file
            filename: Optional[str] = select_file(MODPACKS_DIR, 'mrpack')
            if filename is None:
                continue
            print_title()

            # Print modpack info
            catch_errors(modpack_installer.print_modpack_info, filename)

            # Finish
            print('')
            input('Press ENTER to finish.')

        # Quit
        elif action == 'q':
            print('Goodbye')
            break

        # Invalid Action
        else:
            print('Invalid action!')
            print('')
            input('Press ENTER to continue.')

if __name__ == '__main__':
    main()
