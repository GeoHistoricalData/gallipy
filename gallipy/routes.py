from functools import partial

GALLICA: str = "https://gallica.bnf.fr"
IIIF_ENPOINT: str = GALLICA + "/iiif"


def gallica_route_to(*path_parts: str):
    items = [GALLICA] + list(path_parts)
    return "/".join(str(i) for i in items)


gallica_route_to_services = partial(gallica_route_to, "services")
