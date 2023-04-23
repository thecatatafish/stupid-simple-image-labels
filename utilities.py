import json
import os
import sys
from typing import Dict, List

from settings import Settings


def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def get_classes():
    return [
        str(subdir.name)
        for subdir in Settings.DATA_SOURCE_PATH.iterdir()
        if subdir.is_dir()
    ]


def load_labels():
    Settings.DATA_SOURCE_PATH.joinpath(f"labels.json")
    label_file_uri = Settings.DATA_SOURCE_PATH.joinpath(Settings.LABEL_FILE_NAME)
    if os.path.exists(label_file_uri):
        with open(label_file_uri, "r") as fid:
            return json.load(fid)
    return {c: [] for c in get_classes()}


def get_unlabelled_images(current_labels: Dict[str, List[str]]):
    unlabelled = []
    labelled = [item for sublist in current_labels.values() for item in sublist]
    for f in Settings.DATA_SOURCE_PATH.iterdir():
        if (
            f.is_file()
            and f.name.endswith((".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif"))
            and f.name not in labelled
        ):
            unlabelled.append(f.name)
    return unlabelled
