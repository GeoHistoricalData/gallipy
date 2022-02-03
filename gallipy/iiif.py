from io import BytesIO
from PIL import Image
from io import BytesIO
from dataclasses import dataclass
import json
from gallipy.parsers import XmlParser
from helpers import sync_get
from ark import Ark
from typing import Tuple, Union
import routes


@dataclass
class IIIF:

    ark: Ark

    def __init__(self, ark_):
        if isinstance(ark_, str):
            self.ark = Ark.parse(ark_)
        elif isinstance(ark_, Ark):
            self.ark = ark_
        else:
            raise ValueError(ark_, "is not a string or an Ark object.")

    def image_requests(
        self,
        vue: int,
        region: Tuple[int, int, int, int],
        size: Union[Tuple[int, int], str] = "full",
        rotation: int = 0,
        quality: str = "native",
        format="jpg",
    ):
        if isinstance(size, tuple):
            size = ",".join([str(s) for s in size])
        elif size != "full":
            raise ValueError("Size must be a 2-tuple or 'full'.")
        region = ",".join([str(r) for r in region])
        vue = f"f{vue}"

        url = routes.image_requests(
            self.ark, vue, region, size, rotation, quality, format
        )
        return sync_get(url, lambda c: Image.open(BytesIO(c)))

    def image_information(self, vue: int):
        vue = f"f{vue}"
        url = routes.image_information(self.ark, vue)
        return sync_get(url, json.loads)

    def presentation(self):
        url = routes.presentation(self.ark)
        return sync_get(url, json.loads)
