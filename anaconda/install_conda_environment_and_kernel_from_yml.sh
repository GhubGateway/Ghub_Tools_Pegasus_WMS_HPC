#!/bin/bash -l

# Create the conda environment and associated kernel.
#
# Usage:
# source ./install_conda_environment_and_kernel_from_yml.sh conda_choice environment

# conda uses the libmamba solver.
# See conda info user-agent: solver/libmamba
conda_choice=$1
echo "conda_choice: "${conda_choice}
environment=$2
echo "environment: "$environment

conda=$(which conda)
echo "conda: "${conda}
#echo "#conda: "${#conda}
# Length of /bin/conda = 10
len=$(( ${#conda} - 10 ))
#echo "len: "${len}
conda_root=${conda:0:len}
echo "conda_root: "${conda_root}

tool_env_dir=${conda_root}/envs/${environment}
tool_kernel_json_dir="${conda_root}/share/jupyter/kernels/${environment}"

conda_env_yml=./${conda_choice}_${environment}_environment.yml

start1=$(date +%s)
echo "Creating env "${environment}"..."
# -n,--name: Name of the environment
${conda} env create --name ${environment} --file ${conda_env_yml}
end=$(date +%s)
echo "Env ${environment} created. Elapsed time: $((($end-$start1)/60)) minutes"

echo "Activating env "${environment}"..."
# Observation, conda activate returns Your shell has not been properly configured to use conda activate and
# conda init bash returns No action taken.
. ${conda_root}/bin/activate ${environment}
echo "Env ${environment} activated"

echo "Installing the kernel for env "${environment}"..."

if [[ ${environment} == "geospatial-2021-09" ]]; then
    if [[ ${conda_choice} == "anaconda-6" ]]; then
        python -m ipykernel install --sys-prefix --name "geospatial-anaconda-6" --display-name "geospatial-plus python3"
        python -m ipykernel install --prefix ${conda_root} --name "geospatial-anaconda-6" --display-name "geospatial-plus python3"
    else
        python -m ipykernel install --sys-prefix --name "geospatial-2021-09" --display-name "geospatial-plus python3"
        python -m ipykernel install --prefix ${conda_root} --name "geospatial-2021-09" --display-name "geospatial-plus python3"
    fi
else
    python -m ipykernel install --sys-prefix --name ${environment} --display-name "Python3 (${environment})"
    python -m ipykernel install --prefix ${conda_root} --name ${environment} --display-name "Python3 (${environment})"
fi

KERNEL_JSON_PATH="${tool_kernel_json_dir}/kernel.json"
# For the environment to get activated when the kernel is selected, modify ${KERNEL_JSON_PATH} and add the PATH env variable. For a reference see /apps/share64/debian10/anaconda/anaconda-7/share/jupyter/kernels/geospatial-2021-09/kernel.json.
echo ${KERNEL_JSON_PATH}

# Define the environment variable name and value
ENV_VAR_NAME="PATH"
#echo ${ENV_VAR_NAME}
ENV_VAR_VALUE="${tool_env_dir}/bin:${conda_root}/bin:/bin:/usr/bin:/usr/bin/X11:/sbin:/usr/sbin"
#echo ${ENV_VAR_VALUE}

# Check if the kernel.json file exists
if [ ! -f "${KERNEL_JSON_PATH}" ]; then
    echo "Error: kernel.json not found at ${KERNEL_JSON_PATH}"
else
    # jq is like sed for JavaScript Object Notation (JSON) data.
    # Add or update the environment variable in the 'env' section of kernel.json
    # If 'env' does not exist, it will be created.
    # If the variable already exists, its value will be updated.
    jq --arg name "$ENV_VAR_NAME" --arg value "$ENV_VAR_VALUE" \
       '.env += {($name): $value}' "${KERNEL_JSON_PATH}" > "${KERNEL_JSON_PATH}.tmp" && \
    mv "${KERNEL_JSON_PATH}.tmp" "${KERNEL_JSON_PATH}"

    echo "Environment variable '${ENV_VAR_NAME}' added/updated in ${KERNEL_JSON_PATH}"
    
    echo "${KERNEL_JSON_PATH}:"
    cat ${KERNEL_JSON_PATH}
fi

echo "Deactivating env "${environment}"..."
. ${conda_root}/bin/deactivate
echo "Env ${environment} deactivated"

echo "which jupyter: "$(which jupyter)
echo "which python: "$(which python)
echo "jupyter kernelspec list: "$(jupyter kernelspec list)

end=$(date +%s)
echo "Done. Total elapsed time: $((($end-$start1)/60)) minutes"
