import os
import pathlib
from dataclasses import dataclass


@dataclass
class Settings:
    DATA_SOURCE_ROOT = os.getenv("DATA_SOURCE_ROOT", "./images")
    LABEL_FILE_NAME = "labels.json"
    DATA_SOURCE_PATH = pathlib.Path(DATA_SOURCE_ROOT)
