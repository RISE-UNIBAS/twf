import os
import shutil


def delete_all_in_folder(folder_path):
    """This function deletes all files and folders in the specified directory."""

    # Check if the folder exists
    if not os.path.exists(folder_path):
        # print(f"The specified directory does not exist: {folder_path}")
        return

    # Loop through each item in the directory
    for item_name in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item_name)

        try:
            if os.path.isfile(item_path) or os.path.islink(item_path):
                # If it's a file or symlink, delete it
                os.unlink(item_path)
            elif os.path.isdir(item_path):
                # If it's a directory, delete it and all its contents
                shutil.rmtree(item_path)
        except Exception as e:
            print(f"Failed to delete {item_path}. Reason: {e}")