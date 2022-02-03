from dataclasses import dataclass
from .ark import Ark

GALLICA = "https://gallica.bnf.fr"

##
# Document API
##


def service(verb: str) -> str:
    return f"{GALLICA}/services/{verb}"


issues = service("Issues")

oairecord = service("OAIRecord")

pagination = service("Pagination")

contentsearch = service("ContentSearch")

toc = service("Toc")

requestdigitalelement = f"{GALLICA}/RequestDigitalElement"


def image(ark: Ark, page: int, resolution: str) -> str:
    return f"{GALLICA}/{ark}/f{page}.{resolution}"


def textebrut(ark: Ark) -> str:
    return f"{GALLICA}/{ark}.texteBrut"


##
# IIIF API
##

iiif = f"{GALLICA}/iiif"


def image_requests(
    ark: Ark, vue: int, region: str, size: str, rotation: int, quality: str, format: str
) -> str:
    return f"{iiif}/{ark}/{vue}/{region}/{size}/{rotation}/{quality}.{format}"


def image_information(ark: Ark, vue: int) -> str:
    return f"{iiif}/{ark}/{vue}/info.json"


def presentation(ark: Ark) -> str:
    return f"{iiif}/{ark}/manifest.json"


##
# Search API
##

sru = f"{GALLICA}/SRU"

categories = service("Categories")
