# io.py
import laspy
import numpy as np
import open3d as o3d

def read_las_xyz(path):
    las = laspy.read(path)
    return np.vstack((las.x, las.y, las.z)).T.copy(), las

def save_pcd_as_las(pcd, out_path, template):
    las = laspy.create(point_format=template.header.point_format,
                       file_version=template.header.version)
    las.header.offsets = template.header.offsets
    las.header.scales  = template.header.scales
    xyz = np.asarray(pcd.points)
    las.x, las.y, las.z = xyz[:,0], xyz[:,1], xyz[:,2]
    las.write(str(out_path))