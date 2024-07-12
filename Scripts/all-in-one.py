import os
import shutil
import subprocess

def main():
    # Get the current working directory
    current_directory = os.getcwd()
    print(f"Current directory: {current_directory}")
    
    # Define the source directory where the additional files are located
    source_directory = '/home/pabelchem/bodipy/working/derivatives_all'  # Update this path to your source directory
    
    # List of specific files to be copied
    specific_files = [
        "acetonitrile.frcmod",
        "acetonitrile.prep",
        "btb.frcmod",
        "btb.lib",
        "btb.pdb",
        "tleap.sh",
        "amber_input.py",
        "ch3cn.pdb",
        "packmol.py"
    ]
    
    # Iterate over all items in the current directory
    for item in os.listdir(current_directory):
        # Construct the full path of the item
        item_path = os.path.join(current_directory, item)
        
        # Check if the item is a directory and starts with 'bdp'
        if os.path.isdir(item_path) and item.startswith('bdp'):
            print(f"Processing directory: {item_path}")
            
            # Define expected file names based on the directory name
            expected_files = {
                'frcmod': f"{item}.frcmod",
                'lib': f"{item}.lib",
                'pdb': f"{item}.pdb"
            }
            
            # Define destination file names
            destination_files = {
                'frcmod': 'bdp.frcmod',
                'lib': 'bdp.lib',
                'pdb': 'bdp.pdb'
            }
            
            # Check for the presence of expected files and copy them
            for file_type, expected_file_name in expected_files.items():
                source_path = os.path.join(item_path, expected_file_name)
                if os.path.exists(source_path):
                    destination_path = os.path.join(item_path, destination_files[file_type])
                    shutil.copy(source_path, destination_path)
                    print(f"Copied {source_path} to {destination_path}")
                else:
                    print(f"Expected file {expected_file_name} not found in {item_path}")
            
            # Copy specific files to each 'bdp' directory
            for file_name in specific_files:
                source_file_path = os.path.join(source_directory, file_name)
                destination_file_path = os.path.join(item_path, file_name)
                if os.path.exists(source_file_path):
                    shutil.copy(source_file_path, destination_file_path)
                    print(f"Copied {file_name} to {destination_file_path}")
                else:
                    print(f"File {file_name} not found in source directory: {source_directory}")
            
            # Execute packmol.py script in the destination directory
            os.chdir(item_path)  # Change directory to the destination path
            try:
                subprocess.run(['python', 'packmol.py'], check=True)
                print(f"Successfully executed packmol.py in {item_path}")
            except subprocess.CalledProcessError as e:
                print(f"Error executing packmol.py in {item_path}: {e}")

            try:
                os.system("tleap -f tleap.sh")
                print(f"Successfully executed 'tleap -f tleap.sh' in {item_path}")
            except Exception as e:
                print(f"Error executing 'tleap -f tleap.sh' in {item_path}: {e}")

            try:
                os.system("python amber_input.py")
            except Exception as e:
                print(f"Error executing 'python amber_input.py' in {item_path}: {e}")

            finally:
                os.chdir(current_directory)  # Change back to the original directory


if __name__ == "__main__":
    main()

