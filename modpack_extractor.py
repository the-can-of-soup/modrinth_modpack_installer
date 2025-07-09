# TODO: Ensure compatibility with older Python 3 versions
# TODO: Finish other TODOs below this point in the code

# Documentation used: https://support.modrinth.com/en/articles/8802351-modrinth-modpack-format-mrpack

from urllib.parse import urlparse
from zipfile import ZipFile
import requests
import datetime
import hashlib
import base64
import random
import json
import os

APPDATA_PATH: str = os.path.expandvars('%appdata%')
INSTALLATIONS_DIR: str = os.path.join(APPDATA_PATH, '.soup_mc_modrinth_packs')
VERSIONS_DIR: str = os.path.join(APPDATA_PATH, '.minecraft', 'versions')
LAUNCHER_PROFILES_FILE_PATH: str = os.path.join(APPDATA_PATH, '.minecraft', 'launcher_profiles.json')
FILENAME_UNSAFE_CHARACTERS: str = r'\/:*?"<>|'
STRICT_FILENAME_ALLOWED_CHARACTERS: str = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_-'
ALLOWED_HOSTNAMES: list[str] = ['cdn.modrinth.com', 'github.com', 'raw.githubusercontent.com', 'gitlab.com']
DEFAULT_PROFILE_ICON: str = 'data:image/png;base64,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'

DEPENDENCY_NAMES: dict[str, str] = {
    'minecraft': 'Minecraft',
    'forge': 'Forge',
    'neoforge': 'NeoForge',
    'fabric-loader': 'Fabric',
    'quilt-loader': 'Quilt'
}

class ModpackExtractorError(Exception):
    pass

class ModpackInstallerError(Exception):
    pass

def escape_filename(filename: str, strict: bool = False) -> str:
    escaped_filename: str = ''

    for character in filename:
        if character in FILENAME_UNSAFE_CHARACTERS:
            escaped_filename += '_'
        elif ord(character) < 32:
            escaped_filename += '_'
        elif strict:
            if character in STRICT_FILENAME_ALLOWED_CHARACTERS:
                escaped_filename += character.lower()
            else:
                escaped_filename += '_'
        else:
            escaped_filename += character

    return escaped_filename

def image_to_uri(image_data: bytes) -> str:
    encoded_data: str = base64.b64encode(image_data).decode()
    return f'data:image/png;base64,{encoded_data}'

def extract_modpack(filename: str, destination_folder: str = '.', is_server: bool = False, download_optional_files: bool = True, wait_for_user: bool = True, print_logs: bool = True) -> tuple[str, dict]:
    """
    Converts an .mrpack file into a .zip file.

    :param filename: The path to the .mrpack file.
    :type filename: str
    :param destination_folder: The folder to place the output .zip file into.
    :type destination_folder: str
    :param is_server: Whether the modpack is being extracted for a server.
    :type is_server: bool
    :param download_optional_files: Whether optional files should be downloaded.
    :type download_optional_files: bool
    :param wait_for_user: Whether to wait for user input before extracting.
    :type wait_for_user: bool
    :param print_logs: Whether to print logs while extracting.
    :type print_logs: bool
    :return: The path to the .zip file, and the contents of the modpack index file as a dict.
    :rtype: tuple[str, dict]
    """

    # Read mrpack file
    if print_logs:
        print('Reading mrpack file...')
    with ZipFile(filename, 'r') as zf:

        # Read index file
        data: bytes = zf.read('modrinth.index.json')
        data: dict = json.loads(data.decode())

        # Read overrides
        base_overrides: dict[str, bytes] = {}
        one_sided_overrides: dict[str, bytes] = {}
        for compressed_filename in zf.namelist():

            # Get override type
            override_type: str = 'none'
            if compressed_filename.startswith('overrides/'):
                override_type = 'base'
            elif compressed_filename.startswith('server-overrides/'):
                override_type = 'server'
            elif compressed_filename.startswith('client-overrides/'):
                override_type = 'client'

            # Read override
            filename_relative_to_instance: str = '/'.join(compressed_filename.split('/')[1:])
            if override_type == 'base':
                base_overrides[filename_relative_to_instance] = zf.read(compressed_filename)
            elif (override_type == 'server' and is_server) or (override_type == 'client' and not is_server):
                one_sided_overrides[filename_relative_to_instance] = zf.read(compressed_filename)

        # Merge overrides
        overrides: dict[str, bytes] = base_overrides | one_sided_overrides

    # Get metadata
    modpack_version: str = data['versionId']
    modpack_name: str = data['name']
    modpack_summary: str | None = data.get('summary')
    modpack_dependencies: dict[str, str] = data['dependencies']
    downloads_metadata: list[dict] = data['files']

    # Wait for user
    if wait_for_user:
        if print_logs:
            print('')
        print(f'Modpack name:    {modpack_name}')
        print(f'Modpack version: {modpack_version}')
        if modpack_summary is not None:
            print(f'Modpack summary: {modpack_summary.replace('\n', '\n                 ')}')
        print('Dependencies:')
        for dependency, dependency_version in modpack_dependencies.items():
            print(f'    {DEPENDENCY_NAMES.get(dependency, dependency)} {dependency_version}')
        print('')
        input('Press ENTER to continue.')
        if print_logs:
            print('')

    # Download files
    if print_logs:
        print('Downloading files...')
    downloaded_files: dict[str, bytes] = {}
    for download_metadata in downloads_metadata:

        # Get metadata
        filename_relative_to_instance: str = download_metadata['path']
        file_size: int = download_metadata['fileSize']
        hashes: dict = download_metadata['hashes']
        environment: dict = download_metadata.get('env', {'client': 'required', 'server': 'required'})
        download_urls: list[str] = download_metadata['downloads']

        # Check environment
        file_support: str = environment['server'] if is_server else environment['client']
        should_download: bool = False
        if (file_support == 'required') or (file_support == 'optional' and download_optional_files):
            should_download = True
        if not should_download:
            continue

        # Download file
        if print_logs:
            print(f'Downloading [{file_size / (1024 * 1024):.2f} MiB] {filename_relative_to_instance}')
        success: bool = False
        for download_url in download_urls:
            if print_logs:
                print(f'Using {download_url}')

            # Check hostname
            hostname: str = urlparse(download_url).hostname
            if hostname not in ALLOWED_HOSTNAMES:
                raise ModpackExtractorError(f'Invalid modpack file: Hostname "{hostname}" isn\'t on the whitelist!')

            # Download from URL
            try:
                r: requests.Response = requests.get(download_url)
            except Exception as e:
                if print_logs:
                    print(f'Error during download: {e}')
                continue
            file_data: bytes = r.content

            # Verify hashes
            sha1_hash: str = hashlib.sha1(file_data).hexdigest()
            sha512_hash: str = hashlib.sha512(file_data).hexdigest()
            if sha1_hash != hashes['sha1']:
                raise ModpackExtractorError('SHA1 hashes don\'t match!')
            if sha512_hash != hashes['sha512']:
                raise ModpackExtractorError('SHA512 hashes don\'t match!')

            # Save file
            downloaded_files[filename_relative_to_instance] = file_data
            success = True
            break

        # Check for success
        if not success:
            if len(download_urls) == 0:
                raise ModpackExtractorError('Invalid modpack file: No download URLs were provided!')
            raise ModpackExtractorError('All provided download URLs failed! Check your internet connection.')

    # Get output paths
    escaped_output_name: str = escape_filename(f'{modpack_name} - {modpack_version}')
    output_filename: str = os.path.join(destination_folder, escaped_output_name + '.zip')

    # Write output zip file
    if print_logs:
        print('Writing output zip file...')
    with ZipFile(output_filename, 'w') as zf:

        # Write downloaded files
        for compressed_filename, file_data in downloaded_files.items():
            zf.writestr(compressed_filename, file_data)

        # Write overrides
        for compressed_filename, file_data in overrides.items():
            zf.writestr(compressed_filename, file_data)

    # Show success message
    if print_logs:
        print(f'Successfully extracted to "{output_filename}"!')

    # Return info
    return output_filename, data

def install_modpack(extracted_modpack_filename: str, data: dict, wait_for_user: bool = True, print_logs: bool = True) -> None:
    """
    Creates an installation in the Minecraft Launcher from an extracted modpack.
    Prompts the user for the name of the Minecraft version to use.

    :param extracted_modpack_filename: The path to the .zip file containing the extracted modpack.
    :type extracted_modpack_filename: str
    :param data: The contents of the modpack index file as a dict.
    :type data: dict
    :param wait_for_user: Whether to ask user to confirm before installing if a duplicate installation is found.
    :type wait_for_user: bool
    :param print_logs: Whether to print logs while extracting.
    :type print_logs: bool
    :rtype: None
    """

    # Get installation path and name
    escaped_output_name: str = escape_filename(f'{data['name']}_{data['versionId']}', strict=True)
    install_path: str = os.path.join(INSTALLATIONS_DIR, escaped_output_name)
    profile_name: str = f'{data['name']} - {data['versionId']}'

    # Check for existing installation
    already_installed: bool = os.path.isdir(install_path)
    if already_installed and wait_for_user:
        if print_logs:
            print('')
        print('This modpack is already installed!')
        confirm: str = input('Are you sure you want to install it again? [y/n] ')
        if confirm.strip().lower() not in ('y', 'yes'):
            raise ModpackInstallerError('User cancelled installation.')
        if print_logs:
            print('')

    # Update path to avoid duplicates if already installed
    if already_installed:
        installation_number: int = 2
        while os.path.isdir(install_path):
            escaped_output_name = escape_filename(f'{data['name']}_{data['versionId']}_{installation_number}', strict=True)
            install_path = os.path.join(INSTALLATIONS_DIR, escaped_output_name)
        profile_name = f'{data['name']} - {data['versionId']} (#{installation_number})'

    # Get the icon URI
    if print_logs:
        print('Loading icon...')
    profile_icon: str = DEFAULT_PROFILE_ICON
    with ZipFile(extracted_modpack_filename, 'r') as zf:
        if 'icon.png' in zf.namelist():
            icon_data: bytes = zf.read('icon.png')
            profile_icon = image_to_uri(icon_data)

    # Show version selection instructions
    if print_logs:
        print('')
    print('Please ensure you have a Minecraft version installed that meets these requirements:')
    for dependency, dependency_version in data['dependencies'].items():
        print(f'    {DEPENDENCY_NAMES.get(dependency, dependency)} {dependency_version}')
    print('')
    input('Press ENTER once complete.')
    print('')

    # Get installation version from user
    profile_version: str
    while True:
        profile_version = input('Please enter the exact name of the version: ')

        if profile_version.strip() == '':
            raise ModpackInstallerError('User cancelled installation.')

        profile_version = profile_version.replace('/', '').replace('\\', '')
        if os.path.isabs(profile_version) or os.path.normpath(profile_version).startswith('..'):
            print('Invalid input.')
            print('If you wish to cancel, enter nothing.')
            print('')
            continue

        version_path: str = os.path.join(VERSIONS_DIR, profile_version)
        if os.path.isdir(version_path):
            break

        print('That version is not installed. Check your spelling.')
        print('If you wish to cancel, enter nothing.')
        print('')
    if print_logs:
        print('')

    # Create launcher profile
    profile_id: str = random.randbytes(16).hex()
    profile_timestamp: str = datetime.datetime.now(datetime.UTC).isoformat()
    profile: dict[str, str] = {
        'name': profile_name,
        'type': 'custom',
        'icon': profile_icon,
        'created': profile_timestamp,
        'lastUsed': profile_timestamp,
        'lastVersionId': profile_version,
        'gameDir': install_path
    }

    # Create installations directory if it doesn't exist
    if not os.path.isdir(INSTALLATIONS_DIR):
        os.mkdir(INSTALLATIONS_DIR)

    # Install modpack
    if print_logs:
        print('Installing...')
    with ZipFile(extracted_modpack_filename, 'r') as zf:
        zf.extractall(install_path)

    # Save launcher profile
    if print_logs:
        print('Creating launcher profile...')
    with open(LAUNCHER_PROFILES_FILE_PATH, 'r') as f:
        profiles: dict = json.loads(f.read())
    profiles['profiles'][profile_id] = profile
    with open(LAUNCHER_PROFILES_FILE_PATH, 'w') as f:
        f.write(json.dumps(profiles))

    # Show success message
    if print_logs:
        print(f'Successfully installed as "{profile_name}"!')

if __name__ == '__main__':
    # Testing
    filename, modpack_data = extract_modpack('modpacks/test.mrpack', 'extracted_modpacks')
    install_modpack(filename, modpack_data)
    input('')
