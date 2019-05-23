"""
Gallipy - Python wrapper for the Gallica APIs
Copyright (C) 2019  Bertrand Dumenieu

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

https://github.com/GeoHistoricalData/gallipy
"""
import urllib.parse
import json
import xmltodict as xmltoordereddict
from bs4 import BeautifulSoup
from .monadic import Left, Either


_BASE_PARTS = {"scheme":"https", "netloc":"gallica.bnf.fr"}

def fetch(url):
    """Fetches binary data from an URL

    Retrieves binary data from an URL and wraps it in an Either object.

    Args:
      url: An URL to fetch.
      timeout: Sets a timeout delay (Optional).

    Returns:
      An Either[Binary] if everything went fine and an Either[Exception]
      otherwise.
    """
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            return Either.pure(response.read()) # Maybe returning the stream would be a better idea
    except urllib.error.URLError as ex:
        msgpattern = "Error while fetching URL {}\n{}"
        err = urllib.error.URLError(msgpattern.format(url, str(ex)))
        return Left(err)

def fetch_xml(url):
    """Fetches xml from an URL

    Retrieves xml data from an URL and wraps it in an Either object.
    The xml data is a simple string.

    Args:
      url: An URL to fetch.
      timeout: Sets a timeout delay (Optional).

    Returns:
      An Either[String] if everything went fine and an Either[Exception]
      otherwise.
    """
    try:
        eithersoup = fetch(url).map(lambda xml: BeautifulSoup(xml, 'xml'))
        return eithersoup.map(str)
    except urllib.error.URLError as ex:
        msgpattern = "Error while fetching XML from URL {}\n{}"
        err = urllib.error.URLError(msgpattern.format(url, str(ex)))
        return Left(err)

def fetch_json(url):
    """Fetches json from an URL

    Retrieves json data from an URL and wraps it in an Either object.

    Args:
      url: An URL to fetch.
      timeout: Sets a timeout delay (Optional).

    Returns:
      An Either[Unicode] if everything went fine and an Either[Exception]
      otherwise.
    """
    try:
        jsonu = fetch(url).map(json.loads)
        return jsonu
    except urllib.error.URLError as ex:
        msgpattern = "Error while fetching JSON from URL {}\n{}"
        err = urllib.error.URLError(msgpattern.format(url, str(ex)))
        return Left(err)

def build_service_url(parts=None, service_name=''):
    """Creates an URL to access Gallica services

    Given a dictionary of urllib URL parts and a service name,
    builds a complete URL to reach and query this Web service on Gallica.

    Args:
      parts: URL parts used to build the URL. See the doc of urllib.parse
      service_name: name of the service to query. service_name will be ignored
                    if parts has a key named 'path'.

    Returns:
      A string representation of the URL built.
    """
    this_parts = {"path": "services/"+service_name}
    all_parts = _BASE_PARTS.copy()
    all_parts.update(this_parts)
    all_parts.update(parts)
    return build_url(all_parts)

def build_base_url(parts=None, ark=None):
    """Creates the URL of a Gallica document from its ARK ID.

    Given an ARK ID and a dictionary of URL parts, builds a complete URL
    to reach the document identified by this ARK ID on Gallica .

    Args:
      parts: URL parts used to build the URL. See the doc of urllib.parse
      ark: ARK ID of the document. Parameter ark must be unset if parts['path']
      already contains the ARK ID of the document.

    Returns:
      The URL to reach the document identified by ark, as a string.
    """
    this_parts = {"path": str(ark)}
    all_parts = _BASE_PARTS.copy()
    all_parts.update(this_parts)
    all_parts.update(parts)
    return build_url(all_parts)

def build_url(parts):
    """Creates a URL from a dictionary of parts.

    Creates a URL from a dictionary of urllib parts. See the documentation
    of urllib.parses.

    Args:
      parts: The parts of the URL to build.

    Returns:
      The URL as a string.
    """
    all_parts = parts.copy()
    query = parts.get("query")
    if query and not isinstance(query, str):
        all_parts["query"] = urllib.parse.urlencode(query)
    elements = ["scheme", "netloc", "path", "params", "query", "fragment"]
    sorted_parts = [all_parts.get(key) for key in elements]
    return urllib.parse.urlunparse(sorted_parts)

def jsontodict(json_data):
    """Transforms a json object into a dict .

    Args:
      json_data: A JSON object.

    Returns:
      A dictionary representation of json_data.
    """
    return dict(json_data)

def xmltodict(xml):
    """Transforms a xml document string into a dict.

    Args:
      xml: A valid XML string.

    Returns:
      A dictionary representation of the xml document
    """
    return dict(xmltoordereddict.parse(xml))
