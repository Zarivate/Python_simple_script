import os
import json
import shutil
from subprocess import PIPE, run
import sys


# Variable to hold string to be looked for in directories
GAME_DIR_PATTERN = "game"


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


def main(source_directory, target_directory):

    # Get current working directory where Python file was run
    cwd = os.getcwd()
    # Get complete user paths
    source_path = os.path.join(cwd, source_directory)
    target_path = os.path.join(cwd, target_directory)

    game_paths = find_all_game_paths(source_path)
    print(game_paths)


# Make sure user directly invoked file
if __name__ == "__main__":
    args = sys.argv
    # Make sure have correct number of user arguments
    if len(args) != 3:
        raise Exception("A source and target directory must both be passed. One is missing.")

    # Get source and target directories
    source, target = args[1:]
    main(source, target)
