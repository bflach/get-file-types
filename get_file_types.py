"""
This package will provide file extension information for each file in the current working directory,
or the path provided in the command line argument.
"""
import argparse
import pathlib
from pathlib import Path
import pkgutil
import csv
import magic
from tqdm import tqdm

# Instantiate the parser
parser = argparse.ArgumentParser(
    description='The app provides file information for each file under the given path in a separate output file.')

# Optional arguments
parser.add_argument('--lookup_path', type=str,
                    help='An optional lookup path argument'
                    )
parser.add_argument('--output_file', type=str,
                    help='An optional output file path/name argument')

# Switch for recursive lookup
parser.add_argument('--recursive', action='store_true',
                    help='Is the lookup recursive?')

# Parse the arguments
args = parser.parse_args()

# Get the path for the lookup
try:
    lookup_path = Path(args.lookup_path) if args.lookup_path else pathlib.Path().cwd()
    lookup_path = lookup_path if lookup_path.exists() else pathlib.Path().cwd()
    lookup_path_list = list(lookup_path.glob('**/*.*')) if args.recursive else list(lookup_path.glob('*.*'))
except Exception as e:
    print(f'Exception occurred when parsing the given lookup path: {e}')
    lookup_path_list = list()

output_filename = Path(args.output_file) if args.output_file else Path('file_info.csv')

# Define the "magic database file" location
try:
    magic_file = Path('magic.mgc')
    magic_file.resolve(strict=True)
    file_magic = magic.Magic(magic_file=magic_file)
    file_magic_mime = magic.Magic(magic_file=magic_file, mime=True)
except FileNotFoundError:
    print(f'No magic.mgc file available in the working directory. Bundled magic.mgc file will be used.')
    file_magic = magic.Magic()
    file_magic_mime = magic.Magic(mime=True)

try:
    with open(output_filename, 'w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=';')
        writer.writerow(
            ['File Name', 'File Name Stem', 'File Extension', 'File Type', 'File Type - mime',
             'Absolute Path'])  # Write csv header
        for file in tqdm(lookup_path_list):
            print(file)  # print current file path to the console
            try:  # Try to get the file type information
                file_type = file_magic.from_file(file)
                file_type_mime = file_magic_mime.from_file(file)
            except PermissionError as e:
                print(f'Permission Error occurred at the following file: {file} \n {e}')
                file_type = r"Couldn't open - Permission Error Occurred"
                file_type_mime = r"Couldn't open - Permission Error Occurred"
            # Write the file information to the output CSV
            writer.writerow([file.name, file.stem, file.suffix, file_type, file_type_mime, file.absolute()])
except Exception as e:
    print(f'Exception occurred during the file list process: {e}')
    pass
