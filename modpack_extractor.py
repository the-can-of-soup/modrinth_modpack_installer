from zipfile import ZipFile
import json
import os

FILENAME_UNSAFE_CHARACTERS: str = r'\/:*?"<>|'

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

def extract_modpack(filename: str, destination_folder: str = '.', is_server: bool = False, print_logs: bool = True) -> None:

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

    # Get output paths
    output_path: str = os.path.join(destination_folder, escape_filename(modpack_name))
    compressed_output_filename: str = output_path + ' (Compressed).zip'
    if os.path.isdir(output_path):
        raise ValueError(f'The folder "{output_path}" already exists! Please remove it first.')

    # Write output zip file
    if print_logs:
        print('Writing output zip file...')
    with ZipFile(compressed_output_filename, 'w') as zf:

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
