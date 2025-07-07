# Documentation used: https://support.modrinth.com/en/articles/8802351-modrinth-modpack-format-mrpack

from urllib.parse import urlparse
from zipfile import ZipFile
import requests
import hashlib
import json
import os

FILENAME_UNSAFE_CHARACTERS: str = r'\/:*?"<>|'
ALLOWED_HOSTNAMES: list[str] = ['cdn.modrinth.com', 'github.com', 'raw.githubusercontent.com', 'gitlab.com']
DEPENDENCY_NAMES: dict[str, str] = {
    'minecraft': 'Minecraft',
    'forge': 'Forge',
    'neoforge': 'NeoForge',
    'fabric-loader': 'Fabric',
    'quilt-loader': 'Quilt'
}

class ModpackExtractorError(Exception):
    pass

def escape_filename(filename: str) -> str:
    escaped_filename: str = ''

    for character in filename:
        if character in FILENAME_UNSAFE_CHARACTERS:
            escaped_filename += '_'
        elif ord(character) < 32:
            escaped_filename += '_'
        else:
            escaped_filename += character

    return escaped_filename

def extract_modpack(filename: str, destination_folder: str = '.', is_server: bool = False, download_optional_files: bool = True, wait_for_user: bool = True, print_logs: bool = True) -> None:

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
            print(f'    {DEPENDENCY_NAMES[dependency]} {dependency_version}')
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
    output_path: str = os.path.join(destination_folder, escape_filename(modpack_name + ' - ' + modpack_version))
    compressed_output_filename: str = output_path + ' (Compressed).zip'
    if os.path.isdir(output_path):
        raise ModpackExtractorError(f'The folder "{output_path}" already exists! Please remove it first.')

    # Write output zip file
    if print_logs:
        print('Writing output zip file...')
    with ZipFile(compressed_output_filename, 'w') as zf:

        # Write downloaded files
        for compressed_filename, file_data in downloaded_files.items():
            zf.writestr(compressed_filename, file_data)

        # Write overrides
        for compressed_filename, file_data in overrides.items():
            zf.writestr(compressed_filename, file_data)

    # Extract output zip file
    if print_logs:
        print('Extracting output zip file...')
    with ZipFile(compressed_output_filename, 'r') as zf:
        zf.extractall(output_path)

    # Show success message
    if print_logs:
        print(f'Successfully extracted to "{output_path}"!')

if __name__ == '__main__':
    # Testing
    extract_modpack('modpacks/test.mrpack', 'extracted_modpacks')
