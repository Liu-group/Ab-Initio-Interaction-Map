cat > cpptraj.inp << EOF
parm system.parm
trajin prod_12.nc 1 last 10
strip :C3N
trajout frame pdb multi
go
exit
EOF

cpptraj cpptraj.inp

for file in frame*; do
  obabel -ipdb "$file" -O "${file}.xyz"
done


# Loop from 1 to 100
for i in {1..100}; do
# Create the directory if it doesn't already exist
    mkdir -p "frame$i"
  # Check if the corresponding .xyz file exists
    cd frame$i 
    mv "../frame.$i.xyz" "bdp.xyz"
    cp "/home/pabelchem/storage/bdp.inp" "bdp.inp"
    cp "/home/pabelchem/storage/terachem.sh" "terachem.sh"
    sbatch terachem.sh
    cd ../
done

rm frame.*
