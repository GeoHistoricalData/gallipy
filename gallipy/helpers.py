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
from bs4 import BeautifulSoup
from .monadic import Left, Either


_BASE_PARTS = {"scheme":"https", "netloc":"gallica.bnf.fr"}

def fetch(url):
    """Fetches data from an URL

    Fetch data from URL and wraps the unicode encoded response in an Either object.

    Args:
        url (str): An URL to fetch.
        timeout (:obj:int, optional): Sets a timeout delay (Optional).

    Returns:
        Either[Exception Unicode]: The response content if everything went fine
            and Exception otherwise.
    """
    try:
        with urllib.request.urlopen(url, timeout=30) as res:
            content = res.read()
            if content:
                return Either.pure(content)
            raise Exception("Empty response from {}".format(url))
    except Exception as ex:
        pattern = "Error while fetching URL {}\n{}"
        err = urllib.error.URLError(pattern.format(url, str(ex)))
        return Left(err)

def fetch_xml_html(url, parser='xml'):
    """Fetches xml or html from an URL

    Retrieves xml or html data from an URL and wraps it in an Either object.
    The resulting data is a simple utf-8 string.

    Args:
      url (str): An URL to fetch.
      parser (str): Any BeautifulSoup4 parser, e.g. 'html.parser'. Default: xml.

    Returns:
        Either[Exception String]: String if everything went fine, Exception
        otherwise.
    """
    try:
        return fetch(url).map(lambda res: str(BeautifulSoup(res, parser)))
    except urllib.error.URLError as ex:
        pattern = "Error while fetching XML from {}\n{}"
        err = urllib.error.URLError(pattern.format(url, str(ex)))
        return Left(err)

def fetch_json(url):
    """Fetches json from an URL

    Retrieves json data from an URL and wraps it in an Either object.

    Args:
        url (str): An URL to fetch.

    Returns:
        Either[Exception Unicode]: Unicode if everything went fine and
            Exception otherwise.
    """
    try:
        return fetch(url).map(json.loads)
    except urllib.error.URLError as ex:
        pattern = "Error while fetching JSON from {}\n{}"
        err = urllib.error.URLError(pattern.format(url, str(ex)))
        return Left(err)

def build_service_url(parts=None, service_name=''):
    """Creates an URL to access Gallica services

    Given a dictionary of urllib URL parts and a service name,
    builds a complete URL to reach and query this Web service on Gallica.

    Args:
        parts (dict): URL parts used to build the URL.
            See the doc of urllib.parse
        service_name (str): name of the service to query.
            service_name will be ignored if parts has a key named 'path'.

    Returns:
        str: A string representation of the URL built.
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
        parts (dict): URL parts used to build the URL. See the doc of urllib.parse
        ark (str): ARK ID of the document. Parameter ark must be unset if parts['path']
            already contains the ARK ID of the document.

    Returns:
        str: The URL to reach the document identified by ark, as a string.
    """
    this_parts = {"path": str(ark)}
    all_parts = _BASE_PARTS.copy()
    all_parts.update(this_parts)
    all_parts.update(parts)
    return build_url(all_parts)

def build_url(parts, quote_via=urllib.parse.quote_plus):
    """Creates a URL from a dictionary of parts.

    Creates a URL from a dictionary of urllib parts. See the documentation
    of urllib.parses.

    Args:
        parts (dict): The parts of the URL to build.
        quote_via (function): A function to encode spaces and special characters.
            Defaults to quote_plus. See the documentations of
            urllib.parse.urlencode.

    Returns:
        str: The URL as a string.
    """
    all_parts = parts.copy()
    query = parts.get("query")
    if query:
        all_parts["query"] = urllib.parse.urlencode(query, quote_via=quote_via)
    elements = ["scheme", "netloc", "path", "params", "query", "fragment"]
    sorted_parts = [all_parts.get(key) for key in elements]
    return urllib.parse.urlunparse(sorted_parts)
