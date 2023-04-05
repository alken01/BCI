import os

# Set the directory path
directory_path = "./"

# Get a list of all the files in the directory
file_list = os.listdir(directory_path)

# Loop through each file in the directory
for file_name in file_list:
    # Check if the file starts with "SSVEP_"
    if file_name "SSVEP_"):
        # Get the new file name without "SSVEP_"
        new_file_name = file_name[6:]
        # Rename the file
        os.rename(os.path.join(directory_path, file_name), os.path.join(directory_path, new_file_name))
