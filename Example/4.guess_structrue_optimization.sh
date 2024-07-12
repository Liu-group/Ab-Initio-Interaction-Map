# Create cpptraj input file
cat > cpptraj.inp << EOF
parm system.parm
trajin prod.nc 1 last 10
strip :C3N
trajout frame pdb multi
go
exit
EOF

# Run cpptraj with the input file
cpptraj cpptraj.inp

# Convert PDB files to XYZ format using Open Babel
for file in frame*; do
  obabel -ipdb "$file" -O "${file}.xyz"
done

# Loop from 1 to 100
for i in {1..100}; do
  # Create the directory if it doesn't already exist
  mkdir -p "frame$i"
  
  # Move to the directory
  cd "frame$i"
  
  # Move the corresponding .xyz file and copy the necessary input files
  mv "../frame.$i.xyz" "bdp.xyz"
  cp "/home/pabelchem/storage/bdp.inp" "bdp.inp"
  cp "/home/pabelchem/storage/terachem.sh" "terachem.sh"
  
  # Submit the job using sbatch
  sbatch terachem.sh
  
  # Return to the previous directory
  cd ..
done

# Remove all frame.* files
rm frame.*

