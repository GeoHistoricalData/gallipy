from . import ark
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO


GALLICA = "https://gallica.bnf.fr"


class Ark(ark.Ark):
    def issues(self, date=None):
        ark_ = self
        if self.qualifier != "date":
            ark_ = Ark(self, qualifier="date")
        return xml_request(services.issues, params={"ark": ark_.arkid(), "date": date},)

    def oairecord(self):
        return xml_request(services.oairecord, params={"ark": self.short()},)

    def pagination(self):
        return xml_request(services.pagination, params={"ark": self.short()},)

    def image(self):
        return requests.get(
            services.image,
            params={"ark": self.arkid()},
            hooks=lambda c: Image.open(BytesIO(c)),
            headers={"accept": "image/jpeg"},
        )

    def content_search(self):
        return xml_request(services.content_search, params={"ark": self.short()},)

    def toc(self):
        return xml_request(services.toc, params={"ark": self.arkid()},)

    def texte_brut(self):
        return requests.get(services.textebrut(self), headers={"accept": "text/html"})

    def request_digital_element(self):
        return xml_request(
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

    image = lambda _, ark, page, qualifier: f"{GALLICA}/{ark}/f{page}.{qualifier}"
    texte_brut = lambda _, ark: f"{GALLICA}/{ark}.texteBrut"

    _hook_xmlparse = {"response": lambda r, **_: XmlParser(r.content)}


def XmlParser(raw_xml):
    return BeautifulSoup(raw_xml, "xml")


def xml_request(url, params=None):
    return requests.get(
        url,
        params=params,
        headers={"accept": "application/xml"},
        hooks=services._hook_xmlparse,
    )


services = Services()
