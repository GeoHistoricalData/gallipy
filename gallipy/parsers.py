from bs4 import BeautifulSoup
from ark import Ark
import cchardet
import datetime

##
# Parsing helpers
##

def cast_or(val, type_, fallback):
    try:
        return type_(val)
    except (TypeError, ValueError):
        return fallback(val)

def p_id2int(p_id):
    """ Extracts pages numbers from p_id elements, e.g. "512" from "PAG_512 """
    return int(p_id[4:])

def html2text(bs_html):
    """ Gets the text contained in an HTML document """
    text = [node if isinstance(node, bs4.NavigableString) else node.get_text() for node in bs_html]
    return "".join(text)

def extract_attributes(xml_element):
    return {key: cast_or(value, int, str) for key, value in xml_element.attrs.items()}

def str2timedelta(time_str):
    t = datetime.datetime.strptime(time_str, "%H:%M:%S.%f")
    return datetime.timedelta(hours=t.hour, minutes=t.minute, seconds=t.second, microseconds=t.microsecond)

def XmlParser(xml_string):
    return BeautifulSoup(xml_string, features="lxml")

class IssuesParser:
    def __init__(self, xml_string):
        self._parsed = BeautifulSoup(xml_string, "xml")
    
    def metadata(self):
        md = extract_attributes(self._parsed.find("issues"))
        md["compile_time"] = str2timedelta(md["compile_time"])
        md["parentArk"] = Ark.from_string(md["parentArk"])
        return md

    def years(self):
        return [int(year.text) for year in self._parsed.find_all("year")]

    def issues(self):
        from gallica import Issue  # FIXME circular import
        issues = []
        for issue in self._parsed.find_all("issue"):
            md = extract_attributes(issue)
            value = issue.text
            ark = Ark.from_string(md.pop("ark"))
            issues.append(Issue(ark ,md, value))
        return issues
        


class ContentSearchParser:
    
    _highlight_sep = "(...)"
    
    def __init__(self, xml_string):
        self._parsed = BeautifulSoup(xml_string, "xml")

    def metadata(self):
        md =  self.extract_attributes(self._parsed.find("results"))
        md["ResultsGenerationSearchTime"] = str2timedelta(md["ResultsGenerationSearchTime"])
        return md

    def query(self):
        return self._parsed.find("query").text

    def items(self):
        items = self._parsed.find_all("item")
        
        for item in items:
            data = {}

            page = item.find("p_id")
            page_width = item.find("p_width")
            page_height = item.find("p_height")
            altoid = item.find("altoid")
            content = item.find("content")
            
            if page and page.text:
                data["page"] = p_id2int(page.text)
            
            if page_height and page_height.text:
                data["page_height"] = int(page_height.text)
            
            if page_width and page_width.text:
                data["page_width"] = int(page_width.text)
            
            if content and content.text:
                highlight = BeautifulSoup(content.text, features="lxml")
                c_parsed = self.html2text(highlight)
                data["content"] = c_parsed.split(self._highlight_sep)
            
            if altoid and altoid.text:
                data["altoid"] = self._altoid(altoid)

            yield data

    def _altoid(self, altoid_tree):
        altoid = self.extract_attributes(altoid_tree)
        strings = []
        for altoidstring in altoid_tree.find_all("altoidstring"):
            dic = self.extract_attributes(altoidstring)
            strings.append({altoidstring.text: dic})
        altoid["altoidstring"] = strings
        return altoid

    def content(self):
        highlighted = BeautifulSoup(item.find("content").text)
        items[page] = html2text(highlighted).split(self._highlight_sep)

    def events(self):
        """ Not yet implemented """
        ...

