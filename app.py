import datetime
import json
import os
import posixpath
import random


import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from models import Image, Label
from settings import Settings
from utilities import load_labels, get_unlabelled_images, get_classes, get_resource_path

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/images", StaticFiles(directory=Settings.DATA_SOURCE_ROOT), name="images")
app.mount("/static", StaticFiles(directory=get_resource_path("static")), name="static")
templates = Jinja2Templates(directory=get_resource_path("templates"))

labels_dict = load_labels()
unlabelled_images = get_unlabelled_images(labels_dict)


def store_labels(intermediate: bool = False):
    if intermediate:
        prefix = f"{int(datetime.datetime.now().timestamp())}-"
    else:
        prefix = ""
    with open(
        Settings.DATA_SOURCE_PATH.joinpath(prefix + Settings.LABEL_FILE_NAME), "w"
    ) as fid:
        json.dump(labels_dict, fid, indent=2)


def get_unlabelled_image():
    if unlabelled_images:
        return random.choice(unlabelled_images), len(unlabelled_images)
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
    next_image_uri = posixpath.join(Settings.DATA_SOURCE_ROOT, next_image)
    if num_remaining == 0:
        next_image_uri = "/static/lazy-cat.jpg"
    return Image(src=next_image_uri, numImagesRemaining=num_remaining)


@app.post("/label/", response_model=Label)
async def store_label(label: Label):
    directory, img_name = os.path.split(label.image)
    labels_dict[label.label].append(img_name)
    unlabelled_images.remove(img_name)
    store_labels()
    return label


@app.post("/label/checkpoint")
async def store_label_checkpoint():
    store_labels(intermediate=True)
    return {"status": "success"}


if __name__ == "__main__":
    uvicorn.run(app)
