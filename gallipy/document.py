from enum import Enum
import io
from typing import Any, Literal, Union
from bs4 import BeautifulSoup
from PIL import Image as PILImage
import httpx
from pydantic import BaseModel, validator

from ark import Ark

GALLICA = "https://gallica.bnf.fr"
ENDPOINT_ISSUES = f"{GALLICA}/services/Issues"
ENDPOINT_OAIRecord = f"{GALLICA}/services/OAIRecord"
ENDPOINT_Pagination = f"{GALLICA}/services/Pagination"
ENDPOINT_Image = GALLICA
ENDPOINT_ContentSearch = f"{GALLICA}/services/ContentSearch"
ENDPOINT_Toc = f"{GALLICA}/services/Toc"
ENDPOINT_OCR = f"{GALLICA}/RequestDigitalElement"


def copyparse(ark: Union[str, Ark]) -> Ark:
    if isinstance(ark, Ark):
        return ark.copy()
    elif isinstance(ark, str):
        return Ark.from_string(ark)
    else:
        raise TypeError(f"{ark} is not an ARK.")


class MarkupFormat(Enum):
    HTML = None
    XML = "lxml"


class Service(BaseModel):
    ark: Ark

    @validator("ark", pre=True)
    def init_ark(cls, ark: Union[str, Ark]):
        return copyparse(ark)

    def fetch_markup(
        self,
        url,
        params,
        client: httpx.Client,
        format: MarkupFormat = MarkupFormat.HTML,
    ):
        r = client.get(url, params=params)
        r.raise_for_status()
        return BeautifulSoup(r.text, features=format.value)


class Issues(Service):
    @validator("ark", pre=True)
    def init_ark(cls, ark: Union[str, Ark]):
        ark = super().init_ark(ark)
        if not ark.identifier().endswith("date"):
            ark.qualifiers.append("date")
        return ark

    def get(self, client: httpx.Client, date: int = None):
        return self.fetch_markup(
            ENDPOINT_ISSUES,
            {"ark": self.ark, "date": date},
            client,
            format=MarkupFormat.XML,
        )


class OAIRecord(Service):
    def get(self, client: httpx.Client):
        return self.fetch_markup(
            ENDPOINT_OAIRecord, {"ark": self.ark.name}, client, format=MarkupFormat.XML
        )


class Pagination(Service):
    def get(self, client: httpx.Client):
        return self.fetch_markup(
            ENDPOINT_Pagination, {"ark": self.ark.name}, client, format=MarkupFormat.XML
        )


class ImageQualifier(Enum):
    THUMBNAIL = "thumbnail"
    LOWRES = "lowres"
    MEDRES = "medres"
    HIGHRES = "highres"


class Image(Service):
    def get(self, client: httpx.Client, qualifier: ImageQualifier):
        url = f"{ENDPOINT_Image}/{self.ark}/{qualifier}"
        r = client.get(url)
        r.raise_for_status()
        return PILImage.open(io.BytesIO(r.content))


class ContentSearch(Service):
    def get(
        self,
        client: httpx.Client,
        query: str,
        page: int = None,
        startResult: int = None,
    ):
        params = {
            "ark": self.ark.name,
            "query": query,
            "page": page,
            "startResult": startResult,
        }
        params = {k: v for k, v in params.items() if v}
        return self.fetch_markup(
            ENDPOINT_ContentSearch, params, client, format=MarkupFormat.XML
        )


class Toc(Service):
    def get(self, client: httpx.Client):
        return self.fetch_markup(
            ENDPOINT_Toc, {"ark": self.ark}, client=client, format=MarkupFormat.XML
        )


class Text(Service):
    def get_plaintext(self, client: httpx.Client):
        url = f"{GALLICA}/{self.ark}/texteBrut"
        r = client.get(url)
        r.raise_for_status()
        return r.content

    def get_ocrtext(self, client: httpx.Client, deb: int):
        params = {"O": self.ark.name, "E": "ALTO", "Deb": deb}
        return self.fetch_markup(
            ENDPOINT_OCR, params=params, client=client, format=MarkupFormat.XML
        )


with httpx.Client(timeout=10) as c:
    # i = Issues(ark="ark:/12148/cb32798952c").get(c, date=1937)
    # print(i)
    # i = OAIRecord(ark="ark:/12148/cb32798952c").get(c)
    # print(i)
    i = Text(ark="12148/bpt6k5619759j").get_ocrtext(c, deb=3)
    print(i)
