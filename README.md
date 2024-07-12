# Automatic Protocol for Ab-Initio-Interaction-Map

## Overview

This project provides an automated protocol for generating Ab-Initio Interaction Maps (AIIM) using Python and Shell scripting. By following this protocol, users can efficiently compute a 3D interaction map between two molecules from their XYZ coordinates, which is crucial for identifying the sites where the molecules are most likely to interact with each other. The figure represents stepwise workflow for generating AIIM map for BODIPY and TPAB molecules. The blue regions on the Vander Waals surface of BODIPY indicates TPAB molecule most likely to interact with the BODIPY. By following this protocol, one can generate AIIM maps for any two molecules.

![Alt text](./image.png)

The process involves several steps, including setting up a virtual environment, installing necessary dependencies, running the main script to generate a solvent box, equilibration and initial configuration, geometry optimization, and AIIM generation via convolution. These steps are designed to streamline the workflow and provide a comprehensive solution for AIIM generation.

## Authors

Mohammad Pabel Kabir, Fang Liu

## Requirements

> AMBER16 or above 

> Packmol (https://m3g.github.io/packmol/)

> Python 3 or above


## Workflow Description

### Step 1: Parameter file generation for individual systems

Prepare a starting coordinates file (pdb or xyz) for the interested molecues that we would like to generate AIIM. Use antechamber to create AMBER parameter for the two systems and Solvent. Here, we have used an example of BODIPY (system1) and TPAB (system2) molecules in ACN solvent:

antechamber -i system1.pdb -fi pdb -o system1.mol2 -fo mol2 -c bcc -s 2

antechamber -i system2.pdb -fi pdb -o system2.mol2 -fo mol2 -c bcc -s 2

antechamber -i solvent.pdb -fi pdb -o solvent.mol2 -fo mol2 -c bcc -s 2

Convert the resulting mol2 into an AMBER library file: tleap -f convert.leap

After this, we should have the following files: solvent.frcmod, solvent.prep, solvent.pdb, system1.lib, system1.frcmod, system1.pdb, system2.lib, system2.frcmod, system2.pdb

Note: Since, BODIPY and TPAB both molecules have boron (B) atom, the parameter of B atom is not available in Gaff force field, which requires forcefiled fitting. For our case, we did force field fitting to generate the parameter files.

### Step 2: Solvent Box and parameter generation for whole system

Generate solvent box coordinates using the packmol.py script, which employs Packmol to place system1, system2, in interested solvent and creates solvated.pdb file:

python 1.packmol.py

Generate parameter file for whole system with tleap.sh script, which uses tleap tools and loads parameter files for individual systems and generate parameter file for whole system:

tleap -f 2.tleap.sh

This will generate system.pdb, system.parm, and system.rst files

### Step 3: Minimization, Heating and Equilibration

Perform system minimization, heating, and equilibration for 100ps.

python 3.amber_input.py

### Step 4: Initial Configuration Generation and Geometry Optimization

Take snapshot every 1ps time interval from the equilibration trajectory file which will be used as guess structrues for ab-initio geomery optimization. 

python 4.guess_structrue_optimization.py

### Step 5: Desity Calculation and Normalization

Calculate center of mass (COM) points of system2 molecule from the optimized geometry, calculate density of the COM points and Normalize.

python 5.make_pdb_from_opt.py

bash 6.align_BDP.sh

python 7.pdb_to_xyz.py

bash 8.vdw_surface.sh

### Step 6: Generation of .mol2 File and AIIM

Generate mol2 file, which can be opened with a visualization software like VMD.

python 9.generate_mol2.py

## Getting Started

To begin using this workflow, clone the repository and navigate to the root directory. Ensure that all required Python libraries (`NumPy`, `Cython`, `pyvdwsurface`, etc.) are installed. Follow the steps outlined in the README files within each directory to execute the workflow successfully.


## Contributions

Contributions to this workflow are welcome. If you have suggestions for improvement or encounter any issues, please feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE.md) file for more details.
