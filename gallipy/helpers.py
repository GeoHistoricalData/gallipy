import urllib.parse
import json
import xmltodict as xmltoordereddict
from bs4 import BeautifulSoup
from .monadic import Left, Either

_BASE_PARTS = {"scheme":"https","netloc":"gallica.bnf.fr"}

def fetch(url):
  try:
    with urllib.request.urlopen(url, timeout = 30) as r:
      return Either.pure(r.read()) # Maybe returning the stream would be a better idea
  except Exception as e:
      err = Exception("Error while fetching URL {}\n{}".format(url,str(e)))
      return Left(err)

def fetch_xml(url):
  try:
    eithersoup = fetch(url).map(lambda xml: BeautifulSoup(xml, 'xml'))
    return eithersoup.map(lambda soup : str(soup))
  except Exception as e:
      err = Exception("Error while fetching XML document from {}\n{}".format(url,str(e)))
      return Left(err)

def fetch_json(url):
  try:
    jsonu = fetch(url).map(lambda data: json.loads(data))
    return jsonu
  except Exception as e:
      err = Exception("Error while fetching JSON data from {}\n{}".format(url,str(e)))
      return Left(err)

def build_service_url(parts={},service_name=''):
  this_parts = {"path": "services/"+service_name}
  all_parts = {**_BASE_PARTS, **this_parts, **parts} 
  return build_url(all_parts)

def build_base_url(parts={}, ark=None):
  this_parts = {"path": str(ark)}
  all_parts = {**_BASE_PARTS, **this_parts, **parts} 
  return build_url(all_parts)

def build_url(parts):
  all_parts = parts.copy()
  query = parts.get("query")
  if query and not isinstance(query, str):
    all_parts["query"] = urllib.parse.urlencode(query)
  elements = ["scheme", "netloc", "path", "params", "query", "fragment"]
  sorted_parts = [all_parts.get(key) for key in elements]
  return urllib.parse.urlunparse(sorted_parts)

def jsontodict(js):
  return dict(js)

def xmltodict(xml):
  return dict(xmltoordereddict.parse(xml))