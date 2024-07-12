#!/bin/bash
#SBATCH --time=00:05:00  # Assuming cleanup won't take much time
#SBATCH --ntasks=1
#SBATCH --mem=1G
#SBATCH --cpus-per-task=1
rm -rf autosolvate template workflow.sh workflow.py xyz_to_pdb.py slurm* cleanup.sh

