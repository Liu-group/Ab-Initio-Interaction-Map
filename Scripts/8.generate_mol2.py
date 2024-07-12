import numpy as np
from scipy.spatial import cKDTree

def extract_points(file_path):
    points_coords = []
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split()
            if len(parts) == 3:
                try:
                    x, y, z = map(float, parts)
                    points_coords.append((x, y, z))
                except ValueError:
                    print(f"Skipping invalid line: {line.strip()}")
    return np.array(points_coords)

def extract_b_atom_coords(pdb_file_path):
    b_atom_coords = []
    with open(pdb_file_path, 'r') as file:
        for line in file:
            if line.startswith('ATOM') or line.startswith('HETATM'):
                atom_type = line[76:78].strip()
                if atom_type == 'B':
                    x = float(line[30:38].strip())
                    y = float(line[38:46].strip())
                    z = float(line[46:54].strip())
                    b_atom_coords.append((x, y, z))
    return np.array(b_atom_coords)

def calculate_and_scale_density(points_coords, b_atom_coords, radius=5):
    tree = cKDTree(b_atom_coords)
    density_values = np.array([len(tree.query_ball_point(point, r=radius)) for point in points_coords])
    
    # Normalize to 0-1
    if density_values.max() > 0:  # Avoid division by zero
        scaled_density_values = density_values / density_values.max()
    else:
        scaled_density_values = density_values

    # Transform from 0-1 to -1 to 1
    scaled_density_values = 2 * scaled_density_values - 1
    
    return scaled_density_values

def save_to_mol2(data, coords, file_name):
    header = """@<TRIPOS>MOLECULE
Original B Atom Density
{} 0 0 0 0
SMALL
GASTEIGER

@<TRIPOS>ATOM
""".format(len(coords))
    atom_lines = [f"{i+1:<7} B      {x:>10.4f} {y:>10.4f} {z:>10.4f} B          1 UNL1    {density:>10.4f}\n" for i, (x, y, z, density) in enumerate(zip(coords[:,0], coords[:,1], coords[:,2], data))]
    with open(file_name, 'w') as file:
        file.write(header + "".join(atom_lines))

if __name__ == "__main__":
    file_path = 'points.txt'
    pdb_file_path = 'new.pdb'
    output_file_name = 'original_b_atom_density_map.mol2'

    points_coords = extract_points(file_path)
    b_atom_coords = extract_b_atom_coords(pdb_file_path)
    scaled_density_values = calculate_and_scale_density(points_coords, b_atom_coords)
    save_to_mol2(scaled_density_values, points_coords, output_file_name)
    print(f'Data saved to {output_file_name}')

