from typing import Annotated, Literal, Optional, Tuple, Union
import regex

# from PIL import Image as PILImage
from pydantic import BaseModel, Field, ValidationError, validator
from ark import Ark


class Image(BaseModel):
    endpoint: str
    # Identifier
    identifier: Union[str, Ark]
    # Request parameters
    region: str = Field(regex=r"full|square|(pct:)?\d+,\d+,\d+,\d+", default="full")
    size: str = Field(regex=r"full|max|\d+,|,\d+|pct:\d+|!?\d+,\d+", default="max")
    rotation: str = Field(regex=r"!?\d{1,3}", default="0")
    quality: Literal["color", "gray", "bitonal", "default"] = "default"
    format: Literal["jpg", "tif", "png", "gif", "jp2", " pdf", "webp"] = "jpg"

    @validator("identifier")
    def parse_ark(cls, v):
        if isinstance(v, str):
            v = Ark.from_string(v)
        return v

    @validator("rotation")
    def check_rotation(cls, v):
        shift = int(v.startswith("!"))
        theta = int(v[shift:])
        assert 0 <= theta <= 360
        return v


i = Image(identifier="884eaze/12354", region="10,22,333,10", rotation="!0")
print(i)

# scheme: str
# server: str
# prefix: str
# identifier: Union[str, Ark]
# region: str = Field(
#     regex="(full|square|(?:pct:)?\d+,\d+,\d+,\d+)",
# )
# size: str
# rotation: str
# quality: str
# format: str

# @validator("region")
# def validate_param_region(cls, reg):
#     clean = regex.sub(r"\s", "", reg.lower().strip())
#     region_rgx = r"(full|square|(?:pct:)?\d+,\d+,\d+,\d+)"
#     if not regex.match(region_rgx, reg):
#         raise ValueError(f'Not a valid IIIF region: "{reg}"')
#     return clean


# @dataclass
# class IIIF:

#     ark: Ark

#     def __init__(self, ark_):
#         if isinstance(ark_, str):
#             self.ark = Ark.parse(ark_)
#         elif isinstance(ark_, Ark):
#             self.ark = ark_
#         else:
#             raise ValueError(ark_, "is not a string or an Ark object.")

#     def image_requests(
#         self,
#         vue: int,
#         region: Tuple[int, int, int, int],
#         size: Union[Tuple[int, int], str] = "full",
#         rotation: int = 0,
#         quality: str = "native",
#         format="jpg",
#     ):
#         if isinstance(size, tuple):
#             size = ",".join([str(s) for s in size])
#         elif size != "full":
#             raise ValueError("Size must be a 2-tuple or 'full'.")
#         region = ",".join([str(r) for r in region])
#         vue = f"f{vue}"

#         url = routes.image_requests(
#             self.ark, vue, region, size, rotation, quality, format
#         )
#         return sync_get(url, lambda c: Image.open(BytesIO(c)))

#     def image_information(self, vue: int):
#         vue = f"f{vue}"
#         url = routes.image_information(self.ark, vue)
#         return sync_get(url, json.loads)

#     def presentation(self):
#         url = routes.presentation(self.ark)
#         return sync_get(url, json.loads)
