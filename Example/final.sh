#!/bin/bash
#SBATCH --time=0:30:00
#SBATCH --nodes=1
#SBATCH --partition=day-long
#SBATCH --mem=5G
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --gres=gpu:1
#SBATCH --dependency=afterok:344296:344297:344298:344299:344300:344301:344302:344303:344304:344305:344306:344307:344308:344309:344310:344311:344312:344313:344314:344315:344316:344317:344318:344319:344320:344321:344322:344323:344324:344325:344326:344327:344328
#SBATCH -e %J.err
#SBATCH -o %J.out
python pmf_script.py