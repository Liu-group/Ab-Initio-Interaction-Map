import os
import glob

def keep_last_geometry(input_file_path, output_file_path):
    with open(input_file_path, 'r') as file:
        lines = file.readlines()

    # Find the last geometry
    num_atoms = lines[0].strip()  # Assuming the number of atoms is in the first line
    last_geometry_start = None
    for i, line in enumerate(lines):
        if line.strip() == num_atoms:
            last_geometry_start = i

    # Write the last geometry back to the specified output file
    if last_geometry_start is not None:
        with open(output_file_path, 'w') as file:
            file.writelines(lines[last_geometry_start:])
    else:
        print("Could not find the last geometry in the file.")

# Loop through directories frame1 to frame100
for i in range(1, 101):
    print(f'Processing directory frame{i}') 
    directory_name = f'frame{i}'
    input_file_path = f'{directory_name}/scr-bdp/optim.xyz'  # Constructed input file path
    output_file_path = f'{directory_name}/optim.xyz'  # Constructed output file path

    # Check if the directory and input file exist before proceeding
    import os
    if os.path.isdir(directory_name) and os.path.isfile(input_file_path):
        keep_last_geometry(input_file_path, output_file_path)
    else:
        print(f"Directory or input file does not exist for {directory_name}")

def get_first_residue_atom_number_from_xyz(xyz_directory):
    xyz_files = glob.glob(f"../*.xyz")
    if not xyz_files:
        print("No .xyz file found.")
        return None
    xyz_filename = xyz_files[0]

    with open(xyz_filename, 'r') as file:
        lines = file.readlines()
    
    # The atom number for the end of the first residue is total lines minus 2
    # This accounts for the first line (total atom count) and the second line (comment/blank)
        atom_number = len(lines) - 2
    return atom_number


    print("Atom number not found.")
    return None

def xyz_to_pdb(xyz_filename, pdb_filename, residue1='BDP', residue2='BTB'):
    first_residue_atom_number = get_first_residue_atom_number_from_xyz(os.path.dirname(xyz_filename))
    
    with open(xyz_filename, 'r') as xyz_file:
        lines = xyz_file.readlines()
    atom_lines = lines[2:]

    with open(pdb_filename, 'w') as pdb_file:
        atom_count = 1
        for line in atom_lines:
            parts = line.split()
            atom_type = parts[0]
            x, y, z = parts[1:4]
            if atom_count <= first_residue_atom_number:
                residue_name = residue1
                residue_number = 1
            else:
                residue_name = residue2
                residue_number = 2
                if atom_count == first_residue_atom_number + 1:
                    pdb_file.write("TER\n")

            pdb_line = f"ATOM  {atom_count:>5} {atom_type:<4} {residue_name:3} {residue_number:>4}    {float(x):>8.3f}{float(y):>8.3f}{float(z):>8.3f}  1.00  0.00           {atom_type:>2}\n"
            pdb_file.write(pdb_line)
            atom_count += 1

def combine_pdbs_into_one(parent_directory, combined_pdb_filename):
    frame_dirs = sorted(glob.glob(os.path.join(parent_directory, 'frame*')))
    model_number = 1
    with open(combined_pdb_filename, 'w') as combined_file:
        for frame_dir in frame_dirs:
            xyz_filename = os.path.join(frame_dir, 'optim.xyz')
            pdb_filename = xyz_filename.replace('.xyz', '.pdb')
            xyz_to_pdb(xyz_filename, pdb_filename)
            combined_file.write(f"MODEL        {model_number}\n")
            with open(pdb_filename, 'r') as pdb_file:
                combined_file.write(pdb_file.read())
            combined_file.write("ENDMDL\n")
            model_number += 1

parent_directory = "."  # Adjust as necessary
combined_pdb_filename = os.path.join(parent_directory, "combined_frames.pdb")
combine_pdbs_into_one(parent_directory, combined_pdb_filename)
print(f"Generated 'combined_frames.pdb'")

