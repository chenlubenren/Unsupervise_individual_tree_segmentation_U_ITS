# utils/log.py
import logging
import sys
import pathlib
from typing import Union


def init_logger(root: Union[str, pathlib.Path]):
    root = pathlib.Path(root)
    root.mkdir(parents=True, exist_ok=True)
    logfile = root / "pipeline.log"

    logger = logging.getLogger("pipeline")
    logger.setLevel(logging.INFO)
    if logger.handlers:          # 防止重复初始化
        return logger

    fmt = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")

    fh = logging.FileHandler(logfile, encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    # ---------- 控制台输出已移除 ----------
    # ch = logging.StreamHandler(sys.stdout)
    # ch.setFormatter(fmt)
    # logger.addHandler(ch)
    # ------------------------------------

    # # ---------- 捕获 print ----------
    # class PrintToLog:
    #     def write(self, buf: str):
    #         for line in buf.rstrip().splitlines():
    #             logger.info(line.rstrip())
    #
    #     def flush(self):
    #         pass
    #
    # sys.stdout = PrintToLog()
    # sys.stderr = PrintToLog()

    return logger