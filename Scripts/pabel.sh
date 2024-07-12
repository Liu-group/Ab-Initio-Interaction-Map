for env in $(conda env list | awk '{print $1}' | grep -v '#'); do
    echo "Checking environment: $env"
    source activate $env
    conda list | grep 'vmd' && echo "Found in $env"
    conda deactivate
done

