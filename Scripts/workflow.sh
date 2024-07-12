#!/bin/bash
#SBATCH --time=00:05:00   
#SBATCH --nodes=1         
#SBATCH --mem=1G          
#SBATCH --ntasks=1     
#SBATCH --cpus-per-task=1 
#SBATCH --gres=gpu:1   
module load TeraChem
conda activate autosolvate
echo $0 $1
python xyz_to_pdb.py $1
