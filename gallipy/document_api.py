from enum import Enum
import io
from typing import Union
from PyPDF2 import PdfReader
from bs4 import BeautifulSoup
from PIL import Image as PILImage
import httpx
from pydantic import BaseModel, validator
from urllib.parse import urljoin
from . import Ark
from .routes import gallica_route_to, gallica_route_to_services


class MarkupFormat(Enum):
    HTML = None
    XML = "lxml"


class Service(BaseModel):
    ark: Union[str, Ark]

    @validator("ark", pre=True)
    def init_ark(cls, ark: Union[str, Ark]):
        if isinstance(ark, str):
            return Ark.from_string(ark)
        return ark.copy()

    def fetch(
        self,
        url,
        params,
        client: httpx.Client,
        format: MarkupFormat = MarkupFormat.HTML,
    ) -> BeautifulSoup:
        r = client.get(url, params=params)
        print(url)
        r.raise_for_status()
        return BeautifulSoup(r.text, features=format.value)


class Issues(Service):
    _endpoint: str = gallica_route_to_services("Issues")

    @validator("ark", pre=True)
    def init_ark(cls, ark: Union[str, Ark]):
        ark = super().init_ark(ark)
        date_qualifier = "date"
        if not ark.identifier().endswith(date_qualifier):
            ark.qualifiers.append(date_qualifier)
        return ark

    def fetch(self, client: httpx.Client, date: int = None) -> BeautifulSoup:
        params = {"ark": self.ark, "date": date}
        return super().fetch(
            self._endpoint,
            params,
            client,
            MarkupFormat.XML,
        )


class OAIRecord(Service):
    _endpoint: str = gallica_route_to_services("OAIRecord")

    def fetch(self, client: httpx.Client) -> BeautifulSoup:
        params = {"ark": self.ark.name}
        return super().fetch(self._endpoint, params, client, MarkupFormat.XML)


class Pagination(Service):
    _endpoint: str = gallica_route_to_services("Pagination")

    def fetch(self, client: httpx.Client) -> BeautifulSoup:
        params = {"ark": self.ark.name}
        return super().fetch(self._endpoint, params, client, MarkupFormat.XML)


class ImageQualifier(Enum):
    THUMBNAIL = "thumbnail"
    LOWRES = "lowres"
    MEDRES = "medres"
    HIGHRES = "highres"


class Image(Service):
    _endpoint = None

    def model_post_init(self):
        self._endpoint = gallica_route_to(self.ark, "/")

    def fetch(self, client: httpx.Client, quality: ImageQualifier) -> PILImage:
        url = urljoin(self._endpoint, quality)
        r = client.get(url)
        r.raise_for_status()
        return PILImage.open(io.BytesIO(r.content))


class ContentSearch(Service):
    _endpoint: str = gallica_route_to_services("ContentSearch")

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
        return super().fetch(self._endpoint, params, client, MarkupFormat.XML)


class Toc(Service):
    _endpoint: str = gallica_route_to_services("Toc")

    def fetch(self, client: httpx.Client) -> BeautifulSoup:
        params = {"ark": self.ark}
        return super().fetch(self._endpoint, params, client, MarkupFormat.XML)


class TexteBrut(Service):
    _endpoint = None

    def model_post_init(self):
        self._endpoint = gallica_route_to(self.ark)
        self._endpoint += ".texteBrut"

    def fetch(self, client: httpx.Client):
        r = client.get(self._endpoint)
        r.raise_for_status()
        return r.content


class RequestDigitalElement(Service):
    _endpoint = None

    def model_post_init(self):
        self._endpoint = gallica_route_to(self.ark, "/", "RequestDigitalElement")

    def fetch(self, client: httpx.Client, deb: int):
        params = {"O": self.ark.name, "DEB": deb, "E": "ALTO"}
        return super().fetch(self._endpoint, params, client, MarkupFormat.XML)


class PDF(Service):
    _endpoint = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._endpoint = gallica_route_to(self.ark, "/")

    def fetch(self, client: httpx.Client, _from: int, n: int = None):
        template = "f{a}n{n}.pdf" if n else "f{a}.pdf"
        url = urljoin(self._endpoint, template.format(a=_from, n=n))
        print(url)
        r = client.get(url)
        r.raise_for_status()
        return PdfReader(io.BytesIO(r.content))
