import re
from math import floor, ceil

import laspy
import numpy as np


def init(filename):

    if filename is None:
        raise Exception("File name not provided")

    with open(filename, 'rb') as f:
        in_file = laspy.read(f)

    point_count = in_file.header.point_count
    m_out_views = []

    return in_file, point_count, m_out_views


def split(wide, narrow, index_wide, index_narrow, i_wide, i_narrow, m_partitions, m_out_views):
    pleft = 0
    pright = len(m_partitions) - 1
    left = m_partitions[pleft]
    right = m_partitions[pright]

    if pright - pleft == 1:
        m_out_views.append(index_wide)
    elif pright - pleft == 2:
        centre = m_partitions[pright - 1]
        m_out_views.append(index_wide[left:centre])
        m_out_views.append(index_wide[centre:right])
    else:
        pcenter = (pleft + pright) // 2
        center = m_partitions[pcenter]

        mask = i_narrow < center
        not_mask = np.logical_not(mask)

        narrow1, narrow2 = narrow[mask], narrow[not_mask]
        index_narrow1, index_narrow2 = index_narrow[mask], index_narrow[not_mask]

        i_narrow1, i_narrow2 = i_narrow[mask], i_narrow[not_mask]

        i_wide[i_narrow1] = np.arange(center - left)
        i_wide[i_narrow2] = np.arange(right - center)

        i_narrow2 = i_narrow2 - center

        decide_split(wide[left:center], narrow1, index_wide[left:center], index_narrow1, i_wide[left:center],
                          i_narrow1, m_partitions[pleft: pcenter + 1] - left, m_out_views)
        decide_split(wide[center:right], narrow2, index_wide[center:right], index_narrow2, i_wide[center:right],
                          i_narrow2, m_partitions[pcenter: pright + 1] - center, m_out_views)

    return m_out_views


def decide_split(v1, v2, index_v1, index_v2, i_v1, i_v2, m_partitions, m_out_views):
    left = m_partitions[0]
    right = m_partitions[-1] - 1

    # Decide the wider direction of the block, and split in that direction
    # to maintain squareness.
    v1range = v1[right] - v1[left]
    v2range = v2[right] - v2[left]

    if v1range > v2range:
        return split(v1, v2, index_v1, index_v2, i_v1, i_v2, m_partitions, m_out_views)
    else:
        return split(v2, v1, index_v2, index_v1, i_v2, i_v1, m_partitions, m_out_views)


def partition(size, partition_size):

    def lround(d):
        if d < 0:
            return ceil(d - 0.5)
        else:
            return floor(d + 0.5)

    num_partitions = size // partition_size

    if size % partition_size:
        num_partitions += 1

    partition_size = size / num_partitions
    m_partitions = [lround(partition_size * i) for i in range(num_partitions + 1)]

    return np.array(m_partitions)


def load(in_las_data, point_count):
    v1 = np.array(in_las_data.x)
    index_v1 = np.argsort(v1)
    v1 = v1[index_v1]
    i_v2 = np.zeros(point_count, dtype=int)
    i_v2[index_v1] = np.arange(point_count)

    v2 = np.array(in_las_data.y)
    index_v2 = np.argsort(v2)
    v2 = v2[index_v2]
    i_v2 = i_v2[index_v2]
    i_v1 = np.zeros(point_count, dtype=int)
    i_v1[i_v2] = np.arange(point_count)

    return v1, v2, index_v1, index_v2, i_v1, i_v2


def run(partition_size, in_las_data, point_count, m_out_views):
    v1, v2, index_v1, index_v2, i_v1, i_v2 = load(in_las_data, point_count)
    m_partitions = partition(point_count, partition_size)
    partitions_indexes = decide_split(v1, v2, index_v1, index_v2, i_v1, i_v2, m_partitions, m_out_views)

    return partitions_indexes


def create_partitions(file_name, out_dir, partition_size=None, buffer_size=None):
    print('Start partitioning...')
    in_las_data, point_count, m_out_views = init(file_name)
    partitions_indexes = run(partition_size, in_las_data, point_count, m_out_views)
    print('Partitions computed, adding buffer and saving to disc...')
    write_part(in_las_data, file_name, out_dir, partitions_indexes, buffer_size)
    print('Partitions have been written.')


def write_part(in_file, origfname, out_dir, partitions, buffer):
    for i, part in enumerate(partitions):
        fname = re.sub(r'\\', '/', origfname).split('/')[-1].split('.')[0] + \
                '-' + str(i).zfill(4) + \
                '.las' if '\\' in origfname else origfname.split('/')[-1].split('.')[0] + \
                                                 '-' + str(i).zfill(4) + \
                                                 '.las'
        do_partitions(in_file, fname, out_dir, part, buffer)


def do_partitions(in_las_data, fname, out_dir, partition, buffer):
    x_points, y_points = in_las_data.x, in_las_data.y
    out_las_data = laspy.LasData(in_las_data.header)
    out_las_data.points = in_las_data.points[partition]
    x_min, x_max = np.min(out_las_data.x), np.max(out_las_data.x)
    y_min, y_max = np.min(out_las_data.y), np.max(out_las_data.y)

    if buffer:

        limitX_bufflow = x_min - buffer
        limitX_buffupp = x_max + buffer

        limitY_bufflow = y_min - buffer
        limitY_buffupp = y_max + buffer

        values = np.logical_and(
            np.logical_and((limitX_bufflow <= x_points), (limitX_buffupp >= x_points)),
            np.logical_and((limitY_bufflow <= y_points), (limitY_buffupp >= y_points)))

        values_ind = np.where(values)
        keep_buffer_indices = np.setdiff1d(values_ind, partition)

        all_values = np.union1d(keep_buffer_indices, partition)
        withh = np.isin(all_values, keep_buffer_indices).astype(int)

        out_las_data.points = in_las_data.points[all_values]
        out_las_data.withheld = withh

        with open(out_dir + '/' + fname, 'wb') as f:
            out_las_data.write(f)

    else:
        out_las_data.points = in_las_data.points[partition]
        with open(out_dir + '/' + fname, 'wb') as f:
            out_las_data.write(f)

    return True
