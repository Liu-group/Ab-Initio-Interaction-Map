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


## Workflow Description

### Step 1: Parameter file generation

Prepare a starting coordinates file (pdb or xyz) for the interested molecues that we would like to generate AIIM. Use antechamber to create AMBER parameter for the two systems and Solvent. Here, we have used an example of BODIPY and TPAB molecules:

antechamber -i system1.pdb -fi pdb -o system1.mol2 -fo mol2 -c bcc -s 2

antechamber -i system2.pdb -fi pdb -o system2.mol2 -fo mol2 -c bcc -s 2

antechamber -i solvent.pdb -fi pdb -o solvent.mol2 -fo mol2 -c bcc -s 2

Convert the resulting mol2 into an AMBER library file: tleap -f convert.leap

Note: Since, BODIPY and TPAB both molecules have boron (B) atom, the parameter of B atom is not available in Gaff force field, which requires forcefiled fitting. For our case, we did force field fitting to generate the parameter files.

### Step 2: Solvent Box generation

Prepare a project.com file containing methods, basis sets, and the molecule XYZ (sample input file is given in example directory: project.com).

Run 2.gaussian_input.sh to generate all the Gaussian input files.

### Step 3: Job Submission

Modify the 3.gaussian_sub.sh script based on the total number of .com files.

Run 3.gaussian_sub.sh to submit all the jobs.

### Step 4: Data Collection

Run 4.data_collection.sh to collect all the data from the expected excited state.

### Step 5: Generation of .mol2 File

Run 5.estm.sh to generate a sample.mol2 file, which can be opened with a visualization software like VMD.

## Getting Started

To begin using this workflow, clone the repository and navigate to the root directory. Ensure that all required Python libraries (`NumPy`, `Cython`, `pyvdwsurface`, etc.) are installed. Follow the steps outlined in the README files within each directory to execute the workflow successfully.


## Contributions

Contributions to this workflow are welcome. If you have suggestions for improvement or encounter any issues, please feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE.md) file for more details.
