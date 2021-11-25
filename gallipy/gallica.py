from ark import Ark
from dataclasses import dataclass
from parsers import XmlParser, IssuesParser
from bs4 import BeautifulSoup
import bs4
from PIL import Image
from io import BytesIO
from enum import Enum
from pathlib import Path
import datetime
import requests
import xml
import warnings

GALLICA = "https://gallica.bnf.fr"

def service(verb):
    return f"{GALLICA}/services/{verb}"

@dataclass
class Urls:
    
    base = GALLICA
    
    issues = service("Issues")
    oairecord = service("OAIRecord")
    pagination = service("Pagination")
    contentsearch = service("ContentSearch")
    toc = service("Toc")
    requestdigitalelement=f"{base}/RequestDigitalElement"

    @classmethod
    def image(cls, ark: Ark, page:int, resolution: str ):
        assert resolution in ["thumbnail","lowres","medres","highres"]
        return f"{cls.base}/{ark}/f{page}.{resolution}"

    @classmethod
    def textebrut(cls, ark):
        return f"{cls.base}/{ark}.texteBrut"

def content_or_fail(response, f):
    if response.status_code == 200:
        return f(response.content)
    response.raise_for_status()


@dataclass
class ContentSearch:
    query:str
    metadata:dict
    items:dict

    def __init__(self, query):
        self.query = query
    
    async def exec():
        ...  # Execute the query and fill this ContentSearch in a separate thread

    @classmethod
    def from_xml(cls, raw_xml):     
        parser = ContentSearchParser(raw_xml)
        cs = cls(parser.query())
        cs.items = list(parser.items())
        cs.metadata = parser.metadata()
        cs._parser = parser
        return cs

@dataclass
class Issue:
    ark: Ark
    metadata: dict
    value: str

@dataclass
class Issues:

    parent_ark: Ark
    metadata: dict
    years: list
    issues: list

    @classmethod
    def from_xml(cls, raw_xml):
        parser = IssuesParser(raw_xml)
        md = parser.metadata()
        ark = md["parentArk"]
        years = parser.years()
        issues = parser.issues()
        return cls(ark, md, years, issues)

@dataclass
class Document:

    ark: Ark
    
    def __init__(self, ark_):
        if isinstance(ark_, str):
            self.ark = Ark.from_string(ark_)
        elif isinstance(ark_, Ark):
            self.ark = ark_
        else:
            raise ValueError(ark_, "is not a string or an Ark object.")

    def issues(self, date:int=None, raw:bool=False):
        if self.ark.qualifier == "date":
            params={"ark":self.ark}
            if date:
                params["date"] = date
            handler = XmlParser if raw else Issues.from_xml
            response = requests.get(Urls.issues, params=params)    
            return content_or_fail(response, handler)
        raise ValueError("Service Issues requires an ARK with the qualifier `date`.")

    def oairecord(self):
        return self.ark_query(Urls.issues, self.ark, BeautifulSoup)

    def pagination(self):
        short = self.ark.name
        return self.ark_query(Urls.issues, short, BeautifulSoup)

    def image(self, page: int, qualifier: str="thumbnail"):
        # Only 4 values are valid for the image resolution selector
        valid_resolutions = ["thumbnail","lowres","medres","highres"]
        if qualifier not in valid_resolutions:
            raise ValueError(f"{qualifier} must be one of {valid_resolutions}")

        url = Urls.image(self.ark, page, qualifier)
        response = requests.get(url)
        return content_or_fail(response, lambda c: Image.open(BytesIO(c)))


    def contentsearch(self, query:str, page:int=None, start_result:int=1, index_only=False, raw=False):
        params={"ark":self.ark.name, "query": query}
        if not index_only or page:
            params.update({
                "startResult": start_result,
                "page": page
            })

        handler = BeautifulSoup if raw else ContentSearch.from_xml
        response = requests.get(Urls.contentsearch, params=params)
        return content_or_fail(response, handler)

    def toc(self):
        return self.ark_query(Urls.toc, self.ark, BeautifulSoup)

    def textebrut(self):  # TODO DEBUG BUT SO SLOWWWWWWWWWWWWw
        url = Urls.textebrut(self.ark)
        return self.ark_query(url, self.ark, lambda c: BeautifulSoup(c,features="lxml"))

    def requestdigitalelement(self, deb:int, e:str="ALTO"):
        params={"O":self.ark.name, "Deb":deb, "E":e}
        response = requests.get(Urls.requestdigitalelement, params=params)
        return content_or_fail(response, BeautifulSoup)


# Issues
print(Document("ark:/12148/cb34431794k/date").issues())
#xmlstr = minidom.parseString(ET.tostring(record)).toprettyxml(indent="    ")

