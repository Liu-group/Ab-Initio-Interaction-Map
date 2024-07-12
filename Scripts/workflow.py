import os
import sys
import time
import subprocess
import numpy as np

from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem.Draw import IPythonConsole, MolsToGridImage, MolToImage

from autosolvate.autosolvate import AmberParamsBuilder
from autosolvate.dockers import AntechamberDocker, TeraChemDocker, ParmchkDocker, TleapDocker
from autosolvate.molecule import Molecule
from autosolvate.utils import *

def generate_mol2_for_bodipy(pdbpath, workfolder):
    ccwwdd = os.getcwd()
    pdbpath = os.path.abspath(pdbpath)
    workfolder = os.path.abspath(workfolder)
    if not os.path.exists(workfolder):
        os.makedirs(workfolder, exist_ok=True)
    name = os.path.splitext(os.path.basename(pdbpath))[0]
    subprocess.run(f"cp {pdbpath} {workfolder}/", shell=True, cwd=ccwwdd)
    os.chdir(workfolder)
    print(os.getcwd())

    # replace the boron atom with carbon
    subprocess.run(f"cp {name}.pdb {name}-replaceB.pdb", shell=True)
    # subprocess.run(f"sed -i 's/ B / C /g' {workfolder}/{name}/{name}-replaceB.pdb", shell=True, cwd=cwd)
    with open(f"{name}-replaceB.pdb", "r") as f:
        lines = f.readlines()
    boron_lineidxs = []
    for i, line in enumerate(lines):
        if line.startswith("ATOM") or line.startswith("HETATM"):
            if line[12:16].strip() == "B":
                boron_lineidxs.append(i)
    for i in boron_lineidxs:
        lines[i] = lines[i].replace(" B ", " C ")
    with open(f"{name}-replaceB.pdb", "w") as f:
        f.writelines(lines)

    # get the atomtypes for the sidechain of the replaced molecule
    # as antechamber does not recognize with boron atom
    mol_replB = Molecule(f"{workfolder}/{name}-replaceB.pdb", 
                        charge = -1, 
                        multiplicity = 1, 
                        name = f"{name}-replaceB", 
                        residue_name = "BDP", 
                        folder = workfolder)
    mol_replB.update()
    docker = AntechamberDocker(
        charge_method="bcc", 
        out_format="mol2", 
        workfolder=workfolder, 
        exeoutfile=f"{workfolder}/{name}-replaceB-antechamber.out",
        ek = "maxcyc=0",
        )
    docker.run(mol_replB)

    # get the correct resp charges for the original molecule
    mol = Molecule(f"{workfolder}/{name}.pdb",
                    charge = 0,
                    multiplicity = 1,
                    name = name,
                    residue_name = "BDP",
                    folder = workfolder)
    mol.update()
    tcdocker = TeraChemDocker(jobname = mol.name + "-geomopt", workfolder = workfolder, sbatch_use=False,
                            basis = "gfnxtb", method = "gfnxtb")
    tcdocker.optimize_geometry(mol)
    tcdocker = TeraChemDocker(jobname = mol.name + "-respfit", workfolder = workfolder, sbatch_use=False,
                            basis = "lacvps_ecp", method = "rhf")
    charges = tcdocker.resp(mol)
    modify_mol2(mol_replB.mol2, mol.reference_name + ".mol2", charges)
    mol.mol2 = mol.reference_name + ".mol2"

    # symmetrize the charges
    fake_atom_info, fake_bond_info = read_mol2(mol_replB.mol2)
    fakechgs = np.array(fake_atom_info[7])
    unique_chgs = np.unique(fakechgs)
    symmetric_atom_indexs = []
    for chg in unique_chgs:
        symmetric_atom_indexs.append(np.where(fakechgs == chg)[0])

    real_atom_info, real_bond_info = read_mol2(mol.mol2)
    realchgs = np.array(real_atom_info[7])
    for symmetrix_atom_pairs in symmetric_atom_indexs:
        avgchg = np.mean(realchgs[symmetrix_atom_pairs])
        realchgs[symmetrix_atom_pairs] = avgchg
    realchgs -= np.sum(realchgs) / len(realchgs)
    real_atom_info[7] = list(realchgs)
    write_mol2(real_atom_info, real_bond_info, mol.mol2)

    # replace the carbon with boron in the mol2 file
    with open(mol.pdb, "r") as f:
        lines = f.readlines()
    atmnum = 0
    boron_indexes = []
    for line in lines:
        if line.startswith("ATOM") or line.startswith("HETATM"):
            if line[12:16].strip() == "B":
                boron_indexes.append(atmnum)
            atmnum += 1
    # replace the carbon at the boron index in the mol2 file with boron
    with open(mol.mol2, "r") as f:
        lines = f.readlines()
    target_line_idxes = []
    for i, line in enumerate(lines):
        if line.startswith("@<TRIPOS>ATOM"):
            for boron_index in boron_indexes:
                target_line_idxes.append(i + boron_index + 1)
            break
    for target_line_idx in target_line_idxes:
        lines[target_line_idx] = lines[target_line_idx].replace(" C ", " B ")
        lines[target_line_idx] = lines[target_line_idx].replace(" c3 ", " B  ")
        lines[target_line_idx] = lines[target_line_idx].replace(" b ", " B ")
    with open(mol.mol2, "w") as f:
        f.writelines(lines)

    # create a saturated pdb for the molecule to enable substrcture search
    der_pdbpath = os.path.join(workfolder, f"{name}.pdb")
    der_pdbpath_allsat = os.path.join(workfolder, f"{name}_allsat.pdb")
    subprocess.run(f"obabel -i pdb {der_pdbpath} -o pdb -O {der_pdbpath_allsat} -ac", shell=True)

    # template_pdb = os.path.join(cwd, "template", "bodipy.pdb")
    # template_pdb_allsat = os.path.join(cwd, "template", "bodipy_allsat.pdb")
    # subprocess.run(f"obabel -i pdb {template_pdb} -o pdb -O {template_pdb_allsat} -ac", shell=True)
    os.chdir(ccwwdd)
    return mol

def generate_amber_params_from_mol2(mol:Molecule, atomtype_in_mol:str, template_frcmod:str):
    # modify the atom types in the mol2 file according to the template
    derivative_mol2 = mol.mol2
    data = np.loadtxt(atomtype_in_mol, dtype=str)
    if data.shape[0] == 0 or data.shape[1] != 3:
        print(f"Warning: no atom type information found in {atomtype_in_mol}")
    else:
        tpl_atom_in_der = data[:,:2].astype(int)
        tpl_type_in_der = data[:,2]

        der_atom_info, der_bond_info = read_mol2(derivative_mol2)
        atomtypes = der_atom_info[5]
        for (id_in_tpl, id_in_der), atomtype in zip(tpl_atom_in_der, tpl_type_in_der):
            atomtypes[id_in_der] = atomtype
        der_atom_info[5] = atomtypes
        unmodified_mol2_path = derivative_mol2.replace(".mol2", "_unmodified.mol2")
        os.rename(derivative_mol2, unmodified_mol2_path)
        write_mol2(der_atom_info, der_bond_info, derivative_mol2)

    docker = ParmchkDocker(out_format="frcmod", workfolder=mol.folder)
    docker.run(mol)
    subprocess.run(f'cp {mol.frcmod} {mol.frcmod.replace(".frcmod", "-unmodified.frcmod")}', shell=True)
    der_fmod = FrcmodFile(mol.frcmod)
    tpl_fmod = FrcmodFile(template_frcmod)
    der_fmod.update(tpl_fmod)
    der_fmod.write(mol.frcmod)
    docker = TleapDocker(workfolder=mol.folder)
    docker.run(mol)

def get_template_atom_types_in_derivative(derivative_pdb, template_pdb, template_mol2):
    mol_bdp = Chem.MolFromPDBFile(template_pdb, removeHs=False, proximityBonding=False, sanitize=False)
    mol_bnh = Chem.RemoveAllHs(mol_bdp, sanitize=False)
    mol_der = Chem.MolFromPDBFile(derivative_pdb, removeHs=False, proximityBonding=False, sanitize=False)
    mol_dnh = Chem.RemoveAllHs(mol_der, sanitize=False)
    template_heavy_atom_in_heavy_derivative = mol_dnh.GetSubstructMatch(mol_bnh)
    if len(template_heavy_atom_in_heavy_derivative) < 1:
        print(f"Warning: {derivative_pdb} does not contain the template")
        return [], []
    template_heavy_atom_in_heavy_derivative = [[i, template_heavy_atom_in_heavy_derivative[i]] for i in range(len(template_heavy_atom_in_heavy_derivative))]
    # [template_heavy_index, corresponding_heavy_index_in_derivative]
    heavy_atom_in_template   = mol_bdp.GetSubstructMatch(mol_bnh)
    # [heavy_index_in_heavy_template, corresponding_heavy_index_in_template]
    heavy_atom_in_derivative = mol_der.GetSubstructMatch(mol_dnh)
    # [heavy_index_in_heavy_derivative, corresponding_heavy_index_in_derivative]
    template_atom_in_derivative = [
        [heavy_atom_in_template[i], heavy_atom_in_derivative[j]] for i, j in template_heavy_atom_in_heavy_derivative]
    template_atomtype_in_derivative = []

    # get the hydrogens in the derivative that connects with the heavy atoms in the template
    template_hydrogen_in_derivative = []
    template_hydrogen_atomtype_in_derivative = []
    tpl_atom_info, tpl_bond_info = read_mol2(template_mol2)
    for id_in_tpl, id_in_der in template_atom_in_derivative:
        atom_in_tpl = mol_bdp.GetAtomWithIdx(id_in_tpl)
        atom_in_der = mol_der.GetAtomWithIdx(id_in_der)
        template_atomtype_in_derivative.append(tpl_atom_info[5][id_in_tpl])

        connected_hydrogen_in_der = [nbr.GetIdx() for nbr in atom_in_der.GetNeighbors() if nbr.GetAtomicNum() == 1]
        connected_hydrogen_in_tpl = [nbr.GetIdx() for nbr in atom_in_tpl.GetNeighbors() if nbr.GetAtomicNum() == 1]
        if len(connected_hydrogen_in_tpl) < 1:
            continue
        atom_type = tpl_atom_info[5][connected_hydrogen_in_tpl[0]]
        for hid_in_der in connected_hydrogen_in_der:
            template_hydrogen_in_derivative.append([connected_hydrogen_in_tpl[0], hid_in_der])
            template_hydrogen_atomtype_in_derivative.append(atom_type)
    template_atom_in_derivative = template_atom_in_derivative + template_hydrogen_in_derivative
    template_atomtype_in_derivative = template_atomtype_in_derivative + template_hydrogen_atomtype_in_derivative
    return template_atom_in_derivative, template_atomtype_in_derivative

def create_allsat_pdb(original_pdb:str, allsat_pdb:str = None):
    if allsat_pdb is None:
        allsat_pdb = original_pdb.replace(".pdb", "_allsat.pdb")
    subprocess.run(f"obabel -i pdb {original_pdb} -o pdb -O {allsat_pdb} -xn", shell=True)
    return allsat_pdb


def write_data(tpl_atom_in_der, tpl_type_in_der, fpath):
    with open(fpath, "w") as f:
        for (id_in_tpl, id_in_der), atomtype in zip(tpl_atom_in_der, tpl_type_in_der):
            f.write(f"{id_in_tpl:>6d} {id_in_der:>6d} {atomtype:>6s}\n")

def generate_atomtype_data_main(derivative_pdb:str, template_pdb:str, template_mol2:str, atomtypefile:str = None):
    if atomtypefile is None:
        atomtypefile = derivative_pdb.replace(".pdb", "_atomtype.txt")
    saturated_template_pdb = template_pdb.replace(".pdb", "_allsat.pdb")
    if not os.path.exists(saturated_template_pdb):
        saturated_template_pdb = create_allsat_pdb(template_pdb)
    saturated_derivative_pdb = create_allsat_pdb(derivative_pdb)
    tpl_atom_in_der, tpl_type_in_der = get_template_atom_types_in_derivative(saturated_derivative_pdb, saturated_template_pdb, template_mol2)
    write_data(tpl_atom_in_der, tpl_type_in_der, atomtypefile)

if __name__ == "__main__":
    orgpdbpath = sys.argv[1]
    name = os.path.splitext(os.path.basename(orgpdbpath))[0]

    mainfolder = os.getcwd()
    workfolder = os.path.join(mainfolder, "build", name)
    template_pdb = os.path.join(mainfolder, "template", f"bodipy.pdb")
    template_mol2 = os.path.join(mainfolder, "template", f"bodipy.mol2")
    template_frcmod = os.path.join(mainfolder, "template", "bodipy.frcmod")
    mol = generate_mol2_for_bodipy(orgpdbpath, workfolder)
    mol:Molecule
    atomtype_in_mol = mol.reference_name + "_atomtype.dat"
    generate_atomtype_data_main(mol.pdb, template_pdb, template_mol2, atomtype_in_mol)
    generate_amber_params_from_mol2(mol, atomtype_in_mol, template_frcmod)