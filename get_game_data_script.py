import os
import json
import shutil
from subprocess import PIPE, run
import sys

# Variable to hold string to be looked for in directories
GAME_DIR_PATTERN = "game"
GAME_EXTENSION = ".go"

# List of strings that represent commands to run
GAME_COMPILE_COMMAND = ["go", "build"]


# Function to get all the game directories from the data folder
def find_all_game_paths(source):
    game_paths = []

    # Get the root directory, directories, and files from the path recursively through walk()
    for root, dirs, files in os.walk(source):
        # Look through the directories
        for directory in dirs:
            # Check to see if any of them match/have the string we're looking for
            if GAME_DIR_PATTERN in directory.lower():
                # If so, add to game paths list
                path = os.path.join(source, directory)
                game_paths.append(path)

        # Since only need to get the top level of the "data" directory, the _game folders, break in order to avoid
        # any excess recursion
        break

    return game_paths


# Function to get the names of the folders, edit them to remove the "_game" part, from the path
def get_name_from_paths(paths, to_remove):
    # List to hold the new names of the directories
    new_names = []
    for path in paths:
        # Get last aspect of the path, should be the game folder
        _, dir_name = os.path.split(path)
        # Create the new name of the directory by removing the part to remove from it
        new_dir_name = dir_name.replace(to_remove, "")
        # Add newly created directory name to list
        new_names.append(new_dir_name)

    return new_names


# Function to create the new directory for the location of the edited game folders. Takes path to directly to create.
def create_dir(path):
    # Check if directory already exists
    if not os.path.exists(path):
        os.mkdir(path)


# Function to copy any data from the source directory to the destination directory. That or will overwrite any
# pre-existing data already in the destination.
def copy_or_overwrite(source, destination):
    # If the destination already exists, recursively remove it and it's contents
    if os.path.exists(destination):
        shutil.rmtree(destination)
    # Make recursive copy of source into the destination
    shutil.copytree(source, destination)


# Function to create some basic JSON metadata from the games
def create_json_metadata(path, game_dirs):
    # Create some basic JSON data from passed in parameters
    data = {
        "gameNames": game_dirs,
        "numberOfGames": len(game_dirs)
    }
    # Write and or overwrite any data in the file. "with" is used so file closes automatically.
    with open(path, "w") as f:
        # Dump created data into file
        json.dump(data, f)


# Function to compile the actual game data
def compile_game_code(path):
    code_file_name = None
    # Walk through path again, this time only focusing on the files
    for root, dirs, files in os.walk(path):
        for file in files:
            # If the found game file has the extension we're looking for
            if file.endswith(GAME_EXTENSION):
                # Set the code file name to be equal to it and break to avoid any excess recursion since are assuming
                # in this file that there is/will only do so for the first .go extension file it finds in the path
                code_file_name = file
                break
        break

    # If no .go files are found, just return to avoid any compile non-existing file errors
    if code_file_name is None:
        return

    # Pass the commands to each of the .go files found
    command = GAME_COMPILE_COMMAND + [code_file_name]
    run_command(command, path)


# Function to run any commands passed in, uses path that command will be run from
def run_command(command, path):
    # Get current working directory
    cwd = os.getcwd()

    # Change cwd into path so can run go file in its current directory. Change into the path directory.
    os.chdir(path)

    # Run the actual commands to the files using PIPE
    result = run(command, stdout=PIPE, stdin=PIPE, universal_newlines=True)
    print("compile result", result)

    # Change back to current/original working directory
    os.chdir(cwd)

def main(source_directory, target_directory):

    # Get current working directory where Python file was run
    cwd = os.getcwd()
    # Get complete user paths
    source_path = os.path.join(cwd, source_directory)
    target_path = os.path.join(cwd, target_directory)

    # Get all the game folder paths
    game_paths = find_all_game_paths(source_path)

    # Get the new game directories by removing the "game" part from any game paths found
    new_game_dirs = get_name_from_paths(game_paths, "_game")

    # Create target directory
    create_dir(target_path)

    # Loop through every source and game path, pair their corresponding counterparts together with zip
    # and copy the contents into the destination.
    for src, dest in zip(game_paths, new_game_dirs):
        # Destination path will be the combination of the target path with the new game directory name
        dest_path = os.path.join(target_path, dest)
        # Write the actual content into the files
        copy_or_overwrite(src, dest_path)
        # Compile the game data in the newly created destination directories
        compile_game_code(dest_path)

    # Create JSON data file path
    json_path = os.path.join(target_path, "dummy_data.json")
    create_json_metadata(json_path, new_game_dirs)


# Make sure user directly invoked file
if __name__ == "__main__":
    args = sys.argv
    # Make sure have correct number of user arguments
    if len(args) != 3:
        raise Exception("A source and target directory must both be passed. One is missing.")

    # Get source and target directories
    source, target = args[1:]
    main(source, target)
