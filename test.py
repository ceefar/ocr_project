import os

root_path = f"tempDir" 

try:
        os.mkdir(root_path) 
except FileExistsError:
        pass
