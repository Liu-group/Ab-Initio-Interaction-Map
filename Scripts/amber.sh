#!/bin/bash
#SBATCH --time=24:00:00
#SBATCH --partition=day-long
#SBATCH --nodes=1
#SBATCH --mem=5G
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --gres=gpu:1
echo $HOSTNAME

export LD_LIBRARY_PATH=/home/shared_write/gcc/installation/lib64:$LD_LIBRARY_PATH
pmemd.cuda -O -i prod.in -o prod_12.out -p *.parm -c fram12.rst -r prod_12.rst -x prod_12.nc -inf prod_12.mdinfo
