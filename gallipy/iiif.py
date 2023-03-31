import httpx
import io
from ark import Ark
from pydantic import BaseModel, Field, validator
from PIL import Image as PILImage
from typing import Any, ClassVar, Literal, Union

GALLICA_IIIF = "https://gallica.bnf.fr/iiif"


class IIIF(BaseModel):
    endpoint: ClassVar[str] = GALLICA_IIIF
    ark: Union[Ark, str]

    def __init__(__pydantic_self__, **data: Any) -> None:
        super().__init__(**data)
        self = __pydantic_self__
        if isinstance(self.ark, str):
            self.ark = Ark.from_string(self.ark)

    @classmethod
    def from_url(cls, url: str):
        if not url.startswith(IIIF.endpoint):
            raise ValueError("URL does not match the current IIIF endpoint.")
        file_ext = ("json", "jpg", "tif", "png", "gif", "jp2", " pdf", "webp")
        if url.endswith(file_ext):
            ark, *_ = url.rpartition("/")
        else:
            ark = url
        args = {"ark": Ark.from_string(ark)}
        return cls(**args)

    def manifest(self, client: httpx.Client):
        query = f"{self.endpoint}/{self.ark}/manifest.json"
        r = client.get(query)
        r.raise_for_status()
        return r.json()

    def info(self, client: httpx.Client):
        query = f"{self.endpoint}/{self.ark}/info.json"
        r = client.get(query)
        r.raise_for_status()
        return r.json()

    def image(self, **params):
        return Image(endpoint=self.endpoint, identifier=self.ark, **params)


class Image(BaseModel):
    endpoint: str
    identifier: Union[str, Ark]
    region: str = Field(regex=r"full|square|(pct:)?\d+,\d+,\d+,\d+", default="full")
    size: str = Field(regex=r"full|max|\d+,|,\d+|pct:\d+|!?\d+,\d+", default="max")
    rotation: str = Field(regex=r"!?\d{1,3}", default="0")
    quality: Literal["color", "gray", "bitonal", "default"] = "default"
    format: Literal["jpg", "tif", "png", "gif", "jp2", " pdf", "webp"] = "jpg"

    @validator("identifier")
    def parse_ark(cls, v):
        if isinstance(v, str):
            return Ark.from_string(v)
        return v

    @validator("rotation")
    def check_rotation(cls, v):
        offset = int(v.startswith("!"))
        theta = int(v[offset:])
        assert 0 <= theta <= 360
        return v

    def fetch(self, client: httpx.Client):
        r = client.get(str(self))
        r.raise_for_status()
        im = PILImage.open(io.BytesIO(r.content))
        return im

    def __str__(self) -> str:
        parts = [
            self.endpoint,
            str(self.identifier),
            self.region,
            self.size,
            self.rotation,
            self.quality,
        ]
        url = "/".join(parts) + f".{self.format}"
        return url


# with httpx.Client() as c:
#     i = IIIF.from_url("https://gallica.bnf.fr/iiif/ark:/12148/btv1b90017179/f15/info.json")
#     im = i.image(quality="gray").fetch(c)
#     im.show()
