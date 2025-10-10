#!/usr/bin/env python3
"""
将若干 GeoTIFF 合并成一个 VRT 再转成 GeoTIFF（GDAL 实现，内存友好）
改进版本：修复分辨率解析问题，增加错误处理
"""
import pathlib
import subprocess
import tempfile
import os
import re


def get_resolution(tif_path):
    """获取栅格分辨率（改进版，更健壮的解析方式）"""
    try:
        info = subprocess.run(['gdalinfo', str(tif_path)],
                              capture_output=True,
                              text=True,
                              check=True).stdout

        # 使用正则表达式提取分辨率
        for line in info.split('\n'):
            if 'Pixel Size' in line:
                # 匹配格式如: "Pixel Size = (0.050000000000000,-0.050000000000000)"
                match = re.search(r'$([-+]?\d*\.\d+),\s*([-+]?\d*\.\d+)$', line)
                if match:
                    x_res = abs(float(match.group(1)))
                    y_res = abs(float(match.group(2)))
                    return x_res, y_res

        # 如果正则匹配失败，尝试更宽松的解析方式
        for line in info.split('\n'):
            if 'Pixel Size' in line:
                parts = line.split('=')[-1].strip().strip('()').split(',')
                if len(parts) >= 2:
                    x_res = abs(float(parts[0].strip()))
                    y_res = abs(float(parts[1].strip().split(')')[0]))
                    return x_res, y_res

        raise ValueError(f"无法从gdalinfo输出中解析分辨率: {tif_path}")

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"执行gdalinfo失败: {e.stderr}") from e
    except (ValueError, IndexError, AttributeError) as e:
        raise ValueError(f"解析分辨率失败: {str(e)}") from e


def merge_rasters(tif_list, out_tif):
    """
    输入：tif_list = [Path, Path, ...]
    输出：out_tif = Path
    """
    if not tif_list:
        raise ValueError("输入文件列表为空")

    # 检查文件存在性
    tif_list = [pathlib.Path(p) for p in tif_list]
    for p in tif_list:
        if not p.exists():
            raise FileNotFoundError(f"输入文件不存在: {p}")

    out_tif = pathlib.Path(out_tif)
    out_tif.parent.mkdir(parents=True, exist_ok=True)

    # 获取基准分辨率（取第一个文件）
    try:
        x_res, y_res = get_resolution(tif_list[0])
    except Exception as e:
        raise RuntimeError(f"获取分辨率失败: {str(e)}") from e

    # 用 VRT 合并，再转 GeoTIFF（压缩）
    with tempfile.NamedTemporaryFile(suffix='.vrt', delete=False) as tmp:
        vrt_path = tmp.name

    try:
        # 构建VRT（添加-tr参数）
        cmd = [
                  'gdalbuildvrt',
                  '-q',
                  '-resolution', 'user',
                  '-tr', str(x_res), str(y_res),  # 必须与-tap配合使用
                  '-tap',  # 可选对齐参数
                  vrt_path
              ] + [str(p) for p in tif_list]
        subprocess.run(cmd, check=True)

        # 转换为GeoTIFF
        cmd = [
            'gdal_translate',
            '-q',
            '-co', 'COMPRESS=LZW',
            '-co', 'TILED=YES',
            '-co', 'BIGTIFF=IF_SAFER',
            vrt_path,
            str(out_tif)
        ]
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"GDAL命令执行失败: {e.cmd}\n错误输出: {e.stderr}") from e
    finally:
        if os.path.exists(vrt_path):
            try:
                os.unlink(vrt_path)
            except OSError:
                pass

    return out_tif


if __name__ == '__main__':
    # 示例用法
    import sys

    if len(sys.argv) < 3:

        sys.exit(1)

    output_file = sys.argv[1]
    input_files = sys.argv[2:]

    try:
        merge_rasters(input_files, output_file)
        print(f"成功合并 {len(input_files)} 个文件到 {output_file}")
    except Exception as e:
        print(f"错误: {str(e)}", file=sys.stderr)
        sys.exit(1)