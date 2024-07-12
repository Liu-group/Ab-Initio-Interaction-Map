import os
import subprocess

def main():
    item_path = os.getcwd()  # Set item_path to the current directory
    current_directory = os.getcwd()  # Store the current directory

    try:
        # Execute packmol.py script
        subprocess.run(['python', 'packmol.py'], check=True)
        print(f"Successfully executed packmol.py in {item_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error executing packmol.py in {item_path}: {e}")

    try:
        # Execute tleap script
        subprocess.run(["tleap", "-f", "tleap.sh"], check=True)
        print(f"Successfully executed 'tleap -f tleap.sh' in {item_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error executing 'tleap -f tleap.sh' in {item_path}: {e}")

    try:
        # Execute amber_input.py script
        subprocess.run(["python", "amber_input.py"], check=True)
        print(f"Successfully executed 'python amber_input.py' in {item_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error executing 'python amber_input.py' in {item_path}: {e}")

if __name__ == "__main__":
    main()

