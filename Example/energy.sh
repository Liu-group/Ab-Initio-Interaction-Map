rm -f temp energy  # -f to ignore nonexistent files and suppress error messages

for i in $(seq 1 100); do
    echo $i >> temp
    grep "TeraChem" frame$i/scr-bdp/optim.xyz | awk '{print $1}' | tail -n1 >> energy
done

paste temp energy > energy.txt

