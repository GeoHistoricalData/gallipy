from enum import Enum
import io
from typing import Union
from bs4 import BeautifulSoup
from PIL import Image as PILImage
import httpx
from pydantic import BaseModel, validator
from urllib.parse import urljoin
from ark import Ark

GALLICA = "https://gallica.bnf.fr"


class MarkupFormat(Enum):
    HTML = None
    XML = "lxml"


class Service(BaseModel):
    ark: Ark

    @validator("ark", pre=True)
    def init_ark(cls, ark: Union[str, Ark]):
        if isinstance(ark, str):
            return Ark.from_string(ark)
        return ark.copy()

    def fetch_document(
        self,
        url,
        params,
        client: httpx.Client,
        format: MarkupFormat = MarkupFormat.HTML,
    ) -> BeautifulSoup:
        r = client.get(url, params=params)
        r.raise_for_status()
        return BeautifulSoup(r.text, features=format.value)


class Issues(Service):
    _endpoint: str = urljoin(GALLICA, "service/Issues")

    @validator("ark", pre=True)
    def init_ark(cls, ark: Union[str, Ark]):
        ark = super().init_ark(ark)
        date_qualifier = "date"
        if not ark.identifier().endswith(date_qualifier):
            ark.qualifiers.append(date_qualifier)
        return ark

    def fetch(self, client: httpx.Client, date: int = None) -> BeautifulSoup:
        params = {"ark": self.ark, "date": date}
        return self.fetch_document(
            self._endpoint,
            params,
            client,
            MarkupFormat.XML,
        )


class OAIRecord(Service):
    _endpoint: str = urljoin(GALLICA, "service/OAIRecord")

    def fetch(self, client: httpx.Client) -> BeautifulSoup:
        params = {"ark": self.ark.name}
        return self.fetch_document(self._endpoint, params, client, MarkupFormat.XML)


class Pagination(Service):
    _endpoint: str = urljoin(GALLICA, "service/Pagination")

    def fetch(self, client: httpx.Client) -> BeautifulSoup:
        params = {"ark": self.ark.name}
        return self.fetch_document(self._endpoint, params, client, MarkupFormat.XML)


class ImageQualifier(Enum):
    THUMBNAIL = "thumbnail"
    LOWRES = "lowres"
    MEDRES = "medres"
    HIGHRES = "highres"


class Image(Service):
    def fetch(self, client: httpx.Client, qualifier: ImageQualifier) -> PILImage:
        url = urljoin(GALLICA, f"{self.ark}/{qualifier}")
        r = client.get(url)
        r.raise_for_status()
        return PILImage.open(io.BytesIO(r.content))


class ContentSearch(Service):
    _endpoint: str = urljoin(GALLICA, "service/ContentSearch")

    def fetch(
        self,
        client: httpx.Client,
        query: str,
        page: int = None,
        startResult: int = None,
    ) -> BeautifulSoup:
        params = {
            "ark": self.ark.name,
            "query": query,
            "page": page,
            "startResult": startResult,
        }
        params = {k: v for k, v in params.items() if v}
        return self.fetch_document(self._endpoint, params, client, MarkupFormat.XML)


class Toc(Service):
    _endpoint: str = urljoin(GALLICA, "service/Toc")

    def fetch(self, client: httpx.Client) -> BeautifulSoup:
        params = {"ark": self.ark}
        return self.fetch_document(self._endpoint, params, client, MarkupFormat.XML)


class Text(Service):
    def fetch_plain(self, client: httpx.Client) -> str:
        url = urljoin(GALLICA, f"{self.ark}/texteBrut")
        r = client.get(url)
        r.raise_for_status()
        return r.content

    def fetch_ocr(self, client: httpx.Client, deb: int) -> BeautifulSoup:
        url = urljoin(GALLICA, "RequestDigitalElement")
        params = {"O": self.ark.name, "E": "ALTO", "Deb": deb}
        return self.fetch_document(url, params, client, MarkupFormat.XML)


with httpx.Client(timeout=10) as c:
    # i = Issues(ark="ark:/12148/cb32798952c").get(c, date=1937)
    # print(i)
    # i = OAIRecord(ark="ark:/12148/cb32798952c").get(c)
    # print(i)
    i = Text(ark="12148/bpt6k5619759j").get_ocrtext(c, deb=3)
    print(i)
