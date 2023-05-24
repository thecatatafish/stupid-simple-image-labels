import datetime
import json
import os
import posixpath
import random

import uvicorn
from fastapi import FastAPI, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from models import Classes, Image, Label
from settings import Settings
from utilities import get_classes, get_resource_path, get_unlabelled_images, load_labels

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


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print(exc.body, exc.errors())
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )


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
        "label-images.html",
        {
            "request": request,
        },
    )


@app.get("/classes/", response_model=Classes)
def fetch_classes():
    return {"class_names": get_classes()}


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


@app.get("/view")
async def view_labelled_images(request: Request):
    return templates.TemplateResponse(
        "view-labels.html",
        {
            "request": request,
        },
    )


@app.get("/label/")
async def get_labelled_images():
    return labels_dict


@app.delete("/label/")
async def remove_label(label: Label):
    images = labels_dict.get(label.label, [])
    if images and label.image in images:
        images.remove(label.image)
        store_labels()
        unlabelled_images.append(label.image)
        return {"status": "success"}
    raise HTTPException(status_code=404, detail="Item not found")


if __name__ == "__main__":
    uvicorn.run(app)
