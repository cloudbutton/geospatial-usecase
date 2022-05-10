import argparse
from lidarpartitioner import create_partitions

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='lidarpartitioner')
    parser.add_argument('-f', '--file-name', type=str, help='Input file path', required=True)
    parser.add_argument('-o', '--out-dir', type=str, help='Output directory path', required=True)
    parser.add_argument('-p', '--partition-size', type=int, help='Number of points for each partition', required=True)
    parser.add_argument('-b', '--buffer-size', type=int, help='Distance for buffer points', default=0, required=False)
    args = parser.parse_args()

    create_partitions(file_name=args.file_name, out_dir=args.out_dir, partition_size=args.partition_size,
                      buffer_size=args.buffer_size)
