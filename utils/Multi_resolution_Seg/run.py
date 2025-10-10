#!/usr/bin/env python3
import os
import sys
import subprocess
import numpy as np
from osgeo import gdal
from rasterio.rio.options import resolution_opt
from tqdm import tqdm

def multi_resolution_seg(src_tif: str,
                         seg_tif: str,
                         scale: float = 45,
                         shape_weight: float = 0.2,
                         color_weight: float = 0.9,
                         threshold: float = 0.5):

    # 当前脚本所在目录
    exe_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'main.exe')

    # 中间文件名
    dst_tif = os.path.join(os.path.dirname(src_tif), 'CHM_zero.tif')
    RGB_tif = os.path.splitext(src_tif)[0] + '_zeroRGB.tif'

    # ---------- 1. 预处理：NoData → 0 ----------
    ds = gdal.Open(src_tif, gdal.GA_ReadOnly)
    if ds is None:
        raise RuntimeError(f'无法打开 {src_tif}')

    drv = gdal.GetDriverByName('GTiff')
    out_ds = drv.CreateCopy(dst_tif, ds, strict=0)
    band = out_ds.GetRasterBand(1)
    nodata = band.GetNoDataValue()
    if nodata is not None:
        arr = band.ReadAsArray()
        arr[arr == nodata] = 0
        band.WriteArray(arr)
    band.DeleteNoDataValue()
    band.FlushCache()
    out_ds = band = None

    # ---------- 2. 调用外部程序（静默） ----------
    cmd = [exe_path, dst_tif, '', '', seg_tif, str(scale), str(shape_weight), str(color_weight)]
    if sys.platform == "win32":
        DETACHED = subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW
        subprocess.run(cmd, creationflags=DETACHED, check=True)
    else:
        subprocess.run(cmd, check=True)

    # ---------- 3. 后处理 ----------
    print("开始后处理")
    zero_ds = gdal.Open(dst_tif, gdal.GA_ReadOnly)
    zero_arr = zero_ds.GetRasterBand(1).ReadAsArray()

    seg_ds = gdal.Open(seg_tif, gdal.GA_Update)
    seg_band = seg_ds.GetRasterBand(1)
    seg_arr = seg_band.ReadAsArray()

    labels = np.unique(seg_arr)
    labels = labels[labels != seg_band.GetNoDataValue()]

    for lbl in tqdm(labels):
        mask_lbl = (seg_arr == lbl)
        chm_vals = zero_arr[mask_lbl]
        if chm_vals.size == 0:
            continue
        if np.mean(chm_vals) < threshold:
            seg_arr[mask_lbl] = seg_band.GetNoDataValue()


    # ---------- 4. 清理中间文件 ----------
    for tmp in (dst_tif, RGB_tif):
        if os.path.isfile(tmp):
            os.remove(tmp)

# ----------------- 示例调用 -----------------
if __name__ == '__main__':
    multi_resolution_seg(
        src_tif='CHM.tif',
        seg_tif='CHM_SEGMENTS.tif',
        scale=45,
        shape_weight=0.2,
        color_weight=0.9,
        threshold=0.5
    )