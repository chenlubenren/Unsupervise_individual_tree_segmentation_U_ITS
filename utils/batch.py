import pathlib
from pipeline.step1_filter import run_step1
from pipeline.step2_height import run_step2
from pipeline.step3_segment import run_step3
from pipeline.step4_filter_feature import run_step4
from pipeline.step5_watershed import run_step5


def process_one_las(las_path, out_dir, cfg, start, end):
    out_dir = pathlib.Path(out_dir)
    outputs = {
        1: out_dir / 'ground.las',
        2: out_dir / 'DEM.tif',
        3: out_dir / 'CHM_SEGMENTS.tif',
        4: out_dir / 'FILTERED_MASK.tif',
        5: out_dir / 'INDIVIDUAL_TREE.tif',
    }
    if start <= 1 and end >= 1:
        run_step1(las_path, out_dir, cfg['STEP1'])
    if start <= 2 and end >= 2:
        run_step2(out_dir, cfg['STEP2'], las_path)
    if start <= 3 and end >= 3:
        run_step3(out_dir, cfg['STEP3'])
    if start <= 4 and end >= 4:
        run_step4(out_dir, cfg['STEP4'])
    if start <= 5 and end >= 5:
        run_step5(out_dir, cfg['STEP5'])