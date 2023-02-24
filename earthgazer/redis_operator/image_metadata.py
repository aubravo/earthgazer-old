from pydantic import BaseModel


class BandMetadata(BaseModel):
    ...


class ImageMetadata(BaseModel):
    band_metadata: list[BandMetadata]
