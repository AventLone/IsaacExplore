#!/bin/bash
# export ROS_DISTRO=jazzy
# export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
# export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/avent/Apps/Miniforge3/envs/IsaacSim/lib/python3.11/site-packages/isaacsim/exts/isaacsim.ros2.bridge/jazzy/lib

# >>> mamba initialize >>>
# !! Contents within this block are managed by 'mamba shell init' !!
export MAMBA_EXE='/home/avent/Apps/Miniforge3/bin/mamba';
export MAMBA_ROOT_PREFIX='/home/avent/Apps/Miniforge3';
__mamba_setup="$("$MAMBA_EXE" shell hook --shell bash --root-prefix "$MAMBA_ROOT_PREFIX" 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__mamba_setup"
else
    alias mamba="$MAMBA_EXE"  # Fallback on help from mamba activate
fi
unset __mamba_setup
# <<< mamba initialize <<<

mamba activate IsaacSim
source /home/avent/Apps/IsaacSim5.1/setup_conda_env.sh

python /home/avent/Desktop/PythonProjects/IsaacExplore/formal_sdg_gui.py