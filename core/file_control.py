import os

def delete_path(path):
    if os.path.isfile(path):
        os.remove(path)
        return "File deleted"
    elif os.path.isdir(path):
        os.rmdir(path)
        return "Folder deleted"