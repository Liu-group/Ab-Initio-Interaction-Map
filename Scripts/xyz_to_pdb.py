import sys
import subprocess

def xyz_to_pdb(xyz_filename):
    # Generate the PDB filename based on the XYZ filename
    pdb_filename = xyz_filename.rsplit('.', 1)[0] + '.pdb'

    # Read the XYZ file
    with open(xyz_filename, 'r') as xyz_file:
        lines = xyz_file.readlines()

    # Prepare the PDB content
    pdb_content = []
    atom_counts = {}
    for i, line in enumerate(lines[2:]):  # Skip the first two lines of the XYZ file
        parts = line.split()
        if len(parts) < 4:
            continue  # Skip lines that don't have at least 4 parts
        element = parts[0]
        x, y, z = parts[1:4]

        # Update atom count and generate a unique atom name
        if element not in atom_counts:
            atom_counts[element] = 1
        else:
            atom_counts[element] += 1

        # Handle atom naming for unique identification
        if atom_counts[element] == 1:
            atom_name = element  # Use the element name directly for the first occurrence
        else:
            atom_name = f"{element}{atom_counts[element] - 1}"  # Append count for subsequent occurrences

        # Format the line to match the aaa.pdb spacing
        pdb_line = f"ATOM  {i + 1:>5}  {atom_name:<3} BDP     1    {float(x):>8.3f}{float(y):>8.3f}{float(z):>8.3f}  1.00  0.00\n"
        pdb_content.append(pdb_line)

    # Add TER and END lines
    pdb_content.append("TER\n")
    pdb_content.append("END\n")

    # Write the PDB file
    with open(pdb_filename, 'w') as pdb_file:
        pdb_file.writelines(pdb_content)
    print(f"Converted '{xyz_filename}' to '{pdb_filename}'.")

    return pdb_filename  # Return the path of the generated PDB file

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python xyz_to_pdb.py <input.xyz>")
    else:
        xyz_filename = sys.argv[1]
        pdb_filename = xyz_to_pdb(xyz_filename)  # Capture the returned PDB filename


        # Use subprocess to call workflow.py with the PDB filename
subprocess.run(["python", "workflow.py", pdb_filename])

