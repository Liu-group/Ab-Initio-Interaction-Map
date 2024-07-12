def pdb_to_xyz(pdb_path, xyz_path):
    """
    Convert a PDB file to an XYZ file format.

    Parameters:
    - pdb_path: Path to the input PDB file ('BDP_residue_first_frame.pdb').
    - xyz_path: Path to the output XYZ file ('project.xyz').
    """
    # Read the PDB file and extract atom type and XYZ coordinates
    with open(pdb_path, 'r') as pdb_file:
        lines = pdb_file.readlines()
        atoms = []
        for line in lines:
            if line.startswith('ATOM'):
                # Extracting relevant data: atom type and XYZ coordinates
                atom_type = line[76:78].strip()
                x = line[30:38].strip()
                y = line[38:46].strip()
                z = line[46:54].strip()
                atoms.append(f"{atom_type}     {x}  {y}  {z}")
    
    # Write to the XYZ file
    with open(xyz_path, 'w') as xyz_file:
        # Writing the number of atoms and an empty title line
        xyz_file.write(f"{len(atoms)}\n\n")
        # Writing atom details
        for atom in atoms:
            xyz_file.write(atom + "\n")

# Specify the input and output file paths using the names mentioned
pdb_path = 'BDP_residue_first_frame.pdb'
xyz_path = 'project.xyz'

# Call the function with the specified file paths
pdb_to_xyz(pdb_path, xyz_path)

# You can place this script in the same directory as your PDB file and run it.

