from pydantic import BaseModel, Field


class Label(BaseModel):
    label: str = Field()
    image: str = Field()


class Image(BaseModel):
    src: str = Field()
    num_images_remaining: int = Field(alias="numImagesRemaining")
