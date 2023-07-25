import httpx
import io
from . import Ark
from pydantic import BaseModel, Field, validator
from PIL import Image as PILImage
from typing import Any, ClassVar, Literal, Union
from urllib.parse import urljoin
from .routes import IIIF_ENPOINT


class IIIFResource(BaseModel):
    ark: Union[Ark, str]

    def __init__(__pydantic_self__, **data: Any) -> None:
        super().__init__(**data)
        self = __pydantic_self__
        if isinstance(self.ark, str):
            self.ark = Ark.from_string(self.ark)

    @classmethod
    def from_url(cls, url: str) -> "IIIFResource":
        ark, *_ = url.rpartition("/")
        ark = Ark.from_string(ark)
        # FIXME Check that keeping only the first qualifier doesnt cause later problems.
        ark.qualifiers = ark.qualifiers[:1]
        return cls(ark=ark)

    def manifest(self, client: httpx.Client) -> Any:
        url = urljoin(IIIF_ENPOINT, f"{self.ark}/manifest.json")
        response = client.get(url)
        response.raise_for_status()
        return response.json()

    def info(self, client: httpx.Client) -> Any:
        url = urljoin(IIIF_ENPOINT, f"{self.ark}/info.json")
        response = client.get(url)
        response.raise_for_status()
        return response.json()

    def image(self, **params) -> "Image":
        return Image(endpoint=IIIF_ENPOINT, identifier=self.ark, **params)


class Image(BaseModel):
    FORMATS: ClassVar[str] = ["jpg", "tif", "png", "gif", "jp2", " pdf", "webp"]

    endpoint: str
    identifier: Union[str, Ark]
    region: str = Field(pattern=r"full|square|(pct:)?\d+,\d+,\d+,\d+", default="full")
    size: str = Field(pattern=r"full|max|\d+,|,\d+|pct:\d+|!?\d+,\d+", default="max")
    rotation: str = Field(pattern=r"!?\d{1,3}", default="0")
    quality: Literal["color", "gray", "bitonal", "default"] = "default"
    format: str = "jpg"

    @validator("identifier")
    def parse_identifier(cls, ark_or_str: Union[str, Ark]) -> Ark:
        if isinstance(ark_or_str, str):
            return Ark.from_string(ark_or_str)
        return ark_or_str

    @validator("format")
    def check_format(cls, format: str) -> str:
        assert format in Image.FORMATS
        return format

    @validator("rotation")
    def check_rotation(cls, rot_str: str) -> str:
        offset = int(rot_str.startswith("!"))
        theta = int(rot_str[offset:])
        assert 0 <= theta <= 360
        return rot_str

    def fetch(self, client: httpx.Client) -> PILImage:
        response = client.get(str(self))
        response.raise_for_status()
        return PILImage.open(io.BytesIO(response.content))

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
