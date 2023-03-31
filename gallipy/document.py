# import routes
# from helpers import sync_get
# from dataclasses import dataclass
# from bs4 import BeautifulSoup
# from PIL import Image
# from io import BytesIO
# from ark import Ark
# from parsers import (
#     OAIRecordParser,
#     PaginationParser,
#     XmlParser,
#     IssuesParser,
#     ContentSearchParser,
#     html2text,
# )


from typing import Any, Union
from bs4 import BeautifulSoup
import httpx
from pydantic import BaseModel, validator

from ark import Ark

ENDPOINT_ISSUES = "https://gallica.bnf.fr/services/Issues"
ENDPOINT_OAIRecord = "https://gallica.bnf.fr/services/OAIRecord"
ENDPOINT_Pagination = "https://gallica.bnf.fr/services/Pagination"

def copyparse(ark: Union[str, Ark]) -> Ark:
    if isinstance(ark, Ark):
        return ark.copy()
    elif isinstance(ark, str):
        return Ark.from_string(ark)
    else:
        raise TypeError(f"{ark} is not an ARK.")


class Service(BaseModel):
    ark: Ark

    @validator("ark", pre=True)
    def init_ark(cls, ark: Union[str, Ark]):
        return copyparse(ark)

    def fetch_xml(self, url, params, client: httpx.Client):
        r = client.get(url, params=params)
        r.raise_for_status()
        return BeautifulSoup(r.text, features="xml")

class Issues(Service):

    @validator("ark", pre=True)
    def init_ark(cls, ark: Union[str, Ark]):
        ark = super().init_ark(ark)
        if not ark.identifier().endswith("date"):
            ark.qualifiers.append("date")
        return ark

    def get(self, client: httpx.Client, date: int = None):
        p = {"ark": self.ark, "date": date}
        return self.fetch_xml(ENDPOINT_ISSUES, p, client)

class OAIRecord(Service):
    def get(self, client: httpx.Client):
        p = {"ark": self.ark.name}
        return self.fetch_xml(ENDPOINT_OAIRecord, p, client)

class Pagination(Service):
    def get(self, client: httpx.Client):
        p = {"ark": self.ark.name}
        return self.fetch_xml(ENDPOINT_Pagination, p, client)


with httpx.Client() as c:
    i = Issues(ark="ark:/12148/cb32798952c").get(c, date=1937)
    print(i)
    i = OAIRecord(ark="ark:/12148/cb32798952c").get(c)
    print(i)
# @dataclass
# class Document:

#     ark: Ark

#     def __init__(self, ark_):
#         if isinstance(ark_, str):
#             self.ark = Ark.parse(ark_)
#         elif isinstance(ark_, Ark):
#             self.ark = ark_
#         else:
#             raise ValueError(ark_, "is not a string or an Ark object.")

#     def issues(self, date: int = None, raw: bool = False):
#         if self.ark.qualifier == "date":
#             params = {"ark": self.ark}
#             if date:
#                 params["date"] = date
#             handler = XmlParser if raw else Issues.from_xml
#             return sync_get(routes.issues, handler, params)
#         raise ValueError("Service Issues requires an ARK with the qualifier `date`.")

#     def oairecord(self, raw=False):
#         params = {"ark": self.ark.short()}
#         handler = XmlParser
#         return sync_get(routes.oairecord, handler, params)

#     def pagination(self, raw=False):
#         params = {"ark": self.ark.short()}
#         handler = XmlParser if raw else Pagination.from_xml
#         return sync_get(routes.pagination, handler, params)

#     def image(self, page: int, qualifier: str = "thumbnail"):
#         # Only 4 values are valid for the image resolution selector
#         valid_resolutions = ["thumbnail", "lowres", "medres", "highres"]
#         if qualifier not in valid_resolutions:
#             raise ValueError(f"{qualifier} must be one of {valid_resolutions}")

#         url = routes.image(self.ark, page, qualifier)
#         return sync_get(url, lambda c: Image.open(BytesIO(c)))

#     def contentsearch(
#         self,
#         query: str,
#         page: int = None,
#         start_result: int = 1,
#         index_only=False,
#         raw=False,
#     ):
#         params = {"ark": self.ark.short(), "query": query}
#         if not index_only or page:
#             params.update({"startResult": start_result, "page": page})

#         handler = XmlParser if raw else ContentSearch.from_xml
#         return sync_get(routes.contentsearch, handler, params)

#     def toc(self, raw=False):
#         params = {"ark": self.ark}
#         return sync_get(routes.toc, Toc.from_xml, params)

#     def textebrut(self):
#         url = routes.textebrut(self.ark)
#         handler = lambda c: BeautifulSoup(c, features="lxml")
#         return sync_get(url, handler)

#     def requestdigitalelement(self, deb: int, e: str = "ALTO"):
#         params = {"O": self.ark.short(), "Deb": deb, "E": e}
#         return sync_get(routes.requestdigitalelement, XmlParser, params)


# class Toc:

#     __wrap_tag = "TEI.2"

#     @classmethod
#     def from_xml(cls, raw_xml):
#         return XmlParser(raw_xml).find(Toc.__wrap_tag)


# class Pagination:
#     @classmethod
#     def from_xml(cls, raw_xml):
#         parser = PaginationParser(raw_xml)
#         return {
#             "structure": parser.structure(),
#             "page_list": list(parser.page_list()),
#         }


# class OAIRecord:
#     __fields = [
#         "visibility_rights",
#         "title",
#         "typedoc",
#         "provenance",
#         "dewey",
#         "sdewey",
#         "nqamoyen",
#         "date",
#         "mode_indexation",
#         "source",
#         "first_indexation_date",
#     ]

#     @classmethod
#     def from_xml(cls, raw_xml):
#         parser = OAIRecordParser(raw_xml)
#         fields_dict = {field: getattr(parser, field)() for field in cls.__fields}
#         record = {
#             "metadata": parser.metadata(),
#             "notice": parser.notice(),
#             "_parser": parser,
#         }
#         return {**fields_dict, **record}


# class ContentSearch:
#     @classmethod
#     def from_xml(cls, raw_xml):
#         parser = ContentSearchParser(raw_xml)
#         return {
#             "metadata": parser.metadata(),
#             "items": list(parser.items()),
#             "query": parser.query(),
#             "_parser": parser,
#         }


# class Issues:
#     @classmethod
#     def from_xml(cls, raw_xml):
#         parser = IssuesParser(raw_xml)
#         return {
#             "metadata": parser.metadata(),
#             "year_list": parser.year_list(),
#             "issue_list": parser.issue_list(),
#             "_parser": parser,
#         }
