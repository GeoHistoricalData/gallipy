from bs4 import BeautifulSoup, NavigableString
from .ark import Ark
import cchardet
import datetime


class OAIRecordParser:
    def __init__(self, xml_string):
        self._parsed = XmlParser(xml_string)
        print(self._parsed)

    def metadata(self):
        md = extract_attributes(self._parsed.find("results"))
        md["ResultsGenerationSearchTime"] = str2timedelta(
            md["ResultsGenerationSearchTime"]
        )
        return md

    def _get(self, elem):
        val = self._parsed.find(elem)
        return val.text if val else None

    def visibility_rights(self):
        return self._get("visibility_rights")

    def notice(self):
        return self._parsed.find("notice")

    def provenance(self):
        return self._get("provenance")

    def sdewey(self):
        return int(self._get("sdewey"))

    def dewey(self):
        return int(self._get("dewey"))

    def source(self):
        return self._get("source")

    def typedoc(self):
        return self._get("typedoc")

    def nqamoyen(self):
        return float(self._get("nqamoyen"))

    def mode_indexation(self):
        return self._get("mode_indexation")

    def title(self):
        return self._get("title")

    def date(self):
        return [int(date.text) for date in self._parsed.find_all("date")]

    def first_indexation_date(self):
        val = self._get("first_indexation_date")
        return datetime.datetime.strptime(val, "%d/%m/%Y")


class IssuesParser:
    def __init__(self, xml_string):
        self._parsed = XmlParser(xml_string)

    def metadata(self):
        md = extract_attributes(self._parsed.find("issues"))
        md["compile_time"] = str2timedelta(md["compile_time"])
        md["parentArk"] = Ark.parse(md["parentArk"])
        return md

    def year_list(self):
        return [int(year.text) for year in self._parsed.find_all("year")]

    def issue_list(self):
        issues = []
        for issue in self._parsed.find_all("issue"):
            md = extract_attributes(issue)
            md["ark"] = Ark.parse(md["ark"])
            issue = {
                "metadata": md,
                "text": issue.text,
            }
            issues.append(issue)
        return issues


class PaginationParser:

    __structure_elements = [
        "firstDisplayedPage",
        "hasToc",
        "TocLocation",
        "hasContent",
        "idUPN",
        "nbVueImages",
    ]
    __page_elements = [
        "numero",
        "ordre",
        "pagination_type",
        "image_width",
        "image_height",
    ]

    def __init__(self, xml_string):
        self._parsed = BeautifulSoup(xml_string, "xml")

    def structure(self):
        s = self._parsed.find("structure")
        cast_fb = [int, bool, str]
        d = {
            k: cast_or(s.find(k).text, *cast_fb)
            for k in PaginationParser.__structure_elements
        }
        return d

    def page_list(self):
        cast_fb = [int, bool, str]
        for p in self._parsed.find_all("page"):
            page = {
                k: cast_or(p.find(k).text, *cast_fb)
                for k in PaginationParser.__page_elements
            }
            yield page


class ContentSearchParser:

    _highlight_sep = "(...)"

    def __init__(self, xml_string):
        self._parsed = BeautifulSoup(xml_string, "xml")

    def metadata(self):
        md = extract_attributes(self._parsed.find("results"))
        md["ResultsGenerationSearchTime"] = str2timedelta(
            md["ResultsGenerationSearchTime"]
        )
        return md

    def query(self):
        return self._parsed.find("query").text

    def items(self):
        items = self._parsed.find_all("item")

        for item in items:
            page = item.find("p_id")
            page_width = item.find("p_width")
            page_height = item.find("p_height")
            altoid = item.find("altoid")
            content = item.find("content")

            data = {}
            if page and page.text:
                data["page"] = p_id2int(page.text)

            if page_height and page_height.text:
                data["page_height"] = int(page_height.text)

            if page_width and page_width.text:
                data["page_width"] = int(page_width.text)

            if content and content.text:
                highlight = BeautifulSoup(content.text, features="lxml")
                c_parsed = html2text(highlight)
                data["text"] = c_parsed.split(self._highlight_sep)

            if altoid and altoid.text:
                data["altoid"] = self._altoid(altoid)

            yield data

    def _altoid(self, altoid_tree):
        altoid = extract_attributes(altoid_tree)
        strings = []
        for altoidstring in altoid_tree.find_all("altoidstring"):
            dic = extract_attributes(altoidstring)
            strings.append({altoidstring.text: dic})
        altoid["altoidstring"] = strings
        return altoid

    def events(self):
        """ Not yet implemented """
        ...


##
# Helpers
##


def cast_or(val, *types):
    last_exc = None
    for t in types:
        try:
            return t(val)
        except (TypeError, ValueError) as e:
            last_exc = e
    raise last_exc


def p_id2int(p_id):
    """ Extracts pages numbers from p_id elements, e.g. "512" from "PAG_512 """
    return int(p_id[4:])


def html2text(bs_html):
    """ Gets the text contained in an HTML document """
    text = [
        node if isinstance(node, NavigableString) else node.get_text()
        for node in bs_html
    ]
    return "".join(text)


def extract_attributes(xml_element):
    return {key: cast_or(value, int, str) for key, value in xml_element.attrs.items()}


def str2timedelta(time_str):
    t = datetime.datetime.strptime(time_str, "%H:%M:%S.%f")
    return datetime.timedelta(
        hours=t.hour, minutes=t.minute, seconds=t.second, microseconds=t.microsecond
    )
