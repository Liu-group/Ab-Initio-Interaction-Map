#!/bin/bash

# Loop through directories frame1 to frame100
for i in $(seq 1 100); do
    directory_name="frame${i}"
    bdp_out_path="${directory_name}/bdp.out"
    
    echo "Checking ${directory_name}..."
    
    # Check if bdp.out exists to avoid grep error
    if [ ! -f "${bdp_out_path}" ]; then
        echo "${bdp_out_path} does not exist, skipping."
        continue
    fi
    
    # Search for the keyword in bdp.out
    if grep -q "Optimization Converged." "${bdp_out_path}"; then
        echo "Optimization has already converged in ${directory_name}, skipping."
    else
        echo "Optimization not converged in ${directory_name}, processing..."
        # Remove scr* directories and submit job
        rm -rf "${directory_name}/scr*"
        (cd "${directory_name}" && sbatch terachem.sh)
    fi
done

