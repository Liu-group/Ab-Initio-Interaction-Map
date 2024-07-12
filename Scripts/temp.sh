for i in {1..100}; do
  # Check if the corresponding .xyz file exists
    cd frame$i
    sbatch terachem.sh
    cd ../
done

