# LidarPartitioner
Lidar-Partitioner is a novel tool that enables the partitioning of lidar data by dividing it into several chunks with 
somewhat the same sizes.

This repository contains the code and instructions for the LidarPartitioner tool. This tool is a result from the 
[CloudButton](https://cloudbutton.eu/) project. The main functionality of the tool is the correct partitioning of LiDAR 
files for LAS and LAZ formats. 
LidarPartitioner takes care of:
- Read the file to be partitioned, load its metadata and its Point Data Records.
- Create tile partitions of similar size.
- Add a buffer to each partition.
- Write to disk each of the partitions in different files.

## Install
To use and install LidarPartitioner, Python 3.9 is recommended, but older Python versions are supported, up to Python 3.6.  

This repository contains a [setup.py](./setup.py) file that allows to install LidarPartitioner in a Python environment 
using [Pip](https://pypi.org/project/pip/).

Here is a basic installation example: 

```bash
git clone https://github.com/gfinol/Lidar-Partitioner.git
cd Lidar-Partitioner
pip install .
```

## Examples
The LidarPartitioner tool can be used from both the command line and from a Python program. 

As an example, let's see how can we partition the [lasfile.las](./examples/data/lasfile.las) file into several 
chunks of approximately **30,000 points**, using a **buffer distance of 5** and saving the resulting partitions in the 
[partitions](./examples/partitions) folder.

### Using LidarPartitioner from command line
```bash
python -m lidarpartitioner -f "data/lasfile.las" -o "partitions" -p 30000 -b 5
```

### Using LidarPartitioner in a python program

```python
from lidarpartitioner import create_partitions

if __name__ == '__main__':

    # Define input file and output directory
    file_name = 'data/lasfile.las'
    out_dir = 'partitions'

    # Define Partitioner parameters
    partition_size = 30_000
    buffer_size = 5

    # Create partitions
    create_partitions(file_name, out_dir, partition_size, buffer_size)
```
