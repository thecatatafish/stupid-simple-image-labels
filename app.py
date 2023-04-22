import datetime
import json
import os
import pathlib
import posixpath
import random
import shutil
import sys

import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from models import Image, Label


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


DATA_SOURCE_ROOT = "./images"

data_source_path = pathlib.Path(DATA_SOURCE_ROOT)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/images", StaticFiles(directory=DATA_SOURCE_ROOT), name="images")
app.mount("/static", StaticFiles(directory=resource_path("static")), name="static")

templates = Jinja2Templates(directory=resource_path("templates"))


def get_classes():
    return [
        str(subdir.name) for subdir in data_source_path.iterdir() if subdir.is_dir()
    ]


labels_dict = {c: [] for c in get_classes()}
unlabelled = [str(file.name) for file in data_source_path.iterdir() if file.is_file()]

def store_labels(intermediate: bool=False):
    if intermediate:
        suffix = f"-{int(datetime.datetime.now().timestamp())}"
    else:
        suffix = ""
    with open(data_source_path.joinpath(f"labels{suffix}.json"), "w") as fid:
        json.dump(labels_dict, fid)


def get_unlabelled_image():
    # images = [str(file.name) for file in data_source_path.iterdir() if file.is_file()]
    if unlabelled:
        return random.choice(unlabelled), len(unlabelled)
    return "", 0


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "buttons": get_classes(),
        },
    )


@app.get("/image/", response_model=Image)
def get_next_image():
    next_image, num_remaining = get_unlabelled_image()
    next_image_uri = posixpath.join(DATA_SOURCE_ROOT, next_image)
    if num_remaining == 0:
        next_image_uri = "/static/lazy-cat.jpg"
    return Image(src=next_image_uri, numImagesRemaining=num_remaining)


@app.post("/label/", response_model=Label)
async def store_label(label: Label):
    directory, img_name = os.path.split(label.image)
    labels_dict[label.label].append(img_name)
    unlabelled.remove(img_name)
    store_labels()
    print(labels_dict)
    print(unlabelled)
    return label

@app.post("/label/checkpoint")
async def store_label_checkpoint():
    store_labels(intermediate=True)
    return {"status": "success"}


if __name__ == "__main__":
    uvicorn.run(app)
