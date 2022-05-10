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

