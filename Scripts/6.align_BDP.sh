#!/bin/bash

cat > align.tcl << 'EOF'
# Load the PDB file
mol load pdb combined_frames.pdb

# Select the reference atoms from the first frame
set sel [atomselect top "resname BDP" frame 0]

# Get the number of frames
set num_frames [molinfo top get numframes]

# Align each frame to the first frame
for {set i 0} {$i < $num_frames} {incr i} {
    # Create a new selection for the current frame to align
        set cur_sel [atomselect top "resname BDP" frame $i]
            # Measure the transformation needed to align this selection to the reference
                set trans [measure fit $cur_sel $sel]
                    # Select all atoms in the current frame
                        set all [atomselect top "all" frame $i]
                            # Apply the transformation
                                $all move $trans
                                    # Save the aligned frame to a uniquely named PDB file
                                        set file_name "aligned_frame_${i}.pdb"
                                            $all writepdb $file_name
                                            }


exit
EOF



cat > extract_BDP_first_frame.tcl << 'EOF'
# Load the PDB file
mol load pdb combined_frames.pdb

# Get the number of frames
set bdp_residue [atomselect top "resname BDP" frame 0]

set output_file "BDP_residue_first_frame.pdb"
$bdp_residue writepdb $output_file

exit
EOF

vmd -dispdev text -e extract_BDP_first_frame.tcl
vmd -dispdev text -e align.tcl

# Define the output file
output_file="combined_models_pdb_file.pdb"
# Clear the output file if it already exists
> "$output_file"

# Define the range of frame indices
start_frame=0
end_frame=99

# Loop through each frame index
for i in $(seq $start_frame $end_frame); do
    # Define the filename for the current frame
    filename="aligned_frame_${i}.pdb"
    
    # Check if the file exists
    if [[ -f "$filename" ]]; then
        # Write the MODEL record for the current model
        echo "MODEL     $(printf "%4d" $((i + 1)))" >> "$output_file"
        
        # Read the file and exclude lines with "CRYST1", "END", or "ENDMDL"
        grep -v -E "^(CRYST1|END|ENDMDL)" "$filename" >> "$output_file"
        
        # Write the ENDMDL record to denote the end of the current model
        echo "ENDMDL" >> "$output_file"
    else
        echo "Warning: File $filename does not exist."
    fi
done

#rm aligned_frame_*

grep ' I   BTB ' combined_models_pdb_file.pdb > boron.pdb
sed -i '1d; $d' BDP_residue_first_frame.pdb
cat BDP_residue_first_frame.pdb boron.pdb > new.pdb

