from functools import partial
import ark
import requests
from bs4 import BeautifulSoup
from PIL import Image as PILImg
from io import BytesIO
import pandas as pd
from helpers import ok_or_raise
from requests_cache import CachedSession

GALLICA = "https://gallica.bnf.fr"


session = CachedSession("gallicache")
session.hooks["response"].append(ok_or_raise)

class Livre:
    def _format_children(self, e):
        return {
            child.name: child.text for child in e.find_all(recursive=False)
        }

    def __init__(self, soup, ark) -> None:
        self.ark = ark

        structure = soup.find("structure")
        self.structure = pd.Series(self._format_children(structure))

        pages = soup.find_all("page")
        self.pages = pd.DataFrame(self._format_children(p) for p in pages)


class Issues:
    def _format_issue(self, issue):
        attributes = issue.attrs
        attributes.update(
            {
                "ark": Ark(self.ark, name=attributes["ark"]),
                "fulldate": issue.text,
            }
        )
        return attributes

    def __init__(self, soup, ark) -> None:
        self.ark = ark

        md_element = soup.find("issues")
        self.metadata = md_element.attrs if md_element else None

        issues = soup.find_all("issue")
        self.issues = pd.DataFrame(self._format_issue(iss) for iss in issues)

        years = soup.find_all("year")
        self.years = pd.Series(int(y.text) for y in years)


class Ark(ark.Ark):
    def issues(self, date=None, raw=False):
        qark = Ark(self, qualifier="date").arkid()
        content = get_xml(services.issues, ark=qark, date=date)
        return content if raw else Issues(content, self)

    def oairecord(self, raw=True):
        return get_xml(services.oairecord, ark=self.short())

    def pagination(self, raw=False):
        content = get_xml(services.pagination, ark=self.short())
        return content if raw else Livre(content, self)

    def image(self, page=1, resolution="thumbnail"):
        response = session.get(
            services.image(self.arkid(), page, resolution),
            headers={"accept": "image/jpeg"},
        )
        return PILImg.open(BytesIO(response.content))

    def content_search(self, query, page=None, start_result=1, raw=True):
        content = get_xml(
            services.content_search,
            ark=self.short(),
            query=query,
            page=page,
            startResult=start_result,
        )
        return content if raw else content

    def toc(self):
        return get_xml(services.toc, ark=self.arkid())

    #TODO Stopped here
    def texte_brut(self):
        return requests.get(
            services.textebrut(self), headers={"accept": "text/html"}
        )

    def request_digital_element(self):
        return get_xml(
            services.request_digital_element, params={"ark": self.arkid()},
        )


class Services:
    def _url(verb: str):
        return f"{GALLICA}/services/{verb}"

    toc = _url("Toc")
    issues = _url("Issues")
    oairecord = _url("OAIRecord")
    pagination = _url("Pagination")
    content_search = _url("ContentSearch")
    request_digital_element = _url("RequestDigitalElement")

    def image(self, ark, page, qualifier):
        return f"{GALLICA}/{ark}/f{page}.{qualifier}"

    texte_brut = lambda _, ark: f"{GALLICA}/{ark}.texteBrut"


def XmlParser(raw_xml):
    return BeautifulSoup(raw_xml, "xml")


def get_xml(url, **params):
    response = session.get(
        url,
        params=params,
        headers={"accept": "application/xml"},
    )
    return XmlParser(response.content)


services = Services()
