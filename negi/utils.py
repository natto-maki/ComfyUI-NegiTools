import os
import glob
import re


def get_directory(directory: str) -> str:
    base_path = os.path.abspath(__file__)
    for _ in range(4):
        base_path = os.path.dirname(base_path)
    abs_path = os.path.abspath(os.path.join(base_path, directory))
    os.makedirs(abs_path, exist_ok=True)
    return abs_path


def find_next_index(directory: str, glob_pattern="out.??????.png", re_pattern=r"out\.(\d{6})\.png") -> int:
    next_index = 0
    files = glob.glob(os.path.join(directory, glob_pattern))
    for file in files:
        r = re.match(re_pattern, os.path.basename(file))
        if r is None:
            continue
        next_index = max(next_index, int(r.group(1)) + 1)
    return next_index
