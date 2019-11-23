# Aggregated Multi-task GP
This repository contains the source code for https://arxiv.org/abs/1906.09412
It is based on the [GPy](https://github.com/SheffieldML/GPy) and [HetMOGP](https://github.com/pmorenoz/HetMOGP). Here we use a modified version of the GPy which can be access [here](https://github.com/frb-yousefi/GPy-multitask/tree/multitask-gp).

## Setup Instructions

### Prerequisites 
For reproducibility, all instructions below are tested with this Docker image: [continuumio/anaconda3:2019.07](https://hub.docker.com/layers/continuumio/anaconda3/2019.07/images/sha256-9fad434f3f775ed245f0f888cda954bc93f81ffdc31d4e3e37d69283260c3f41) - which is based on Debian 10 and Anaconda3 and Python 3.7.3 (Ubuntu works as well). The authors may release a Docker image as well in the future.

If you already have a Python 3.7 environment, you may want to skip to the `GPy-multitask installation` part below (and ignore all Docker commands)

```bash
# pull the image
docker pull continuumio/anaconda3:2019.07

# run the image
docker run -i -t --rm -p 8888:8888 continuumio/anaconda3:2019.07 /bin/bash

# the rest of the commands here are assumed to be executed from the Docker image

# install the required packages (needed for Cython extensions of the GPy)
apt update && apt install -y build-essential 

# GPy-multitask installation
# clone a modified version of the GPy toolkit:
git clone https://github.com/frb-yousefi/GPy-multitask.git
cd GPy-multitask

# switch to the multitask-gp branch
git checkout multitask-gp

# Now install GPy based on the instructions provided in the README file (https://github.com/frb-yousefi/GPy-multitask/blob/multitask-gp/README.md)
python setup.py build_ext --inplace

# set PYTHONPATH environment variable to include the GPy-multitask path
echo "export PYTHONPATH=$PWD" >> ~/.bashrc
source ~/.bashrc
cd ..
```

### Multi-task GP Setup
```bash
# clone this repository 
git clone https://github.com/frb-yousefi/aggregated-multitask-gp
cd aggregated-multitask-gp

# install the required Python packages
pip install -r requirements.txt

```

### Sample Notebooks
A sample notebook is provided with this repository. Assuming you're running the Docker image, you can execute this command to start a Jupyter Notebook server and check the sample notebook:

```bash
# starting from the root folder of this cloned repo
cd notebooks
jupyter notebook --port 8888 --ip '*' --allow-root
```
